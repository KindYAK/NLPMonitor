from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT_EVAL


def es_document_eval_search_factory(dashboard, widget, **kwargs):
    s = Search(using=ES_CLIENT,
               index=f"{ES_INDEX_DOCUMENT_EVAL}_{dashboard.topic_modelling_name}_{widget.criterion.id}"
    )
    return s
