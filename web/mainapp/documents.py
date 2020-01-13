import json

import elasticsearch_dsl as es
from django.utils import timezone
from elasticsearch_dsl import Index, MetaField

from mainapp.models import Document as ModelDocument
from nlpmonitor.settings import ES_INDEX_DOCUMENT, ES_INDEX_DASHOBARD, ES_INDEX_EMBEDDING, ES_INDEX_CLASSIFIER, \
    ES_INDEX_TOPIC_MODELLING, ES_INDEX_DICTIONARY_INDEX, ES_INDEX_DICTIONARY_WORD, ES_CLIENT, ES_INDEX_TOPIC_DOCUMENT, \
    ES_INDEX_CUSTOM_DICTIONARY_WORD, ES_INDEX_DOCUMENT_EVAL, ES_INDEX_DOCUMENT_EVAL_UNIQUE_IDS, ES_INDEX_TOPIC_DOCUMENT_UNIQUE_IDS

DYNAMIC_TEMPLATES = [{
    "not_indexed_double": {
    "match_mapping_type": "double",
    "mapping": {
        "type": "float",
        "index": False
    }
}}]


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
    
    class Meta:
        dynamic_templates = MetaField(DYNAMIC_TEMPLATES)


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


class TopicWord(es.InnerDoc):
    word = es.Keyword()
    weight = es.Float()


class Topic(es.InnerDoc):
    id = es.Keyword()
    name = es.Keyword()
    topic_words = es.Nested(TopicWord)
    topic_size = es.Integer()
    topic_weight = es.Float()


class TopicDocument(es.Document):
    topic_id = es.Keyword()
    topic_weight = es.Float()
    document_es_id = es.Keyword()
    datetime = es.Date()
    document_source = es.Keyword()

    class Index:
        name = ES_INDEX_TOPIC_DOCUMENT # f"{ES_INDEX_TOPIC_DOCUMENT}_{tm}"
        using = ES_CLIENT

        settings = {
            "number_of_shards": 3,
            "number_of_replicas": 1,
            "max_result_window": 5000000,
        }
        mappings = {
            "properties": {
                "datetime": {
                    "type": "date"
                },
                "document_es_id": {
                    "type": "keyword",
                },
                "document_source": {
                    "type": "keyword",
                },
                "topic_id": {
                    "type": "keyword",
                },
                "topic_weight": {
                    "type": "float"
                }
            }
        }


class TopicDocumentUniqueIDs(es.Document):
    document_es_id = es.Keyword()

    class Index:
        name = ES_INDEX_TOPIC_DOCUMENT_UNIQUE_IDS # f"{ES_INDEX_TOPIC_DOCUMENT_UNIQUE_IDS}_{tm}"
        using = ES_CLIENT

        settings = {
            "number_of_shards": 3,
            "number_of_replicas": 1,
        }
        mappings = {
            "properties": {
                "document_es_id": {
                    "type": "keyword",
                },
            }
        }


class DocumentEval(es.Document):
    value = es.Float()
    document_es_id = es.Keyword()
    document_datetime = es.Date()
    document_source = es.Keyword()
    topic_ids_top = es.Keyword()
    topic_ids_bottom = es.Keyword()

    class Index:
        name = ES_INDEX_DOCUMENT_EVAL # !!! f"{ES_INDEX_DOCUMENT_EVAL}_{tm}_{criterion.id}"
        using = ES_CLIENT

        settings = {
            "number_of_shards": 3,
            "number_of_replicas": 1,
            "max_result_window": 5000000,
        }
        mappings = {
            "properties": {
                "document_datetime": {
                    "type": "date"
                },
                "document_es_id": {
                    "type": "keyword"
                },
                "document_source": {
                    "type": "keyword"
                },
                "value": {
                    "type": "float"
                },
                "topic_ids_top": {
                    "type": "keyword"
                },
                "topic_ids_bottom": {
                    "type": "keyword"
                },
            }
        }


class DocumentEvalUniqueIDs(es.Document):
    document_es_id = es.Keyword()

    class Index:
        name = ES_INDEX_DOCUMENT_EVAL_UNIQUE_IDS # f"{ES_INDEX_DOCUMENT_EVAL_UNIQUE_IDS}_{tm}"
        using = ES_CLIENT

        settings = {
            "number_of_shards": 3,
            "number_of_replicas": 1,
        }
        mappings = {
            "properties": {
                "document_es_id": {
                    "type": "keyword",
                },
            }
        }


# List of all TMs in the storage
class TopicModellingIndex(es.Document):
    corpus = es.Keyword()
    source = es.Keyword()
    number_of_documents = es.Integer()
    is_ready = es.Boolean()
    has_topic_info = es.Boolean()
    name = es.Keyword()
    description = es.Text()
    datetime_created = es.Date()
    datetime_finished = es.Date()

    datetime_from = es.Date()
    datetime_to = es.Date()

    algorithm = es.Keyword()
    number_of_topics = es.Integer()
    hierarchical = es.Boolean()
    meta_parameters = es.Object()

    perplexity = es.Float()
    purity = es.Float()
    contrast = es.Float()
    coherence = es.Float()

    tau_smooth_sparse_theta = es.Float()
    tau_smooth_sparse_phi = es.Float()
    tau_decorrelator_phi = es.Float()
    tau_coherence_phi = es.Float()

    topics = es.Nested(Topic)

    is_actualizable = es.Boolean()

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


class DictionaryWord(es.Document):
    dictionary = es.Keyword()
    word = es.Keyword()
    word_normal = es.Keyword()

    is_in_pymorphy2_dict = es.Boolean()
    is_multiple_normals_in_pymorphy2 = es.Boolean()
    is_stop_word = es.Boolean()
    is_latin = es.Boolean()
    is_kazakh = es.Boolean()
    pos_tag = es.Keyword()
    word_len = es.Integer()

    word_frequency = es.Integer()
    word_normal_frequency = es.Integer()
    document_frequency = es.Integer()
    document_normal_frequency = es.Integer()

    word_frequency_relative = es.Float()
    word_normal_frequency_relative = es.Float()
    document_frequency_relative = es.Float()
    document_normal_frequency_relative = es.Float()

    word_first_capital_ratio = es.Float()
    word_normal_first_capital_ratio = es.Float()

    class Index:
        name = ES_INDEX_DICTIONARY_WORD
        using = ES_CLIENT


class Dictionary(es.Document):
    corpus = es.Keyword()
    name = es.Keyword()
    description = es.Text()
    datetime = es.Date()
    number_of_documents = es.Integer()

    is_ready = es.Boolean()

    class Index:
        name = ES_INDEX_DICTIONARY_INDEX
        using = ES_CLIENT


class CustomDictionaryWord(es.Document):
    word = es.Keyword()
    word_normal = es.Keyword()

    class Index:
        name = ES_INDEX_CUSTOM_DICTIONARY_WORD
        using = ES_CLIENT
