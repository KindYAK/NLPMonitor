import json
import re

import numpy as np

from django.views.generic import TemplateView

from dashboard.models import MonitoringObject, Widget
from dashboard.services import es_widget_search_factory
from evaluation.models import EvalCriterion
from mainapp.forms import TopicChooseForm, DynamicTMForm
from mainapp.services import apply_fir_filter, unique_ize, get_user_group
from nlpmonitor.settings import ES_INDEX_META_DTM, \
    ES_INDEX_DYNAMIC_TOPIC_MODELLING, ES_INDEX_MAPPINGS, ES_INDEX_DYNAMIC_TOPIC_DOCUMENT, ES_INDEX_TOPIC_COMBOS
from topicmodelling.services import *


class TopicsListView(TemplateView):
    template_name = "topicmodelling/topics_list.html"
    form_class = TopicChooseForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser or hasattr(self.request.user, "expert"):
            context['criterions'] = EvalCriterion.objects.all()
            if not self.request.user.is_superuser:
                group = get_user_group(self.request.user)
                context['criterions'] = context['criterions'].filter(usergroup=group)
        form = self.form_class(data=self.request.GET, user=self.request.user)
        if not form.fields['topic_modelling'].choices:
            context['error'] = "403 FORBIDDEN"
            return context
        context['form'] = form
        if form.is_valid():
            context['topic_modelling'] = form.cleaned_data['topic_modelling']
            context['topic_weight_threshold'] = form.cleaned_data['topic_weight_threshold']
        else:
            context['topic_modelling'] = form.fields['topic_modelling'].choices[0][0]
            context['topic_weight_threshold'] = 0.05  # Initial

        key = make_template_fragment_key('topics_list', [context['topic_modelling'], context['topic_weight_threshold']])
        if cache.get(key):
            return context

        tm_index = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING) \
                .filter("term", name=context['topic_modelling']).execute()[0]
        is_multi_corpus = False
        if hasattr(tm_index, "is_multi_corpus"):
            is_multi_corpus = tm_index.is_multi_corpus
        topics = get_topics_with_meta(context['topic_modelling'],
                                      context['topic_weight_threshold'],
                                      is_multi_corpus)

        # Create context
        context['is_multi_corpus'] = is_multi_corpus
        context['has_resonance_score'] = any((hasattr(topic, "high_resonance_score") and topic.high_resonance_score for topic in topics))
        if is_multi_corpus:
            corpuses = set()
            for topic in topics:
                if not hasattr(topic, "corpus_weights"):
                    continue
                for corpus in topic.corpus_weights:
                    corpuses.add(corpus)
            context['corpuses'] = list(corpuses)
        context['topics'] = sorted([t for t in topics if len(t.topic_words) >= 5],
                                   key=lambda x: x.weight, reverse=True)
        context['rest_weight'] = sum([t.weight for t in topics[10:]])
        return context


class TopicDocumentListView(TemplateView):
    template_name = "topicmodelling/abstract_document_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_superuser:
            group = get_user_group(self.request.user)
            if not group or kwargs['topic_modelling'] not in group.topic_modelling_names.split(","):
                context['error'] = "403 FORBIDDEN"
                return context

        if 'topic_name' in kwargs:
            topics = [kwargs['topic_name']]
        else:
            topics = json.loads(self.request.GET['topics'])
            is_too_many_groups = len(topics) > 50

        # Forms Management
        try:
            context = abstract_documents_list_form_management(context, self.request, kwargs)
        except CacheHit:
            return context

        key = make_template_fragment_key('topic_detail', [kwargs, self.request.GET])
        if cache.get(key):
            return context

        # Total metrics
        total_metrics_dict = get_total_metrics(kwargs['topic_modelling'], context['granularity'],
                                               context['topic_weight_threshold'])

        # Current topic metrics
        topic_documents, number_of_documents = get_current_topics_metrics(kwargs['topic_modelling'],
                                                                          topics,
                                                                          context['granularity'],
                                                                          context['topic_weight_threshold'],
                                                                          intersection=self.request.GET.get("intersection", "") == "1"
                                                                          )

        # Get documents, set weights
        documents = get_documents_with_weights(topic_documents)

        # Normalize
        normalize_topic_documnets(topic_documents, total_metrics_dict)

        # Separate signals
        absolute_power = [bucket.doc_count for bucket in topic_documents.aggregations.dynamics.buckets]
        relative_power = [bucket.doc_count_normal for bucket in topic_documents.aggregations.dynamics.buckets]
        relative_weight = [bucket.dynamics_weight.value for bucket in topic_documents.aggregations.dynamics.buckets]

        # Smooth
        if context['smooth']:
            absolute_power = apply_fir_filter(absolute_power, granularity=context['granularity'])
            relative_power = apply_fir_filter(relative_power, granularity=context['granularity'])
            relative_weight = apply_fir_filter(relative_weight, granularity=context['granularity'])

        # Create context
        context['list_type'] = "topics"
        context['documents'] = unique_ize(documents, key=lambda x: x.id)
        context['number_of_documents'] = number_of_documents
        context['date_ticks'] = [bucket.key_as_string for bucket in topic_documents.aggregations.dynamics.buckets]
        context['absolute_power'] = absolute_power
        context['relative_power'] = relative_power
        context['relative_weight'] = relative_weight
        context['source_weight'] = sorted(topic_documents.aggregations.source.buckets,
                                          key=lambda x: x.source_weight.value,
                                          reverse=True)
        return context


