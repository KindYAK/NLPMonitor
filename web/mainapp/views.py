from django.views.generic import TemplateView
from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_DOCUMENT
from .dashboard_types import *
from .forms import DocumentSearchForm, DashboardFilterForm, KibanaSearchForm, TopicChooseForm
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
            topic.size = topic_info_dict[topic.id]['count']
            topic.weight = round(topic_info_dict[topic.id]['weight_sum'], 2)
        context['topics'] = sorted([t for t in topics if len(t.topic_words) > 0],
                                   key=lambda x: x.size, reverse=True)
        context['form'] = form
        return context


class TopicDocumentListView(TemplateView):
    template_name = "mainapp/topic_document_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_name = kwargs['topic_name']
        topic_modelling = kwargs['topic_modelling']
        std = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
            .filter("term", topic_modelling=topic_modelling) \
            .filter("term", topic_id=topic_name).sort("-topic_weight") \
            .filter("range", topic_weight={"gte": 0.001}) \
            .source(['document_es_id', 'topic_weight'])[:500]
        std.aggs.bucket(name="dynamics", agg_type="date_histogram", field="datetime", calendar_interval="1w") \
            .metric("dynamics_weight", agg_type="sum", field="topic_weight")
        topic_documents = std.execute()

        sd = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)\
            .filter('terms', _id=[d.document_es_id for d in topic_documents])\
            .source(('id', 'title', 'source', 'datetime',))[:500]
        documents = sd.execute()
        weight_dict = dict((d.document_es_id, d.topic_weight) for d in topic_documents)
        for document in documents:
            document.weight = weight_dict[document.meta.id]
        documents = sorted(documents, key=lambda x: x.weight, reverse=True)

        context['documents'] = documents
        context['topic_dynamics'] = topic_documents.aggregations.dynamics.buckets
        context['topic_name'] = Search(using=ES_CLIENT)
        return context


class SearchView(TemplateView):
    template_name = "mainapp/search.html"
    form_class = DocumentSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.form_class(data=self.request.GET)
        search_request = {}
        if form.is_valid():
            search_request = form.cleaned_data
        results = execute_search(search_request)
        context['documents'] = [{
            "ID": document['source']['id'],
            "datetime": document['source']['datetime'] if 'datetime' in document['source'] else "",
            "title": document['source']['title'],
            "source": document['source']['source'],
            "score": str(document['score']).replace(",", "."),
        } for document in results['hits']]
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
        context = super().get_context_data(**kwargs)
        context['document'] = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
                .filter("term", **{"id": kwargs['document_id']}).execute()[0]
        return context
