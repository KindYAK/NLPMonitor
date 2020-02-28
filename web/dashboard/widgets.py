from dashboard.services import es_document_eval_search_factory


def overall_positive_negative(dashboard, widget):
    context_update = {}
    s = es_document_eval_search_factory(dashboard, widget)
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
    print("!!!", r.took)
    context_update['overall_posneg'] = [bucket.doc_count for bucket in r.aggregations.posneg.buckets]
    return context_update
