import datetime

from elasticsearch_dsl import Search, Q

from mainapp.constants import SEARCH_CUTOFF_CONFIG
from mainapp.services_es import get_elscore_cutoff
from nlpmonitor.settings import ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_DOCUMENT, ES_CLIENT, ES_INDEX_DOCUMENT_EVAL


def filter_analytical_query(topic_modelling, criterion_id, action, value):
    s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
              .filter("term", **{'topic_modelling.keyword': topic_modelling}) \
              .filter("term", criterion_id=criterion_id) \
              .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)})\
              .filter("range", value={action: value}) \
              .source(['document_es_id']).sort('-value')
    return (d.document_es_id for d in s.scan())


def get_current_document_evals(topic_modelling, criterion, granularity, documents_ids_to_filter,
                               date_from=None, date_to=None, analytical_query=None):
    # Basic search object
    std = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
              .filter("term", **{'topic_modelling.keyword': topic_modelling}) \
              .filter("term", criterion_id=criterion.id).sort('-value') \
              .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}) \
              .source(['document_es_id'])

    # Analytical querying
    if analytical_query:
        documents_ids_to_filter_by_query = set()
        for q in analytical_query:
            documents_ids_to_filter_by_query.update(filter_analytical_query(topic_modelling, **q))
        if documents_ids_to_filter:
            documents_ids_to_filter = list(set(documents_ids_to_filter).intersection(documents_ids_to_filter_by_query))
        else:
            documents_ids_to_filter = list(documents_ids_to_filter_by_query)

    # Filter by group and keyword
    if documents_ids_to_filter or analytical_query:
        std = std.filter("terms", **{'document_es_id.keyword': documents_ids_to_filter})

    # Range selection
    if date_from:
        std = std.filter("range", document_datetime={"gte": date_from})
    if date_to:
        std = std.filter("range", document_datetime={"lte": date_to})

    # Posneg distribution
    if criterion.value_range_from < 0:
        neutrality_threshold = 0.1
        std.aggs.bucket(
            name="posneg",
            agg_type="range",
            field="value",
            ranges=
            [
                {"from": neutrality_threshold, "to": criterion.value_range_to},
                {"from": -neutrality_threshold, "to": neutrality_threshold},
                {"from": criterion.value_range_from, "to": neutrality_threshold}
            ]
        )
        std.aggs['posneg'].bucket(name="source",
                                  agg_type="terms",
                                  field="document_source.keyword",
                                  size=25)

    # Dynamics
    if granularity:
        # Average dynamics
        std.aggs.bucket(name="dynamics",
                        agg_type="date_histogram",
                        field="document_datetime",
                        calendar_interval=granularity) \
                .metric("dynamics_weight", agg_type="avg", field="value")

        # Positive-negative distribution
        if criterion.value_range_from < 0:
            # Positive/negative dynamics
            std.aggs['posneg'].bucket(name="dynamics",
                                      agg_type="date_histogram",
                                      field="document_datetime",
                                      calendar_interval=granularity) \
                .metric("dynamics_weight", agg_type="avg", field="value")


    # Source distributions
    std.aggs.bucket(name="source", agg_type="terms", field="document_source.keyword") \
        .metric("source_value", agg_type="avg", field="value")

    # Execute search
    std = std[:200]
    document_evals = std.execute()

    # Top_news ids - get minimum values
    top_news = set()
    top_news.update((d.document_es_id for d in document_evals))
    std_min = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
              .filter("term", **{'topic_modelling.keyword': topic_modelling}) \
              .filter("term", criterion_id=criterion.id).sort('value') \
              .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}) \
              .source(['document_es_id'])
    if documents_ids_to_filter or analytical_query:
        std_min = std_min.filter("terms", **{'document_es_id.keyword': documents_ids_to_filter})
    if date_from:
        std_min = std_min.filter("range", document_datetime={"gte": date_from})
    if date_to:
        std_min = std_min.filter("range", document_datetime={"lte": date_to})
    std_min = std_min[:200]
    document_evals_min = std_min.execute()
    top_news.update((d.document_es_id for d in document_evals_min))
    return document_evals, top_news


def get_criterions_values_for_normalization(criterions, topic_modelling, granularity=None, analytical_query=None):
    # Get max positive/negative values for criterion
    max_criterion_value_dict = {}
    total_criterion_date_value_dict = {}
    for criterion in criterions:
        max_criterion_value_dict[criterion.id] = {}
        s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
                    .filter("term", criterion_id=criterion.id) \
                    .filter("term", **{'topic_modelling.keyword': topic_modelling})[:0]
        s.aggs.metric(name="max_value", agg_type="max", field="value")
        if criterion.value_range_from < 0:
            s.aggs.metric(name="min_value", agg_type="min", field="value")
        if granularity:
            s.aggs.bucket(name="dynamics",
                            agg_type="date_histogram",
                            field="document_datetime",
                            calendar_interval=granularity) \
                .metric("dynamics_weight", agg_type="avg", field="value")
        r = s.execute()
        max_criterion_value_dict[criterion.id]["max_positive"] = r.aggregations.max_value.value
        if criterion.value_range_from < 0:
            max_criterion_value_dict[criterion.id]["max_negative"] = r.aggregations.min_value.value
        if granularity:
            total_criterion_date_value_dict[criterion.id] = dict(
                (t.key_as_string, t.dynamics_weight.value) for t in r.aggregations.dynamics.buckets
            )
        else:
            total_criterion_date_value_dict[criterion.id] = {}
    return max_criterion_value_dict, total_criterion_date_value_dict


