from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin
from .forms import DocumentSearchForm
from elasticsearch_dsl import Search
from nlpmonitor.settings import ES_CLIENT


class SearchView(FormMixin, TemplateView):
    template_name = "mainapp/search.html"
    form_class = DocumentSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        s = Search(using=ES_CLIENT)
        result = s[:1000].execute().to_dict()['hits']['hits']
        context['documents'] = [{
            "ID": document['_source']['id'],
            "datetime": document['_source']['datetime'],
            "title": document['_source']['title'],
            "source": document['_source']['source'],
        } for document in result]
        return context

class DashboardView(TemplateView):
    template_name = "mainapp/dashboard.html"
