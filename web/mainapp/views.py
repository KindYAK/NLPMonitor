from django.views.generic import TemplateView
from .forms import DocumentSearchForm, DashboardFilterForm
from .services_es_documents import execute_search
from .services_es_dashboard import get_publications_dashboard


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
            "datetime": document['source']['datetime'],
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
        if form.cleaned_data['tags']:
            context['publications_by_tag'] = self.parse_es_response(get_publications_dashboard(search_request))
        context['publications_overall'] = self.parse_es_response(get_publications_dashboard({}))
        context['form'] = form
        return context