class MonitoringObjectDocumentListView(TemplateView):
    template_name = "topicmodelling/abstract_document_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_superuser:
            group = get_user_group(self.request.user)
            if not group or kwargs['topic_modelling'] not in group.topic_modelling_names.split(","):
                context['error'] = "403 FORBIDDEN"
                return context

        widget = Widget.objects.get(id=kwargs['widget_id'])
        monitoring_object = MonitoringObject.objects.get(id=kwargs['object_id'])

        # Forms Management
        try:
            context = abstract_documents_list_form_management(context, self.request, kwargs)
        except CacheHit:
            return context

        s = es_widget_search_factory(widget, object_id=monitoring_object.id)
        s.aggs.bucket("dynamics", agg_type="date_histogram", field="datetime", calendar_interval=context['granularity'])
        s.aggs.bucket("source", agg_type="terms", field="document_source")
        number_of_documents = s.count()
        s = s.source(("document_es_id", "datetime"))[:1000 * 300]
        r = s.execute()

        documents = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter("terms", _id=list(set([d.document_es_id for d in r])))
        documents = documents.source(("id", "title", "datetime", "source", "url"))[:2000]
        documents = documents.execute()

        # Separate signals
        absolute_power = [bucket.doc_count for bucket in r.aggregations.dynamics.buckets]

        # Smooth
        if context['smooth']:
            absolute_power = apply_fir_filter(absolute_power, granularity=context['granularity'])

        # Create context
        context['list_type'] = "monitoring_object"
        context['monitoring_object'] = monitoring_object
        context['widget'] = widget
        context['documents'] = unique_ize(documents, key=lambda x: x.id)
        context['number_of_documents'] = number_of_documents
        context['date_ticks'] = [bucket.key_as_string for bucket in r.aggregations.dynamics.buckets]
        context['absolute_power'] = absolute_power
        context['source_weight'] = sorted(r.aggregations.source.buckets,
                                          key=lambda x: x.doc_count,
                                          reverse=True)
        return context


