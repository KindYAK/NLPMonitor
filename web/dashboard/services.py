from datetime import datetime, timedelta

from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT_EVAL
from .util import default_parser


def es_document_eval_search_factory(widget, **kwargs):
    s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{widget.topic_modelling_name}_{widget.criterion.id}")
    datetime_from = datetime(2000, 1, 1).date()
    datetime_to = datetime.now().date()

    if widget.datetime_to:
        datetime_to = widget.datetime_to
    if widget.datetime_from:
        datetime_from = widget.datetime_from
    if widget.days_before_now:
        datetime_from = datetime_to - timedelta(days=widget.days_before_now)
        datetime_to = datetime.now().date()

    s = s.filter("range", document_datetime={"gte": datetime_from}) \
        .filter("range", document_datetime={"lte": datetime_to})

    if widget.ner_query:
        s = default_parser(
            widget_ner_query=widget.ner_query,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            parent_search=s
        )
    return s
