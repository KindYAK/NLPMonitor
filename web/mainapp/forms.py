import django.forms as forms
from mainapp.models import *


class DocumentSearchForm(forms.Form):
    id = forms.CharField(label="ID", required=False)
    corpuses = forms.ModelMultipleChoiceField(queryset=Corpus.objects.all(), label="Корпусы", required=False)
    sources = forms.ModelMultipleChoiceField(queryset=Source.objects.all(), label="Источники", required=False)
    authors = forms.ModelMultipleChoiceField(queryset=Author.objects.all(), label="Авторы", required=False)
    title = forms.CharField(label="Заголовок", required=False)
    text = forms.CharField(label="Текст", required=False)

    datetime_from = forms.DateField(label="Дата - Начало периода")
    datetime_to = forms.DateField(label="Дата - Конец периода")

    num_views_from = forms.IntegerField(label="Количество просмотров - больше чем")
    num_views_to = forms.IntegerField(label="Количество просмотров - меньше чем")
    num_shares_from = forms.IntegerField(label="Количество репостов - больше чем")
    num_shares_to = forms.IntegerField(label="Количество репостов - меньше чем")
    num_comments_from = forms.IntegerField(label="Количество комментариев - больше чем")
    num_comments_to = forms.IntegerField(label="Количество комментариев - меньше чем")
    num_likes_from = forms.IntegerField(label="Количество лайков - больше чем")
    num_likes_to = forms.IntegerField(label="Количество лайков - меньше чем")

    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), label="Теги", required=False)
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), label="Категории", required=False)
