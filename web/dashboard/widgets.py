from dashboard.services import es_document_eval_search_factory
from evaluation.services import normalize_documents_eval_dynamics


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
