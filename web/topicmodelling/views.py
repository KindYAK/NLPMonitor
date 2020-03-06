import datetime
import json
import operator
import re
from collections import defaultdict

import numpy as np
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.views.generic import TemplateView
from elasticsearch_dsl import Search

from evaluation.models import EvalCriterion
from mainapp.forms import TopicChooseForm, get_topic_weight_threshold_options, DynamicTMForm
from mainapp.services import apply_fir_filter, unique_ize
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_META_DTM, \
    ES_INDEX_DYNAMIC_TOPIC_MODELLING, ES_INDEX_MAPPINGS, ES_INDEX_DYNAMIC_TOPIC_DOCUMENT
from topicmodelling.services import normalize_topic_documnets, get_documents_with_weights, get_current_topics_metrics, \
    get_total_metrics


class TopicsListView(TemplateView):
    template_name = "topicmodelling/topics_list.html"
    form_class = TopicChooseForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser or hasattr(self.request.user, "expert"):
            context['criterions'] = EvalCriterion.objects.all()
        form = self.form_class(data=self.request.GET,
                               is_superuser=self.request.user.is_superuser or hasattr(self.request.user, "expert"))
        context['form'] = form
        if form.is_valid():
            context['topic_modelling'] = form.cleaned_data['topic_modelling']
            context['topic_weight_threshold'] = form.cleaned_data['topic_weight_threshold']
        else:
            context['topic_modelling'] = form.fields['topic_modelling'].choices[0][0]
            context['topic_weight_threshold'] = 0.05  # Initial

        key = make_template_fragment_key('topics_list', [self.request.GET])
        if cache.get(key):
            return context

        # Get topics aggregation
        s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{context['topic_modelling']}") \
            .filter("range", topic_weight={"gte": context['topic_weight_threshold']}) \
            .filter("range", datetime={"gte": datetime.date(2000, 1, 1)}) \
            .filter("range", datetime={"lte": datetime.datetime.now().date()})
        s.aggs.bucket(name='topics', agg_type="terms", field='topic_id', size=10000) \
            .metric("topic_weight", agg_type="sum", field="topic_weight")
        result = s.execute()
        topic_info_dict = dict(
            (bucket.key, {
                "count": bucket.doc_count,
                "weight_sum": bucket.topic_weight.value
            }) for bucket in result.aggregations.topics.buckets
        )

        # Get actual topics
        topics = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING) \
            .filter("term", **{"name": context['topic_modelling']}) \
            .filter("term", **{"is_ready": True}).execute()[0]['topics']
        # Fill topic objects with meta data
        for topic in topics:
            if topic.id in topic_info_dict:
                topic.size = topic_info_dict[topic.id]['count']
                topic.weight = topic_info_dict[topic.id]['weight_sum']
            else:
                topic.size, topic.weight = 0, 0
            if not topic.topic_words:
                continue
            max_word_weight = max((word.weight for word in topic.topic_words))
            for topic_word in topic.topic_words:
                topic_word.weight /= max_word_weight
                topic_word.word = topic_word.word[0].upper() + topic_word.word[1:]  # Stub - upper case
            # Stub - topic name upper case
            topic.name = ", ".join([w[0].upper() + w[1:] for w in topic.name.split(", ")])

        # Normalize topic weights by max
        max_topic_weight = max((topic.weight for topic in topics))
        if max_topic_weight != 0:
            for topic in topics:
                topic.weight /= max_topic_weight

        # Create context
        context['topics'] = sorted([t for t in topics if len(t.topic_words) >= 5],
                                   key=lambda x: x.weight, reverse=True)
        context['rest_weight'] = sum([t.weight for t in topics[10:]])
        return context


class TopicDocumentListView(TemplateView):
    template_name = "topicmodelling/topic_document_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'topic_name' in kwargs:
            topics = [kwargs['topic_name']]
        else:
            topics = json.loads(self.request.GET['topics'])
            is_too_many_groups = len(topics) > 50

        # Forms Management
        context['granularity'] = self.request.GET['granularity'] if 'granularity' in self.request.GET else "1w"
        context['smooth'] = True if 'smooth' in self.request.GET else (
            True if 'granularity' not in self.request.GET else False)
        context['topic_weight_threshold_options'] = get_topic_weight_threshold_options(
            self.request.user.is_superuser or hasattr(self.request.user, "expert"))
        context['topic_weight_threshold'] = float(self.request.GET['topic_weight_threshold']) \
            if 'topic_weight_threshold' in self.request.GET else \
            0.05  # Initial

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
                                                                          context['topic_weight_threshold']
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


class DynamicTMView(TemplateView):
    template_name = "topicmodelling/dynamictm.html"
    dynamictm_form = DynamicTMForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_dtm'] = {s.meta_name: s.to_dict() for s in Search(using=ES_CLIENT, index=ES_INDEX_META_DTM).
                                                                     source(
            ['meta_name', 'from_date', 'to_date', 'tm_volume_days', 'delta_days'])[:10000].execute()}

        form = self.dynamictm_form(data=self.request.GET, meta_dtms=context['meta_dtm'])

        dynamic_tm = Search(using=ES_CLIENT, index=ES_INDEX_DYNAMIC_TOPIC_MODELLING).filter('term', **{
            'meta_dtm_name.keyword': list(context['meta_dtm'].keys())[-1]}).sort('datetime_from')[:1000].execute()

        choice = [(s.name[-21:], s.name[-21:]) for s in dynamic_tm]
        topic_num = dynamic_tm[0].number_of_topics
        form.fields['dtm_from'].choices = choice
        form.fields['dtm_to'].choices = choice[::-1]

        if form.is_valid():
            data = form.cleaned_data
            threshold = data['thresholds']
            topic_modelling_first_from = data['dtm_from'].split('_')[-2]
            topic_modelling_second_to = data['dtm_to'].split('_')[-1]
            meta_dtm = data['meta_dtm']

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

                for i, mapping in enumerate(mappings_list):
                    for key, value in json.loads(mapping.mappings_dict).items():
                        for val in value:
                            source.append(topic_val_idx[f'tm_{i}-{key}'])
                            target.append(topic_val_idx[f'tm_{i+1}-{val}'])

                values = []  # TODO fix this, with Kirills agg logic
                for i, tm in enumerate(dynamic_tm, start=0):
                    s = Search(using=ES_CLIENT, index=f'{ES_INDEX_DYNAMIC_TOPIC_DOCUMENT}_{tm.name}')
                    s.aggs.bucket(name="topic", agg_type="terms", field="topic_id", size=topic_num).metric(
                        "topic_weight", agg_type="sum", field="topic_weight")
                    r = s.execute()
                    values_dict = {}
                    for bucket in r.aggregations.topic.buckets:
                        if bucket.key in list(labels_dict[f'tm_{i}']):
                            values_dict[bucket.key] = bucket.topic_weight.value
                    sorted_values = [j for i, j in sorted(values_dict.items(), key=operator.itemgetter(0))]
                    values.extend(sorted_values)
                step = 1 / len(mappings_list)  # 0.5

                x = [int(key.split('_')[1]) * step + 0.01 if not int(key.split('_')[1]) else int(
                    key.split('_')[1]) * step for
                     key, label in labels_dict.items() for _ in label]

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
            else:
                print('!!! no such mappings')

        else:
            print("!! not valid")

        context['form'] = form

        return context
