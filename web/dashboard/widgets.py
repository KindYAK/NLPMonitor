import datetime

from elasticsearch_dsl import Q

from dashboard.services import es_widget_search_factory, es_document_location_search_factory
from evaluation.services import calc_source_input, divide_posneg_source_buckets, \
    get_documents_with_values, get_criterions_values_for_normalization, normalize_buckets_main_topics, get_topic_dict, \
    smooth_buckets
from .util import location_buckets_parser, criterion_map_parser


def overall_positive_negative(widget):
    context_update = dict()
    s = es_widget_search_factory(widget)
    s = s.source(tuple())[:0]
    if widget.criterion.value_range_from < 0:
        range_center = (widget.criterion.value_range_from + widget.criterion.value_range_to) / 2
        neutral_neighborhood = 0.1
    else:
        range_center = 0
        neutral_neighborhood = 0.001
    s.aggs.bucket(
        name="posneg",
        agg_type="range",
        field="value",
        ranges=
        [
            {"from": widget.criterion.value_range_from, "to": range_center - neutral_neighborhood},
            {"from": range_center - neutral_neighborhood, "to": range_center + neutral_neighborhood},
            {"from": range_center + neutral_neighborhood, "to": widget.criterion.value_range_to},
        ]
    )
    r = s.execute()
    context_update[f'overall_posneg_{widget.id}'] = [bucket.doc_count for bucket in r.aggregations.posneg.buckets]
    return context_update


def dynamics(widget):
    context_update = {}
    s = es_widget_search_factory(widget)
    s = s.source(tuple())[:0]
    # Average dynamics
    s.aggs.bucket(name="dynamics",
                  agg_type="date_histogram",
                  field="document_datetime",
                  calendar_interval="1w") \
        .metric("dynamics_weight", agg_type="avg", field="value")
    r = s.execute()
    _, total_criterion_date_value_dict = \
        get_criterions_values_for_normalization([widget.criterion],
                                                widget.topic_modelling_name,
                                                granularity="1w")
    # if not widget.criterion.calc_virt_negative:
    #     normalize_documents_eval_dynamics(r, total_criterion_date_value_dict[widget.criterion.id])
    # else:
    #     normalize_documents_eval_dynamics_with_virt_negative(r, widget.topic_modelling_name, "1w", widget.criterion)
    buckets = r.aggregations.dynamics.buckets
    smooth_buckets(buckets,
                   is_posneg=False,
                   granularity="1w")
    context_update[f'dynamics_{widget.id}'] = buckets
    return context_update


def source_distribution(widget):
    context_update = dict()
    s = es_widget_search_factory(widget)
    s = s.source(tuple())[:0]

    # Posneg distribution
    if widget.criterion.value_range_from < 0:
        range_center = (widget.criterion.value_range_from + widget.criterion.value_range_to) / 2
        neutral_neighborhood = 0.1
    else:
        range_center = 0
        neutral_neighborhood = 0.001
    s.aggs.bucket(
        name="posneg",
        agg_type="range",
        field="value",
        ranges=
        [
            {"from": widget.criterion.value_range_from, "to": range_center - neutral_neighborhood},
            {"from": range_center - neutral_neighborhood, "to": range_center + neutral_neighborhood},
            {"from": range_center + neutral_neighborhood, "to": widget.criterion.value_range_to},
        ]
    )

    # Source distribution
    if widget.criterion.value_range_from < 0:
        s.aggs['posneg'].bucket(name="source",
                                  agg_type="terms",
                                  field="document_source",
                                  size=100)
    else:
        s.aggs.bucket(name="source", agg_type="terms", field="document_source")
        s.aggs['source'].metric("source_value_sum", agg_type="sum", field="value")
        s.aggs['source'].metric("source_value_average", agg_type="avg", field="value")
    r = s.execute()

    if widget.criterion.value_range_from < 0:
        context_update[f'source_distribution_{widget.id}'] = divide_posneg_source_buckets(r.aggregations.posneg.buckets)
    else:
        r = calc_source_input(r)
        context_update[f'source_distribution_{widget.id}'] = [
            {
                "source": bucket.key,
                "value": bucket.value,
            } for bucket in r.aggregations.source
        ]
        context_update[f'source_distribution_{widget.id}'] = \
            sorted(context_update[f'source_distribution_{widget.id}'], key=lambda x: x['value'], reverse=True)
    return context_update


def top_news(widget):
    return main_news(widget, "top")


def last_news(widget):
    return main_news(widget, "last")


def bottom_news(widget):
    return main_news(widget, "bottom")


