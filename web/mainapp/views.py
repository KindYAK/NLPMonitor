from django.views.generic import TemplateView
from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_DOCUMENT
from .dashboard_types import *
from .forms import DocumentSearchForm, DashboardFilterForm, KibanaSearchForm, TopicChooseForm
from .services_es_dashboard import get_dashboard, get_kibana_dashboards
from .services_es_documents import execute_search


class KibanaDashboardView(TemplateView):
    template_name = "mainapp/kibana_dashboard.html"
    form_class = KibanaSearchForm
    kibana_port = 5601

    def host(self):
        return "109.233.109.110" # TODO the method return "web" now - no good
        """localhost:8000 > http://localhost:5601"""
        host = self.request.get_host()
        host_name = host.split(":")[0]
        return f"http://{host_name}:{self.kibana_port}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dashbords = get_kibana_dashboards()
        form = self.form_class(dashbords, data=self.request.GET)
        if form.is_valid():
            selected = form.cleaned_data
            context['selected_dashboard'] = selected['dashboard']

        context['form'] = form
        context['host'] = self.host()
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
        topics = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING) \
                .filter("term", **{"name": context['topic_modelling']}) \
                .filter("term", **{"is_ready": True}).execute()[0]['topics']
        context['topics'] = topics
        context['form'] = form
        return context


class TopicDocumentListView(TemplateView):
    template_name = "mainapp/topic_document_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_name = kwargs['topic_name']
        topic_modelling = kwargs['topic_modelling']
        documents = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
            .filter("term", **{f"topics_{topic_modelling}.topic": topic_name}) \
            .source(['id', 'title', 'source', 'datetime'])[:100].execute()
        context['documents'] = documents
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
