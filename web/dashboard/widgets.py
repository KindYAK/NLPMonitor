from dashboard.services import es_document_eval_search_factory
from evaluation.services import normalize_documents_eval_dynamics, calc_source_input, divide_posneg_source_buckets


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
    # Positive-negative distribution
    # if widget.criterion.value_range_from < 0:
    #     # Positive/negative dynamics
    #     s.aggs['posneg'].bucket(name="dynamics",
    #                             agg_type="date_histogram",
    #                             field="document_datetime",
    #                             calendar_interval="1w") \
    #         .metric("dynamics_weight", agg_type="avg", field="value")
    r = s.execute()
    normalize_documents_eval_dynamics(r, None)
    context_update[f'dynamics_{widget.id}'] = [
        {
            "date": bucket.key_as_string,
            "value": bucket.dynamics_weight.value,
        } for bucket in r.aggregations.dynamics
    ]
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
