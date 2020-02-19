import django.forms as forms
from django.db.models import Count
from django.forms.utils import ErrorList
from elasticsearch_dsl import Search

from mainapp.models import *
from nlpmonitor.settings import MIN_DOCS_PER_AUTHOR, MIN_DOCS_PER_TAG, ES_CLIENT, ES_INDEX_TOPIC_MODELLING, \
    ES_INDEX_META_DTM


def get_topic_weight_threshold_options(is_superuser):
    if is_superuser:
        return [(i, str(i)) for i in
                [0.0001, 0.001] + [j / 100 for j in range(1, 10)] + [0.1, 0.125, 0.15, 0.175, 0.2, 0.25]]
    else:
        return [
            (0.01, "Очень мягкий (0.01)"),
            (0.05, "Мягкий (0.05)"),
            (0.1, "Средний (0.1)"),
            (0.15, "Жёсткий (0.15)"),
            (0.2, "Очень жёсткий (0.2)"),
        ]


class TopicChooseForm(forms.Form):
    topic_modelling = forms.ChoiceField(label="Тематическое моделирование")
    topic_weight_threshold = forms.ChoiceField(label="Порог принадлежности к топику")

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None,
                 renderer=None, is_superuser=False):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
                         use_required_attribute, renderer)

        # Get topic_modellings
        s = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter('term', is_ready=True) \
                .source(['name', 'algorithm', 'number_of_topics', 'number_of_documents',
                         'source', 'datetime_from', 'datetime_to'
                         # 'perplexity', 'purity', 'contrast', 'coherence',
                         # 'tau_smooth_sparse_theta', 'tau_smooth_sparse_phi',
                         # 'tau_decorrelator_phi', 'tau_coherence_phi',
                         ])[:100]
        topic_modellings = s.execute()
        topic_modellings = sorted(topic_modellings, key=lambda x: x.number_of_documents, reverse=True)
        topic_modellings = ((tm.name.lower(),
                             f"{tm.name.replace('bigartm', 'tm')} - {tm.number_of_topics} топиков - {tm.number_of_documents} текстов - " +
                             (f"{tm.source} - " if hasattr(tm, 'source') and tm.source else f"Все СМИ ") +
                             (f"С {tm.datetime_from[:10]} - " if hasattr(tm,
                                                                         'datetime_from') and tm.datetime_from else f"") +
                             (f"По {tm.datetime_to[:10]} - " if hasattr(tm, 'datetime_to') and tm.datetime_to else f"")
                             ) for tm in topic_modellings)
        self.fields['topic_modelling'].choices = topic_modellings

        # Get topic_weight_thresholds
        self.fields['topic_weight_threshold'].choices = get_topic_weight_threshold_options(is_superuser)


class KibanaSearchForm(forms.Form):
    def __init__(self, choices, *args, **kwargs):
        super(KibanaSearchForm, self).__init__(*args, **kwargs)
        self.fields["dashboard"] = forms.ChoiceField(choices=choices)


class DocumentSearchForm(forms.Form):
    id = forms.CharField(label="ID", required=False)
    corpuses = forms.ModelMultipleChoiceField(queryset=Corpus.objects.all(), label="Корпусы", required=False)
    sources = forms.ModelMultipleChoiceField(queryset=Source.objects.all(), label="Источники", required=False)
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.annotate(num_docs=Count('document')).filter(num_docs__gte=MIN_DOCS_PER_AUTHOR),
        label="Авторы", required=False)
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

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.annotate(num_docs=Count('document')).filter(num_docs__gte=MIN_DOCS_PER_TAG), label="Теги",
        required=False)
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), label="Категории", required=False)


class DashboardFilterForm(forms.Form):
    corpus = forms.ModelChoiceField(queryset=Corpus.objects.all(), label="Корпус", required=True,
                                    initial=Corpus.objects.first())
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.annotate(num_docs=Count('document')).filter(num_docs__gte=MIN_DOCS_PER_TAG), label="Теги",
        required=False)

    datetime_from = forms.DateField(label="Дата - Начало периода", input_formats=['%d-%m-%Y'], required=False)
    datetime_to = forms.DateField(label="Дата - Конец периода", input_formats=['%d-%m-%Y'], required=False)


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['source', 'title', 'text', 'url', 'datetime', 'sentiment_loader', ]

    def clean(self):
        try:
            title = self.cleaned_data['title']
            source = self.cleaned_data['source']
            datetime = self.cleaned_data['datetime']
            if Document.objects.filter(title=title, source=source, datetime=datetime).exists():
                raise forms.ValidationError("Такая новость уже существует")
        except KeyError:
            pass
        return super().clean()


class DynamicTMForm(forms.Form):
    meta_dtm = forms.MultipleChoiceField(label="META DTM", required=True)

    dtms = forms.MultipleChoiceField(label="Topic Modellings", required=True)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None,
                 renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted,
                         field_order,
                         use_required_attribute, renderer)
        meta_dtms = Search(using=ES_CLIENT, index=ES_INDEX_META_DTM)[:10000]
        self.fields['meta_dtm'].choices = [
            (m.name, f"{m.name} мета топик моделлинг") for m in meta_dtms.execute()
        ]
