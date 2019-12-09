from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DeleteView
from elasticsearch_dsl import Search

from mainapp.models import Document
from mainapp.services_es import get_elscore_cutoff
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT
from .dashboard_types import *
from .forms import DocumentSearchForm, DashboardFilterForm, KibanaSearchForm, DocumentForm
from .services import apply_fir_filter, unique_ize
from .services_es_dashboard import get_dashboard, get_kibana_dashboards
from .services_es_documents import execute_search


def login_redirect(request):
    if request.user.is_superuser or hasattr(request.user, "viewer"):
        return HttpResponseRedirect(reverse_lazy('evaluation:criterion_eval_analysis'))
    if hasattr(request.user, "expert"):
        return HttpResponseRedirect(reverse_lazy('topicmodelling:topics_list'))
    if hasattr(request.user, "contentloader"):
        return HttpResponseRedirect(reverse_lazy('mainapp:document_create'))
    return HttpResponseRedirect(reverse_lazy('mainapp:index'))


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


class SearchView(TemplateView):
    template_name = "mainapp/search.html"
    form_class = DocumentSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.form_class(data=self.request.GET)
        context['form'] = form
        if form.is_valid():
            search_request = form.cleaned_data

        # Form Management
        context['granularity'] = self.request.GET['granularity'] if 'granularity' in self.request.GET else "1w"
        context['smooth'] = True if 'smooth' in self.request.GET else (True if 'granularity' not in self.request.GET else False)

        key = make_template_fragment_key('search_page', [self.request.GET])
        if cache.get(key):
            return context

        search_request = {}
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
        s = execute_search(search_request, return_search_obj=True)[:200]
        s.aggs.bucket(name="dynamics",
                      agg_type="date_histogram",
                      field="datetime",
                      calendar_interval=context['granularity']) \
            .metric("dynamics_weight", agg_type="sum", script="_score")
        results = s.execute()
        if 'text' in search_request and search_request['text']:
            relevant_count = get_elscore_cutoff([d.meta.score for d in results], "SEARCH_LVL_LIGHT")
        else:
            relevant_count = s.count().value
        context['total_found'] = relevant_count
        context['documents'] = [{
            "id": document.id,
            "datetime": document.datetime if hasattr(document, "datetime") else "",
            "title": document.title,
            "source": document.source,
            "score": str(document.meta.score).replace(",", "."),
        } for document in results[:relevant_count*2]]
        context['documents'] = unique_ize(context['documents'], key=lambda x: x['id'])[:min(relevant_count, 100)]

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
            absolute_power = apply_fir_filter(absolute_power, granularity=context['granularity'])
            relative_power = apply_fir_filter(relative_power, granularity=context['granularity'])
            relative_weight = apply_fir_filter(relative_weight, granularity=context['granularity'])

        # Create context
        context['date_ticks'] = [bucket.key_as_string for bucket in results.aggregations.dynamics.buckets]
        context['absolute_power'] = absolute_power
        context['relative_power'] = relative_power
        context['relative_weight'] = relative_weight
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


class DocumentCreateView(CreateView):
    template_name = "mainapp/document_create.html"
    form_class = DocumentForm
    model = Document
    success_url = reverse_lazy('mainapp:document_create_success')

    def form_valid(self, form):
        self.object = form.save()
        self.object.author_loader = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class DocumentListView(ListView):
    template_name = "mainapp/document_list.html"
    model = Document

    def get_queryset(self):
        return self.model.objects.filter(author_loader=self.request.user).order_by('-datetime_created')[:1000]


class DocumentDeleteView(DeleteView):
    model = Document
    success_url = reverse_lazy('mainapp:document_list')
    template_name = "mainapp/document_delete_confirm.html"

    def get_queryset(self):
        return super().get_queryset().filter(author_loader=self.request.user)
