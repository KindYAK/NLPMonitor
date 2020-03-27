import datetime

from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT_EVAL


def es_document_eval_search_factory(widget, **kwargs):
    s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{widget.topic_modelling_name}_{widget.criterion.id}")\
        .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)})\
        .filter("range", document_datetime={"lte": datetime.datetime.now().date()})
    return s