def normalize_documents_eval_dynamics(document_evals, total_metrics_dict):
    normalizer = None
    if not total_metrics_dict:
        normalizer = max(abs(max(bucket.dynamics_weight.value if bucket.dynamics_weight.value else 0 for bucket in document_evals.aggregations.dynamics.buckets)),
                         abs(max(-bucket.dynamics_weight.value if bucket.dynamics_weight.value else 0 for bucket in document_evals.aggregations.dynamics.buckets)))
    for bucket in document_evals.aggregations.dynamics.buckets:
        if not bucket.dynamics_weight.value:
            bucket.dynamics_weight.value = 0
            continue
        if total_metrics_dict:
            val = bucket.dynamics_weight.value
            total_val = total_metrics_dict[bucket.key_as_string]
            if val * total_val > 0:
                bucket.dynamics_weight.value /= abs(total_val)
            else:
                bucket.dynamics_weight.value *= (1 + abs(val - total_val))
        else:
            bucket.dynamics_weight.value /= normalizer


def get_documents_with_values(top_news_total, criterions, topic_modelling, max_criterion_value_dict, date_from=None, date_to=None):
    # Get documents and documents eval
    sd = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
             .filter('terms', _id=list(top_news_total)) \
             .source(('id', 'title', 'source', 'datetime',))[:1000]
    if date_from:
        sd = sd.filter("range", datetime={"gte": date_from})
    if date_to:
        sd = sd.filter("range", datetime={"lte": date_to})
    documents = sd.scan()
    documents_dict = dict((d.meta.id, d) for d in documents)
    std = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
            .filter("terms", **{'criterion_id': [c.id for c in criterions]}) \
            .filter("term", **{'topic_modelling.keyword': topic_modelling}) \
            .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}) \
            .filter("terms", **{'document_es_id.keyword': list(top_news_total)}) \
            .source(['document_es_id', 'value', 'criterion_id'])[:100000]
    document_evals = std.scan()

    # Creating final documents dict
    documents_eval_dict = {}
    seen_id = set()
    for td in document_evals:
        if td.document_es_id in documents_dict and documents_dict[td.document_es_id].id in seen_id \
                and td.document_es_id not in documents_eval_dict:
            continue
        if td.document_es_id not in documents_eval_dict:
            documents_eval_dict[td.document_es_id] = {}
            documents_eval_dict[td.document_es_id]['document'] = documents_dict[td.document_es_id]
            seen_id.add(documents_dict[td.document_es_id].id)
        if td.value > 0:
            documents_eval_dict[td.document_es_id][td.criterion_id] = \
                td.value / max_criterion_value_dict[td.criterion_id]["max_positive"]
        else:
            documents_eval_dict[td.document_es_id][td.criterion_id] = \
                td.value / -max_criterion_value_dict[td.criterion_id]["max_negative"]
    dict_vals = sorted(documents_eval_dict.items(), key=lambda x: sum(abs(i) for i in x[1].values() if type(i) == float), reverse=True)
    return dict(dict_vals[:200])


def get_documents_ids_filter(topics, keyword, topic_modelling, topic_weight_threshold):
    is_empty_search = False
    documents_ids_to_filter = []
    if topics:
        s = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
                .filter("terms", **{"topic_id.keyword": topics}) \
                .filter("term", **{"topic_modelling.keyword": topic_modelling}) \
                .filter("range", topic_weight={"gte": topic_weight_threshold}) \
                .source(("document_es_id",))[:10000000]
        documents_ids_to_filter = list(set([d.document_es_id for d in s.scan()]))
        if not documents_ids_to_filter:
            is_empty_search = True

    if keyword:
        s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
        q = Q('multi_match',
              query=keyword,
              fields=['title^10',
                      'tags^3',
                      'categories^3',
                      'text^2'])
        s = s.query(q)
        s = s.source(tuple())
        search_lvl = "SEARCH_LVL_LIGHT"
        s = s[:SEARCH_CUTOFF_CONFIG[search_lvl]['ABS_MAX_RESULTS_CUTOFF']]
        r = s.execute()
        cutoff = get_elscore_cutoff([d.meta.score for d in r], search_lvl)
        keyword_ids_to_filter = [d.meta.id for d in r[:cutoff]]
        if topics:
            documents_ids_to_filter = list(set(documents_ids_to_filter).intersection(set(keyword_ids_to_filter)))
        else:
            documents_ids_to_filter = keyword_ids_to_filter
        if not documents_ids_to_filter:
            is_empty_search = True
    return is_empty_search, documents_ids_to_filter
