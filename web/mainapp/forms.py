import django.forms as forms
from django.db.models import Count
from django.forms.utils import ErrorList

from nlpmonitor.settings import MIN_DOCS_PER_AUTHOR, MIN_DOCS_PER_TAG, ES_CLIENT, ES_INDEX_TOPIC_MODELLING
from mainapp.models import *

from elasticsearch_dsl import Search, Q


class TopicChooseForm(forms.Form):
    topic_modelling = forms.ChoiceField(label="Тематическое моделирование")

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None,
                 renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
                         use_required_attribute, renderer)
        s = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter('term', is_ready=True) \
                  .source(['name', 'algorithm', 'number_of_topics', 'number_of_documents',
                           'source', 'datetime_from', 'datetime_to'
                           # 'perplexity', 'purity', 'contrast', 'coherence',
                           # 'tau_smooth_sparse_theta', 'tau_smooth_sparse_phi',
                           # 'tau_decorrelator_phi', 'tau_coherence_phi',
                           ])[:100]
        # self.fields['topic_modelling'].choices = [(tm.name, f"{tm.name} - {tm.algorithm} - {tm.number_of_topics} топиков - "
        #                                                     f"PRPLX={round(tm.perplexity, 1) if hasattr(tm, 'perplexity') else 'None'} "
        #                                                     f"SST={round(tm.tau_smooth_sparse_theta, 1) if hasattr(tm, 'perplexity') else 'None'} "
        #                                                     f"SSP={round(tm.tau_smooth_sparse_phi, 1) if hasattr(tm, 'perplexity') else 'None'} "
        #                                                     f"DEC={round(tm.tau_decorrelator_phi, 1) if hasattr(tm, 'perplexity') else 'None'} "
        #                                                     f"COH={round(tm.tau_coherence_phi, 1) if hasattr(tm, 'perplexity') else 'None'} "
        #                                            ) for tm in s.scan()]
        self.fields['topic_modelling'].choices = [(tm.name, f"{tm.name} - {tm.number_of_topics} топиков - {tm.number_of_documents} текстов - " +
                                                            (f"{tm.source} - " if hasattr(tm, 'source') and tm.source else f"Все СМИ") +
                                                            (f"С {tm.datetime_from[:10]} - " if hasattr(tm, 'datetime_from') and tm.datetime_from else f"") +
                                                            (f"По {tm.datetime_to[:10]} - " if hasattr(tm, 'datetime_to') and tm.datetime_to else f"")
                                                   ) for tm in s.scan()]


class KibanaSearchForm(forms.Form):
    def __init__(self, choices, *args, **kwargs):
        super(KibanaSearchForm, self).__init__(*args, **kwargs)
        self.fields["dashboard"] = forms.ChoiceField(choices=choices)


class DocumentSearchForm(forms.Form):
    id = forms.CharField(label="ID", required=False)
    corpuses = forms.ModelMultipleChoiceField(queryset=Corpus.objects.all(), label="Корпусы", required=False)
    sources = forms.ModelMultipleChoiceField(queryset=Source.objects.all(), label="Источники", required=False)
    authors = forms.ModelMultipleChoiceField(queryset=Author.objects.annotate(num_docs=Count('document')).filter(num_docs__gte=MIN_DOCS_PER_AUTHOR), label="Авторы", required=False)
    title = forms.CharField(label="Заголовок", required=False)
    text = forms.CharField(label="Текст", required=False)

    datetime_from = forms.DateField(label="Дата - Начало периода", input_formats=['%d-%m-%Y'], required=False)
    datetime_to = forms.DateField(label="Дата - Конец периода", input_formats=['%d-%m-%Y'], required=False)

    num_views_from = forms.IntegerField(label="Количество просмотров - больше чем", required=False)
    num_views_to = forms.IntegerField(label="Количество просмотров - меньше чем", required=False)
    num_shares_from = forms.IntegerField(label="Количество репостов - больше чем", required=False)
    num_shares_to = forms.IntegerField(label="Количество репостов - меньше чем", required=False)
    num_comments_from = forms.IntegerField(label="Количество комментариев - больше чем", required=False)
    num_comments_to = forms.IntegerField(label="Количество комментариев - меньше чем", required=False)
    num_likes_from = forms.IntegerField(label="Количество лайков - больше чем", required=False)
    num_likes_to = forms.IntegerField(label="Количество лайков - меньше чем", required=False)

    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.annotate(num_docs=Count('document')).filter(num_docs__gte=MIN_DOCS_PER_TAG), label="Теги", required=False)
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), label="Категории", required=False)


class DashboardFilterForm(forms.Form):
    corpus = forms.ModelChoiceField(queryset=Corpus.objects.all(), label="Корпус", required=True, initial=Corpus.objects.first())
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.annotate(num_docs=Count('document')).filter(num_docs__gte=MIN_DOCS_PER_TAG), label="Теги", required=False)

    datetime_from = forms.DateField(label="Дата - Начало периода", input_formats=['%d-%m-%Y'], required=False)
    datetime_to = forms.DateField(label="Дата - Конец периода", input_formats=['%d-%m-%Y'], required=False)
