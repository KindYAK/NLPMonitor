import datetime

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DeleteView
from elasticsearch_dsl import Search

from dashboard.models import DashboardPreset
from mainapp.models import Document
from mainapp.services_es import get_elscore_cutoff
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT
from .forms import DocumentSearchForm, DocumentForm
from .services import apply_fir_filter, unique_ize, get_user_group
from .services_es_documents import execute_search, es_filter


def login_redirect(request):
    # if request.user.is_superuser:
    #     return HttpResponseRedirect(reverse_lazy('dashboard:dashboard', kwargs={"dashboard_id": DashboardPreset.objects.first().id}))
    # if hasattr(request.user, "viewer"):
    #     group = get_user_group(request.user)
    #     if not group or not group.dashboard_presets.exists():
    #         return HttpResponseRedirect(reverse_lazy('evaluation:criterion_eval_analysis'))
    #     return HttpResponseRedirect(reverse_lazy('dashboard:dashboard', kwargs={"dashboard_id": group.dashboard_presets.first().id}))
    # if hasattr(request.user, "expert"):
    #     return HttpResponseRedirect(reverse_lazy('topicmodelling:topics_list'))
    if hasattr(request.user, "contentloader"):
        return HttpResponseRedirect(reverse_lazy('mainapp:document_create'))
    return HttpResponseRedirect(reverse_lazy('topicmodelling:topics_list'))
    # return HttpResponseRedirect(reverse_lazy('mainapp:index'))


class SearchView(TemplateView):
    template_name = "mainapp/search.html"
    form_class = DocumentSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.form_class(data=self.request.GET, user=self.request.user)
        context['form'] = form
        if form.is_valid():
            search_request = form.cleaned_data
        elif 'corpuses' in form.errors:
            form.cleaned_data['corpuses'] = form.fields['corpuses'].queryset[:1]
            search_request = form.cleaned_data
        else:
            return context
        # Form Management
        context['granularity'] = self.request.GET['granularity'] if 'granularity' in self.request.GET else "1w"
        context['smooth'] = True if 'smooth' in self.request.GET else (True if 'granularity' not in self.request.GET else False)

        key = make_template_fragment_key('search_page', [self.request.GET])
        if cache.get(key):
            return context

        # Total metrics
        sd_total = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
        sd_total = es_filter(sd_total, "corpuses", search_request['corpuses'])
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
        search_request['datetime_from'] = datetime.date(2000, 1, 1)
        search_request['datetime_to'] = datetime.datetime.now().date()
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
            "document_es_id": document.meta.id,
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


def search_api(request):
    result = {}
    smooth = True if 'smooth' in request.GET else (True if 'granularity' not in request.GET else False)
    granularity = request.GET['granularity'] if 'granularity' in request.GET else "1w"

    # Total metrics
    sd_total = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
    sd_total = es_filter(sd_total, "corpuses", "main")
    sd_total.aggs.bucket(name="dynamics",
                         agg_type="date_histogram",
                         field="datetime",
                         calendar_interval=granularity)
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
    search_request = {}
    search_request['datetime_from'] = datetime.date(2000, 1, 1)
    search_request['datetime_to'] = datetime.datetime.now().date()
    search_request['text'] = request.GET.get('text', '')
    s = execute_search(search_request, return_search_obj=True)[:200]
    s.aggs.bucket(name="dynamics",
                  agg_type="date_histogram",
                  field="datetime",
                  calendar_interval=granularity) \
        .metric("dynamics_weight", agg_type="sum", script="_score")
    results = s.execute()
    if 'text' in search_request and search_request['text']:
        relevant_count = get_elscore_cutoff([d.meta.score for d in results], "SEARCH_LVL_LIGHT")
    else:
        relevant_count = s.count().value
    result['total_found'] = relevant_count
    result['documents'] = [{
        "id": document.id,
        "document_es_id": document.meta.id,
        "datetime": document.datetime if hasattr(document, "datetime") else "",
        "title": document.title,
        "source": document.source,
        "score": str(document.meta.score).replace(",", "."),
    } for document in results[:relevant_count * 2]]
    result['documents'] = unique_ize(result['documents'], key=lambda x: x['id'])[:min(relevant_count, 100)]

    # Normalize dynamics
    for bucket in results.aggregations.dynamics.buckets:
        if bucket.key_as_string not in total_metrics_dict:
            bucket.doc_count_normal = 0
            continue
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

    if smooth:
        absolute_power = apply_fir_filter(absolute_power, granularity=granularity)
        relative_power = apply_fir_filter(relative_power, granularity=granularity)
        relative_weight = apply_fir_filter(relative_weight, granularity=granularity)

    # Create context
    result['date_ticks'] = [bucket.key_as_string for bucket in results.aggregations.dynamics.buckets]
    result['absolute_power'] = list(absolute_power)
    result['relative_power'] = list(relative_power)
    result['relative_weight'] = list(relative_weight)
    return JsonResponse(result)


class DocumentDetailView(TemplateView):
    template_name = "mainapp/document_detail.html"

    def get_context_data(self, **kwargs):
        key = make_template_fragment_key('document_detail', [kwargs])
        context = super().get_context_data(**kwargs)
        if cache.get(key):
            return context
        r = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter("term", **{"id": kwargs['document_id']})[:1].execute()
        # TODO Get user group
        if len(r) > 0:
            context['document'] = r[0]
        else:
            context['error'] = "Документ не найден - возможно он ещё не обработан в хранилище"
            return context
        group = get_user_group(self.request.user)
        if not self.request.user.is_superuser and (not group or not group.corpuses.filter(name=r[0].corpus).exists()):
            context['error'] = "403 FORBIDDEN"
            return context
        context['document'] = r[0]
        return context


class DocumentCreateView(CreateView):
    template_name = "mainapp/document_create.html"
    form_class = DocumentForm
    model = Document
    success_url = reverse_lazy('mainapp:document_create_success')

    def form_valid(self, form):
        if not hasattr(self.request.user, "contentloader"):
            return HttpResponse("403 FORBIDDEN")
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