class DynamicTMView(TemplateView):
    template_name = "topicmodelling/dynamictm.html"
    dynamictm_form = DynamicTMForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_dtm'] = {s.meta_name: s.to_dict() for s in Search(using=ES_CLIENT, index=ES_INDEX_META_DTM).
                                                                     source(
            ['meta_name', 'from_date', 'to_date', 'tm_volume_days', 'delta_days'])[:10000].execute()}

        form = self.dynamictm_form(data=self.request.GET, meta_dtms=context['meta_dtm'])
        context['form'] = form
        dynamic_tm = Search(using=ES_CLIENT, index=ES_INDEX_DYNAMIC_TOPIC_MODELLING).filter('term', **{
            'meta_dtm_name.keyword': list(context['meta_dtm'].keys())[-1]}).sort('datetime_from')[:1000].execute()

        choice = [(s.name[-21:], s.name[-21:]) for s in dynamic_tm]
        topic_num = dynamic_tm[0].number_of_topics
        form.fields['dtm_from'].choices = choice
        form.fields['dtm_to'].choices = choice[::-1]
        if form.is_valid():
            if form.cleaned_data['meta_dtm']:
                data = form.cleaned_data
                threshold = data['thresholds']
                topic_modelling_first_from = data['dtm_from'].split('_')[-2]
                topic_modelling_second_to = data['dtm_to'].split('_')[-1]
                meta_dtm = data['meta_dtm']
            else:
                meta_dtm = form.fields['meta_dtm'].choices[0][0]
                threshold = form.fields['thresholds'].choices[0][0]
                topic_modelling_second_to = "2019-04-01"
                topic_modelling_first_from = "2019-01-01"
        else:
            return context

        dynamic_tm = Search(using=ES_CLIENT, index=ES_INDEX_DYNAMIC_TOPIC_MODELLING).filter('term', **{
            'meta_dtm_name.keyword': meta_dtm}).sort('datetime_from')[:1000].execute()
        mappings_list = Search(using=ES_CLIENT, index=ES_INDEX_MAPPINGS) \
            .filter('range', topic_modelling_first_from={'gte': topic_modelling_first_from}) \
            .filter('range', topic_modelling_second_to={'lte': topic_modelling_second_to}) \
            .filter('term', **{'meta_dtm_name.keyword': meta_dtm}) \
            .filter('term', **{'threshold.keyword': threshold}) \
            .sort("topic_modelling_first_from") \
            .source(['mappings_dict', 'threshold', 'topic_modelling_first_from', 'topic_modelling_second_to']) \
            .execute()
        if mappings_list:
            draw_list, labels_list, source, target, y = list(), list(), list(), list(), list()
            topic_val_idx = dict()
            labels_dict = defaultdict(list)

            for i, mappings in enumerate(mappings_list):
                for key in json.loads(mappings.mappings_dict).keys():
                    labels_list.append(f'tm_{i}-{key}')

                for value in json.loads(mappings.mappings_dict).values():
                    for val in value:
                        labels_list.append(f'tm_{i+1}-{val}')

            matcher = re.compile(r'\-?\d{0,10}\.?\d{1,10}')
            labels_list = sorted(list(set(labels_list)))
            for label in labels_list:
                tm_idx, topic_idx = list(map(int, re.findall(matcher, label)))
                labels_dict[f'tm_{tm_idx}'] += [f'topic_{topic_idx}']
                draw_list.append('*'.join([w.word for w in dynamic_tm[tm_idx].topics[topic_idx].topic_words[:3]]))

            default_keys = list(map(str, range(len(mappings_list) + 1)))

            class_count_dict = defaultdict(int, {k: 0 for k in default_keys})

            for i, val in enumerate(labels_list):
                class_count_dict[val.split('-')[0].split('_')[1]] += 1
                topic_val_idx[val] = i

            source_dict = defaultdict(list)
            for i, mapping in enumerate(mappings_list):
                for key, value in json.loads(mapping.mappings_dict).items():
                    for val in value:
                        source.append(topic_val_idx[f'tm_{i}-{key}'])
                        source_dict[f'tm_{i}'] += [key]
                        target.append(topic_val_idx[f'tm_{i+1}-{val}'])
            values = []
            for i, tm in enumerate(dynamic_tm[::-1], start=0):
                s = Search(using=ES_CLIENT, index=f'{ES_INDEX_DYNAMIC_TOPIC_DOCUMENT}_{tm.name}')
                s.aggs.bucket(name="topic", agg_type="terms", field="topic_id", size=topic_num).metric(
                    "topic_weight", agg_type="sum", field="topic_weight")
                r = s[0].execute()
                st_values_dict = {}
                for bucket in r.aggregations.topic.buckets:
                    if bucket.key in source_dict[f'tm_{i}']:
                        st_values_dict[bucket.key] = bucket.topic_weight.value
                values_to_extend = [st_values_dict[val] for val in source_dict[f'tm_{i}']]
                values.extend(values_to_extend)

            step = 1 / len(dynamic_tm)  # 0.5

            x = [int(key.split('_')[1]) * step + 0.01 if not int(key.split('_')[1]) else int(
                key.split('_')[1]) * step for key, label in labels_dict.items() for _ in label]

            for val in class_count_dict.values():
                y.extend(np.linspace(0.01, 0.99, val))
            context['sankey_params'] = {
                'label': draw_list,
                'x': x,
                'y': y,
                'source': source,
                'target': target,
                'value': values
            }

        return context


class TopicsComboListView(TemplateView):
    template_name = "topicmodelling/topics_combo_list.html"
    form_class = TopicChooseForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.form_class(data=self.request.GET, user=self.request.user, has_combo=True)
        if not form.fields['topic_modelling'].choices:
            context['error'] = "403 FORBIDDEN"
            return context
        context['form'] = form
        if form.is_valid():
            context['topic_modelling'] = form.cleaned_data['topic_modelling']
        else:
            context['topic_modelling'] = form.fields['topic_modelling'].choices[0][0]

        key = make_template_fragment_key('topics_combo_list', [context['topic_modelling']])
        if cache.get(key):
            return context

        s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_COMBOS}_{context['topic_modelling']}") \
                .source(('topics', 'common_docs_len'))[:10000]
        topic_combos = s.execute()

        # Create context
        context['topic_combos'] = sorted([t for t in topic_combos], key=lambda x: x.common_docs_len, reverse=True)
        return context
