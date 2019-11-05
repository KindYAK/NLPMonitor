import numpy as np
import json

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.views.generic import TemplateView
from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_DOCUMENT
from .dashboard_types import *
from .forms import DocumentSearchForm, DashboardFilterForm, KibanaSearchForm, TopicChooseForm
from .services import apply_fir_filter
from .services_es_dashboard import get_dashboard, get_kibana_dashboards
from .services_es_documents import execute_search


class KibanaDashboardView(TemplateView):
    template_name = "mainapp/kibana_dashboard.html"
    form_class = KibanaSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dashbords = get_kibana_dashboards()
        form = self.form_class(dashbords, data=self.request.GET)
        if form.is_valid():
            selected = form.cleaned_data
            context['selected_dashboard'] = selected['dashboard']

        context['form'] = form
        return context


class TopicsListView(TemplateView):
    template_name = "mainapp/topics_list.html"
    form_class = TopicChooseForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = make_template_fragment_key('topic_groups_list', [self.request.GET])
        if cache.get(key):
            return context
        form = self.form_class(data=self.request.GET)
        if form.is_valid():
            context['topic_modelling'] = form.cleaned_data['topic_modelling']
        else:
            context['topic_modelling'] = form.fields['topic_modelling'].choices[0][0]

        s = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
            .filter("term", topic_modelling=context['topic_modelling']) \
            .filter("range", topic_weight={"gte": 0.001})
        s.aggs.bucket(name='topics', agg_type="terms", field='topic_id.keyword', size=10000)\
            .metric("topic_weight", agg_type="sum", field="topic_weight")
        result = s.execute()
        topic_info_dict = dict(
            (bucket.key, {
                "count": bucket.doc_count,
                "weight_sum": bucket.topic_weight.value
            }) for bucket in result.aggregations.topics.buckets
        )

        topics = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING) \
            .filter("term", **{"name": context['topic_modelling']}) \
            .filter("term", **{"is_ready": True}).execute()[0]['topics']
        for topic in topics:
            if topic.id in topic_info_dict:
                topic.size = topic_info_dict[topic.id]['count']
                topic.weight = round(topic_info_dict[topic.id]['weight_sum'], 2)
            else:
                topic.size, topic.weight = 0, 0
            if not topic.topic_words:
                continue
            max_weight = max((word.weight for word in topic.topic_words))
            for topic_word in topic.topic_words:
                topic_word.weight /= max_weight
        context['topics'] = sorted([t for t in topics if len(t.topic_words) > 0],
                                   key=lambda x: x.weight, reverse=True)
        context['rest_weight'] = sum([t.weight for t in topics[10:]])
        context['form'] = form
        return context


class TopicDocumentListView(TemplateView):
    template_name = "mainapp/topic_document_list.html"

    def get_total_metrics(self, granularity):
        std_total = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
            .filter("term", topic_modelling=self.topic_modelling) \
            .filter("range", topic_weight={"gte": 0.001})
        std_total.aggs.bucket(name="dynamics",
                              agg_type="date_histogram",
                              field="datetime",
                              calendar_interval=granularity) \
                      .metric("dynamics_weight", agg_type="sum", field="topic_weight")
        topic_documents_total = std_total.execute()
        total_metrics_dict = dict(
            (
                t.key_as_string,
                {
                    "size": t.doc_count,
                    "weight": t.dynamics_weight.value
                }
            ) for t in topic_documents_total.aggregations.dynamics.buckets
        )
        return total_metrics_dict

    def get_current_topics_metrics(self, topics, granularity):
        std = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
                  .filter("term", topic_modelling=self.topic_modelling) \
                  .filter("term", topic_id=topics).sort("-topic_weight") \
                  .filter("range", topic_weight={"gte": 0.001}) \
                  .source(['document_es_id', 'topic_weight'])[:100]
        std.aggs.bucket(name="dynamics",
                        agg_type="date_histogram",
                        field="datetime",
                        calendar_interval=granularity) \
            .metric("dynamics_weight", agg_type="sum", field="topic_weight")
        std.aggs.bucket(name="source", agg_type="terms", field="document_source.keyword") \
            .metric("source_weight", agg_type="sum", field="topic_weight")
        topic_documents = std.execute()
        return topic_documents

    def get_documents_with_weights(self, topic_documents):
        sd = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
                 .filter('terms', _id=[d.document_es_id for d in topic_documents]) \
                 .source(('id', 'title', 'source', 'datetime',))[:100]
        documents = sd.execute()
        weight_dict = dict((d.document_es_id, d.topic_weight) for d in topic_documents)
        for document in documents:
            document.weight = weight_dict[document.meta.id]
        documents = sorted(documents, key=lambda x: x.weight, reverse=True)
        return documents

    def normalize_topic_documnets(self, topic_documents, total_metrics_dict):
        for bucket in topic_documents.aggregations.dynamics.buckets:
            total_weight = total_metrics_dict[bucket.key_as_string]['weight']
            total_size = total_metrics_dict[bucket.key_as_string]['size']
            if total_weight != 0:
                bucket.dynamics_weight.value /= total_weight
            if total_size != 0:
                bucket.doc_count_normal = bucket.doc_count / total_size
            else:
                bucket.doc_count_normal = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = make_template_fragment_key('topic_detail', [kwargs, self.request.GET])
        if cache.get(key):
            return context
        self.topic_modelling = kwargs['topic_modelling']

        if 'topic_name' in kwargs:
            topic_name = kwargs['topic_name']
            is_group = False
        else:
            topics = json.loads(self.request.GET['topics'])
            is_too_many_groups = len(topics) > 50
            is_group = True

        # Forms Management
        context['granularity'] = self.request.GET['granularity'] if 'granularity' in self.request.GET else "1w"
        context['smooth'] = True if 'smooth' in self.request.GET else (True if 'granularity' not in self.request.GET else False)

        # Total metrics
        total_metrics_dict = self.get_total_metrics(context['granularity'])

        # Current topic metrics
        topic_documents = self.get_current_topics_metrics(topic_name, context['granularity'])

        # Get documents, set weights
        documents = self.get_documents_with_weights(topic_documents)

        # Normalize
        self.normalize_topic_documnets(topic_documents, total_metrics_dict)

        # Separate signals
        absolute_power = [bucket.doc_count for bucket in topic_documents.aggregations.dynamics.buckets]
        relative_power = [bucket.doc_count_normal for bucket in topic_documents.aggregations.dynamics.buckets]
        relative_weight = [bucket.dynamics_weight.value for bucket in topic_documents.aggregations.dynamics.buckets]

        # Smooth
        if context['smooth']:
            absolute_power = apply_fir_filter(np.array(absolute_power), granularity=context['granularity'])
            relative_power = apply_fir_filter(relative_power, granularity=context['granularity'])
            relative_weight = apply_fir_filter(relative_weight, granularity=context['granularity'])

        # Create context
        context['documents'] = documents
        context['date_ticks'] = [bucket.key_as_string for bucket in topic_documents.aggregations.dynamics.buckets]
        context['absolute_power'] = absolute_power
        context['relative_power'] = relative_power
        context['relative_weight'] = relative_weight
        context['source_weight'] = topic_documents.aggregations.source.buckets
        return context


