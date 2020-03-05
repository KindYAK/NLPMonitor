import datetime

from dashboard.services import es_document_eval_search_factory
from evaluation.services import normalize_documents_eval_dynamics, calc_source_input, divide_posneg_source_buckets, \
    get_documents_with_values, get_criterions_values_for_normalization, normalize_buckets_main_topics, get_topic_dict, \
    smooth_buckets, normalize_documents_eval_dynamics_with_virt_negative


def overall_positive_negative(dashboard, widget):
    context_update = {}
    s = es_document_eval_search_factory(dashboard, widget)
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
    context_update['widget'] = widget
    return context_update


def dynamics(dashboard, widget):
    context_update = {}
    s = es_document_eval_search_factory(dashboard, widget)
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
                                                dashboard.topic_modelling_name,
                                                granularity="1w")
    if not widget.criterion.calc_virt_negative:
        normalize_documents_eval_dynamics(r, total_criterion_date_value_dict[widget.criterion.id])
    else:
        normalize_documents_eval_dynamics_with_virt_negative(r, dashboard.topic_modelling_name, "1w", widget.criterion)
    buckets = r.aggregations.dynamics.buckets
    # smooth_buckets(buckets,
    #                is_posneg=False,
    #                granularity="1w")
    context_update[f'dynamics_{widget.id}'] = buckets
    context_update['widget'] = widget
    return context_update


def source_distribution(dashboard, widget):
    context_update = {}
    s = es_document_eval_search_factory(dashboard, widget)
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
    context_update['widget'] = widget
    return context_update


def top_news(dashboard, widget):
    context_update = {}
    top_news_ids = set()
    num_news = 50
    # Get top news
    s = es_document_eval_search_factory(dashboard, widget)
    s = s.source(['document_es_id'])[:num_news].sort('-value')
    top_news_ids.update((d.document_es_id for d in s.execute()))

    # Get bottom news
    s = es_document_eval_search_factory(dashboard, widget)
    s = s.source(['document_es_id'])[:num_news].sort('value')
    top_news_ids.update((d.document_es_id for d in s.execute()))

    max_criterion_value_dict, _ = \
        get_criterions_values_for_normalization([widget.criterion],
                                                dashboard.topic_modelling_name,
                                                granularity=None)

    documents_eval_dict = get_documents_with_values(top_news_ids,
                                                    [widget.criterion],
                                                    dashboard.topic_modelling_name,
                                                    max_criterion_value_dict,
                                                    top_news_num=num_news)

    context_update[f'top_news_{widget.id}'] = documents_eval_dict
    context_update['widget'] = widget
    return context_update


def top_topics(dashboard, widget):
    context_update = {}
    s = es_document_eval_search_factory(dashboard, widget)
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
    topics_dict, tm_dict = get_topic_dict(dashboard.topic_modelling_name)
    last_date = r.aggregations.late_date.value_as_string
    last_date = datetime.datetime.fromisoformat(last_date[:19])
    context_update[f'top_topics_{widget.id}'] = normalize_buckets_main_topics(r.aggregations.posneg.buckets[-1].top_topics.buckets,
                                          topics_dict, tm_dict, 0.05, last_date)
    context_update[f'bottom_topics_{widget.id}'] = normalize_buckets_main_topics(r.aggregations.posneg.buckets[0].bottom_topics.buckets,
                                          topics_dict, tm_dict, 0.05, last_date)
    context_update['dashboard'] = dashboard
    context_update['widget'] = widget
    return context_update