def main_news(widget, mode):
    if mode not in ["bottom", "top", "last"]:
        raise Exception("NOT IMPLEMENTED!")

    context_update = dict()
    top_news_ids = set()
    num_news = 50
    range_center = (widget.criterion.value_range_from + widget.criterion.value_range_to) / 2
    neutrality_threshold = 0.01

    # Get top news
    s = es_widget_search_factory(widget)
    if mode == "top":
        s = s.source(['document_es_id'])[:num_news].sort('-value')
    elif mode == "last":
        s = s.filter("range", value={"gte": range_center + neutrality_threshold})
        s = s.source(['document_es_id']).sort('-document_datetime')[:num_news*5]
    top_news_ids.update((d.document_es_id for d in s.execute()))

    # Get bottom news
    s = es_widget_search_factory(widget)
    if mode == "bottom":
        s = s.source(['document_es_id'])[:num_news].sort('value')
    elif mode == "last":
        s = s.filter("range", value={"lte": range_center - neutrality_threshold})
        s = s.source(['document_es_id']).sort('-document_datetime')[:num_news*5]
    top_news_ids.update((d.document_es_id for d in s.execute()))

    max_criterion_value_dict, _ = \
        get_criterions_values_for_normalization([widget.criterion],
                                                widget.topic_modelling_name,
                                                granularity=None)

    documents_eval_dict = get_documents_with_values(top_news_ids,
                                                    [widget.criterion],
                                                    widget.topic_modelling_name,
                                                    max_criterion_value_dict,
                                                    top_news_num=num_news)

    if mode == "top":
        documents_eval_dict = dict(
            filter(lambda x: x[1][widget.criterion.id] >= range_center, documents_eval_dict.items())
        )
    elif mode == "bottom":
        documents_eval_dict = dict(
            filter(lambda x: x[1][widget.criterion.id] < range_center, documents_eval_dict.items())
        )

    if mode == "top":
        documents_eval_dict = dict(
            sorted(documents_eval_dict.items(), key=lambda x: x[1][widget.criterion.id], reverse=True)
        )
    if mode == "bottom":
        documents_eval_dict = dict(
            sorted(documents_eval_dict.items(), key=lambda x: x[1][widget.criterion.id], reverse=False)
        )
    elif mode == "last":
        documents_eval_dict = dict(
            sorted(documents_eval_dict.items(), key=lambda x: x[1]["document"]["datetime"], reverse=True)
        )
    context_update[f'top_news_{widget.id}'] = documents_eval_dict
    return context_update


def top_topics(widget):
    context_update = dict()
    s = es_widget_search_factory(widget)
    num_topics = 5
    # Posneg distribution
    if widget.criterion.value_range_from < 0:
        range_center = (widget.criterion.value_range_from + widget.criterion.value_range_to) / 2
        neutral_neighborhood = 0.1
    else:
        range_center = 0
        neutral_neighborhood = 0.001
    s.aggs.bucket(
        name="posneg",
        agg_type="range",
        field="value",
        ranges=
        [
            {"from": widget.criterion.value_range_from, "to": range_center - neutral_neighborhood},
            {"from": range_center - neutral_neighborhood, "to": range_center + neutral_neighborhood},
            {"from": range_center + neutral_neighborhood, "to": widget.criterion.value_range_to},
        ]
    )
    # Main topics
    s.aggs['posneg'].bucket(name="top_topics",
                              agg_type="terms",
                              field="topic_ids_top",
                              size=num_topics)
    s.aggs['posneg'].bucket(name="bottom_topics",
                              agg_type="terms",
                              field="topic_ids_bottom",
                              size=num_topics)
    s.aggs.metric('late_date', agg_type='max', field='document_datetime')
    r = s.execute()
    topics_dict, tm_dict = get_topic_dict(widget.topic_modelling_name)
    last_date = r.aggregations.late_date.value_as_string
    last_date = datetime.datetime.strptime(last_date[:19], "%Y-%m-%dT%H:%M:%S")
    context_update[f'top_topics_{widget.id}'] = normalize_buckets_main_topics(r.aggregations.posneg.buckets[-1].top_topics.buckets,
                                          topics_dict, tm_dict, 0.05, last_date)
    context_update[f'bottom_topics_{widget.id}'] = normalize_buckets_main_topics(r.aggregations.posneg.buckets[0].bottom_topics.buckets,
                                          topics_dict, tm_dict, 0.05, last_date)
    return context_update


def geo(widget):
    context_update = dict()
    s = es_document_location_search_factory(widget)
    s.aggs.bucket(name="criterion", agg_type="terms", field="location_name.keyword", size=5_000_000)
    s.aggs['criterion'].metric(name='criterion_value_sum',
                               agg_type='avg',
                               field=f'criterion_{widget.topic_modelling_name}_{widget.criterion_id}')
    results = s.execute()
    buckets = results.aggregations.criterion.buckets
    crit_type, colormap = criterion_map_parser(widget)
    data = location_buckets_parser(buckets, crit_type)
    context_update[f'map_type_{widget.id}'] = crit_type
    context_update[f'colormap_{widget.id}'] = colormap
    context_update[f'lat_lon_z_data_{widget.id}'] = data
    context_update[f'tm_{widget.id}'] = widget.topic_modelling_name
    context_update[f'criterion_{widget.id}'] = widget.criterion
    return context_update


def monitoring_objects_compare(widget):
    context_update = {}
    ss = es_widget_search_factory(widget)
    monitoring_objects = list()
    granularity = "1w"
    if widget.days_len < 65:
        granularity = "1d"
    for s, monitoring_object in zip(ss, widget.monitoring_objects_group.monitoring_objects.all()):
        s = s.source(tuple())[:0]
        if widget.criterion:
            s.aggs.bucket(name="dynamics",
                          agg_type="date_histogram",
                          field="document_datetime",
                          calendar_interval=granularity) \
                .metric("dynamics_weight", agg_type="avg", field="value")
            s.aggs.metric('avg', agg_type='avg', field='value')
            r = s.execute()
            value = r.aggregations.avg.value
            is_posneg = False
        else:
            s.aggs.bucket(name="dynamics",
                          agg_type="date_histogram",
                          field="datetime",
                          calendar_interval=granularity)
            value = s.count()
            r = s.execute()
            is_posneg = True
        buckets = r.aggregations.dynamics.buckets
        smooth_buckets(buckets,
                       is_posneg=is_posneg,
                       granularity=granularity)
        monitoring_objects.append(
            {
                "id": monitoring_object.id,
                "name": monitoring_object.name_query,
                "is_criterion": bool(widget.criterion),
                "value": value if value else 0,
                "dynamics": buckets
            }
        )
    monitoring_objects = sorted(monitoring_objects, key=lambda x: x['value'], reverse=False)
    context_update[f'monitoring_objects_{widget.id}'] = monitoring_objects
    return context_update
