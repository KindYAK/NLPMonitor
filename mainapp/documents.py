import json

import elasticsearch_dsl as es
from nlpmonitor.settings import ES_INDEX, ES_CLIENT
from mainapp.models import Document as ModelDocument
from django.utils import timezone


class Document(es.Document):
    id = es.Keyword()
    corpus = es.Keyword()
    source = es.Keyword()
    author = es.Keyword()
    title = es.Text(fields={'keyword': es.Keyword()})
    text = es.Text()
    html = es.Text()
    links = es.Keyword()
    url = es.Keyword()

    datetime = es.Date()
    datetime_parsed = es.Date()
    datetime_indexed = es.Date()
    datetime_modified = es.Date()

    num_views = es.Integer()
    num_shares = es.Integer()
    num_comments = es.Integer()
    num_likes = es.Integer()

    tags = es.Keyword()
    categories = es.Keyword()

    def init_from_model(self, model_obj: ModelDocument) -> None:
        self.id = model_obj.id
        self.corpus = model_obj.source.corpus.name
        self.source = model_obj.source.name
        if model_obj.author:
            self.author = model_obj.author.name
        else:
            self.author = None
        self.title = model_obj.title
        self.text = model_obj.text
        self.html = model_obj.html
        if model_obj.links:
            self.links = json.loads(model_obj.links)
        self.url = model_obj.url

        self.datetime = model_obj.datetime
        self.datetime_parsed = model_obj.datetime_created
        self.datetime_indexed = timezone.now()
        self.datetime_modified = timezone.now()

        self.num_views = model_obj.num_views
        self.num_shares = model_obj.num_shares
        self.num_comments = model_obj.num_comments
        self.num_likes = model_obj.num_likes

        self.tags = [tag.name for tag in model_obj.tags.all()]
        self.categories = [category.name for category in model_obj.categories.all()]

    class Index:
        name = ES_INDEX
        using = ES_CLIENT
