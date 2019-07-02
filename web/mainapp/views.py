from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin
from .forms import DocumentSearchForm
from .services_es import execute_search


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
