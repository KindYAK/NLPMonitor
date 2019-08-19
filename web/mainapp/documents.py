import json

import elasticsearch_dsl as es
from elasticsearch_dsl import Index

from nlpmonitor.settings import ES_INDEX_DOCUMENTS, ES_INDEX_DASHOBARD, ES_CLIENT
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
            try:
                self.links = json.loads(model_obj.links)
            except json.JSONDecodeError:
                self.links = model_obj.links
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
        name = ES_INDEX_DOCUMENTS
        using = ES_CLIENT


class DashboardValue(es.InnerDoc):
    value = es.Integer()
    datetime = es.Date()


dashboard_index = Index(ES_INDEX_DASHOBARD, ES_CLIENT)
dashboard_index.settings(
    **{"index.mapping.nested_objects.limit": 50000}
)


@dashboard_index.document
class Dashboard(es.Document):
    corpus = es.Keyword()
    type = es.Keyword()
    granularity = es.Keyword() # 1d / 1h
    datetime_started = es.Date()
    datetime_generated = es.Date()
    is_ready = es.Boolean()

    tag = es.Keyword()

    values = es.Nested(DashboardValue)

    def add_value(self, value, datetime):
        self.values.append(DashboardValue(value=value, datetime=datetime))


# List of all Embeddings in the storage
class EmbeddingIndex(es.Document):
    corpus = es.Keyword()
    name = es.Keyword()
    description = es.Text()
    datetime_created = es.Date()
    datetime_finished = es.Date()

    by_unit = es.Keyword() # Token/Word/Sentence/Text
    algorithm = es.Keyword()
    pooling = es.Keyword()
    meta_parameters = es.Object()


# List of all TMs in the storage
class TopicModellingIndex(es.Document):
    name = es.Keyword()
    description = es.Text()
    datetime_created = es.Date()
    datetime_finished = es.Date()

    algorithm = es.Keyword()
    number_of_topics = es.Integer()
    hierarchical = es.Boolean()
    meta_parameters = es.Object()


# List of all TMs in the storage
class ClassifierIndex(es.Document):
    name = es.Keyword()
    description = es.Text()
    datetime_created = es.Date()
    datetime_finished = es.Date()

    algorithm = es.Keyword()
    target = es.Keyword()
    quality = es.Object() # Different quality metrics - F1, ROC, etc.
    meta_parameters = es.Object()
