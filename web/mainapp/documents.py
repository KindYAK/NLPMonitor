import json

import elasticsearch_dsl as es
import django_elasticsearch_dsl as ded
from elasticsearch_dsl import Index

from nlpmonitor.settings import ES_INDEX_DOCUMENT, ES_INDEX_DASHOBARD, ES_INDEX_EMBEDDING, ES_INDEX_CLASSIFIER, ES_INDEX_TOPIC_MODELLING, \
                                ES_CLIENT
from mainapp.models import (
    Document as ModelDocument, Source, Author, Tag, Category, Topic)
from django.utils import timezone
from django_elasticsearch_dsl.registries import registry


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
        name = ES_INDEX_DOCUMENT
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
    granularity = es.Keyword()  # 1d / 1h
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
    number_of_documents = es.Integer()
    is_ready = es.Boolean()
    name = es.Keyword()
    description = es.Text()
    datetime_created = es.Date()
    datetime_finished = es.Date()

    by_unit = es.Keyword()  # Token/Word/Sentence/Text
    algorithm = es.Keyword()
    pooling = es.Keyword()
    meta_parameters = es.Object()

    class Index:
        name = ES_INDEX_EMBEDDING
        using = ES_CLIENT


# List of all TMs in the storage
class TopicModellingIndex(es.Document):
    corpus = es.Keyword()
    number_of_documents = es.Integer()
    is_ready = es.Boolean()
    name = es.Keyword()
    description = es.Text()
    datetime_created = es.Date()
    datetime_finished = es.Date()

    algorithm = es.Keyword()
    number_of_topics = es.Integer()
    hierarchical = es.Boolean()
    meta_parameters = es.Object()

    class Index:
        name = ES_INDEX_TOPIC_MODELLING
        using = ES_CLIENT


# List of all TMs in the storage
class ClassifierIndex(es.Document):
    corpus = es.Keyword()
    number_of_documents = es.Integer()
    is_ready = es.Boolean()
    name = es.Keyword()
    description = es.Text()
    datetime_created = es.Date()
    datetime_finished = es.Date()

    algorithm = es.Keyword()
    target = es.Keyword()
    quality = es.Object()  # Different quality metrics - F1, ROC, etc.
    meta_parameters = es.Object()

    class Index:
        name = ES_INDEX_CLASSIFIER
        using = ES_CLIENT


# Alternative to Document
@registry.register_document
class DocumentInElastic(ded.Document):
    corpus = ded.fields.TextField(attr='corpus_name')
    source = ded.fields.TextField(attr='source_name')
    author = ded.fields.TextField(attr='author_name')
    tags = ded.fields.ListField(
        ded.fields.TextField(attr='tags_name')
    )
    categories = ded.fields.ListField(
        ded.fields.TextField(attr='categories_name')
    )
    topics = ded.fields.ListField(
        ded.fields.TextField(attr='topics_name')
    )

    class Index:
        name = 'mainapp_document'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = ModelDocument
        fields = [
            'title',
            'text',
            'html',
            'links',
            'url',
            'datetime',
            'datetime_created',
            'num_views',
            'num_shares',
            'num_comments',
            'num_likes',
            'unique_hash',
        ]
        related_models = [Source, Author, Tag, Category, Topic]

        queryset_pagination = 1000