class SearchView(TemplateView):
    template_name = "mainapp/search.html"
    form_class = DocumentSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = make_template_fragment_key('search_page', [self.request.GET])
        if cache.get(key):
            return context
        form = self.form_class(data=self.request.GET)
        search_request = {}
        if form.is_valid():
            search_request = form.cleaned_data

        # Form Management
        context['granularity'] = self.request.GET['granularity'] if 'granularity' in self.request.GET else "1w"
        context['smooth'] = True if 'smooth' in self.request.GET else (True if 'granularity' not in self.request.GET else False)

        # Total metrics
        sd_total = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
        sd_total.aggs.bucket(name="dynamics",
                             agg_type="date_histogram",
                             field="datetime",
                             calendar_interval=context['granularity'])
        documents_total = sd_total.execute()
        total_metrics_dict = dict(
            (
                t.key_as_string,
                {
                    "size": t.doc_count
                }
            ) for t in documents_total.aggregations.dynamics.buckets
        )

        # Search
        s = execute_search(search_request, return_search_obj=True)[:100]
        s.aggs.bucket(name="dynamics",
                      agg_type="date_histogram",
                      field="datetime",
                      calendar_interval=context['granularity']) \
            .metric("dynamics_weight", agg_type="sum", script="_score")
        context['total_found'] = s.count()
        results = s.execute()
        context['documents'] = [{
            "id": document.id,
            "datetime": document.datetime if hasattr(document, "datetime") else "",
            "title": document.title,
            "source": document.source,
            "score": str(document.meta.score).replace(",", "."),
        } for document in results]

        # Normalize dynamics
        for bucket in results.aggregations.dynamics.buckets:
            total_size = total_metrics_dict[bucket.key_as_string]['size']
            if total_size != 0:
                bucket.doc_count_normal = bucket.doc_count / total_size
                bucket.dynamics_weight.value /= total_size
            else:
                bucket.doc_count_normal = 0

        # Separate signals
        absolute_power = [bucket.doc_count for bucket in results.aggregations.dynamics.buckets]
        relative_power = [bucket.doc_count_normal for bucket in results.aggregations.dynamics.buckets]
        relative_weight = [bucket.dynamics_weight.value for bucket in results.aggregations.dynamics.buckets]

        # Smooth
        if context['smooth']:
            absolute_power = apply_fir_filter(np.array(absolute_power), granularity=context['granularity'])
            relative_power = apply_fir_filter(relative_power, granularity=context['granularity'])
            relative_weight = apply_fir_filter(relative_weight, granularity=context['granularity'])

        # Create context
        context['date_ticks'] = [bucket.key_as_string for bucket in results.aggregations.dynamics.buckets]
        context['absolute_power'] = absolute_power
        context['relative_power'] = relative_power
        context['relative_weight'] = relative_weight
        context['form'] = form
        return context


class DashboardView(TemplateView):
    template_name = "mainapp/dashboard.html"
    form_class = DashboardFilterForm

    def parse_es_response(self, response):
        return [
            {
                "x": [tick['datetime'] for tick in source['source']['values']],
                "y": [tick['value'] for tick in source['source']['values']],
                "tag": source['source']['tag'] if 'tag' in source['source'] else None
            } for source in response['hits']
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.form_class(data=self.request.GET)
        search_request = {}
        if form.is_valid():
            search_request = form.cleaned_data
        context['plots'] = []
        for dashboard_type in DASHBOARD_TYPES:
            search_params = {"type": dashboard_type['type']}
            if form.cleaned_data['tags'] and dashboard_type['filtering'] == FILTERING_TYPE_BY_TAG:
                search_params = {**search_params, **search_request}
            context['plots'].append({
                "data": self.parse_es_response(get_dashboard(search_params)),
                "name": dashboard_type['name'],
                "id": dashboard_type['type'],
            })
        context['form'] = form
        return context


class DocumentDetailView(TemplateView):
    template_name = "mainapp/document_detail.html"

    def get_context_data(self, **kwargs):
        key = make_template_fragment_key('document_detail', [kwargs])
        context = super().get_context_data(**kwargs)
        if cache.get(key):
            return context
        context['document'] = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
                .filter("term", **{"id": kwargs['document_id']}).execute()[0]
        return context
