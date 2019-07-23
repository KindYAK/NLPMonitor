import django.forms as forms
from django.db.models import Count

from nlpmonitor.settings import MIN_DOCS_PER_AUTHOR, MIN_DOCS_PER_TAG
from mainapp.models import *


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
