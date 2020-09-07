from datetime import datetime, timedelta

from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT_EVAL, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_DOCUMENT_LOCATION
from .util import default_parser


def es_widget_search_factory(widget, object_id=None):
    if widget.criterion and object_id is None:
        s_type = "eval"
        widget.criterion.id_postfix = widget.criterion.id
        s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{widget.topic_modelling_name}_{widget.criterion.id}")
    else:
        s_type = "tm"
        s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{widget.topic_modelling_name}")
    s = es_default_fields_parser(widget, s, s_type, object_id)
    return s


def es_document_location_search_factory(widget, **kwargs):
    s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_LOCATION)
    s = es_default_fields_parser(widget, s)
    params = widget.params_obj
    if 'location_level' not in params:  # TODO fix this shit, now we need this because of default locality maps,
                                        # TODO in future we need to parse all levels(locality, area, district)
        s = s.filter('term', **{'location_level.keyword': 'Населенный пункт'})
    if params:
        for key, value in params.items():
            if not value:
                continue
            if any(key.endswith(range_selector) for range_selector in ['__gte', '__lte', '__gt', '__lt']):
                range_selector = key.split("__")[-1]
                if key == f'criterion__{range_selector}':
                    key = f'criterion_{widget.topic_modelling_name}_{widget.criterion_id}__{range_selector}'
                s = s.filter('range', **{key.replace(f"__{range_selector}", ""): {range_selector: value}})
            else:
                s = s.filter('term', **{key: value})
    return s


def es_default_fields_parser(widget, s, s_type="eval", object_id=None):
    datetime_from = datetime(2000, 1, 1).date()
    datetime_to = datetime.now().date()

    if widget.datetime_to:
        datetime_to = widget.datetime_to
    if widget.datetime_from:
        datetime_from = widget.datetime_from
    if widget.days_before_now:
        datetime_from = datetime_to - timedelta(days=widget.days_before_now)
        datetime_to = datetime.now().date()

    if s_type == "eval":
        datetime_field = "document_datetime"
    else:
        datetime_field = "datetime"
    s = s.filter("range", **{datetime_field: {"gte": datetime_from}}) \
        .filter("range", **{datetime_field: {"lte": datetime_to}})

    try:
        widget_ner_query = widget.monitoring_object.ner_query
    except AttributeError:
        widget_ner_query = None

    if widget_ner_query:
        s = default_parser(
            widget_ner_query=widget_ner_query,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            parent_search=s
        )

    try:
        monitoring_objects = widget.monitoring_objects_group.monitoring_objects.all()
    except AttributeError:
        monitoring_objects = None

    if monitoring_objects:
        ss = list()
        for monitoring_object in monitoring_objects:
            if object_id and monitoring_object.id != object_id:
                continue
            ss.append(
                default_parser(
                    widget_ner_query=monitoring_object.ner_query,
                    datetime_from=datetime_from,
                    datetime_to=datetime_to,
                    parent_search=s
                )
            )
        s = ss
        if object_id:
            s = s[0]
    return s
