import datetime

from elasticsearch_dsl import Search, Q

from evaluation.models import TopicsEval
from mainapp.constants import SEARCH_CUTOFF_CONFIG
from mainapp.services import apply_fir_filter
from mainapp.services_es import get_elscore_cutoff
from nlpmonitor.settings import ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_DOCUMENT, ES_CLIENT, ES_INDEX_DOCUMENT_EVAL, \
    ES_INDEX_TOPIC_MODELLING
from topicmodelling.services import get_total_metrics


def filter_analytical_query(topic_modelling, criterion_id, action, value):
    s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{topic_modelling}_{criterion_id}") \
              .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}).filter("range", document_datetime={"lte": datetime.datetime.now().date()}) \
              .filter("range", value={action: value}) \
              .source(['document_es_id']).sort('-value')
    return (d.document_es_id for d in s.scan())


def get_current_document_evals(topic_modelling, criterion, granularity, documents_ids_to_filter,
                               date_from=None, date_to=None, analytical_query=None):
    # Basic search object
    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{topic_modelling}_{criterion.id}") \
              .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}).filter("range", document_datetime={"lte": datetime.datetime.now().date()}) \
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
        std = std.filter("terms", **{'document_es_id': documents_ids_to_filter})

    # Range selection
    if date_from:
        std = std.filter("range", document_datetime={"gte": date_from})
    if date_to:
        std = std.filter("range", document_datetime={"lte": date_to})

    # Posneg distribution
    if criterion.value_range_from < 0:
        range_center = (criterion.value_range_from + criterion.value_range_to) / 2
        neutral_neighborhood = 0.1
    else:
        range_center = 0
        neutral_neighborhood = 0.001
    std.aggs.bucket(
        name="posneg",
        agg_type="range",
        field="value",
        ranges=
        [
            {"from": criterion.value_range_from, "to": range_center-neutral_neighborhood},
            {"from": range_center - neutral_neighborhood, "to": range_center + neutral_neighborhood},
            {"from": range_center + neutral_neighborhood, "to": criterion.value_range_to},
        ]
    )
    std.aggs['posneg'].bucket(name="top_topics",
                              agg_type="terms",
                              field="topic_ids_top",
                              size=10)
    std.aggs['posneg'].bucket(name="bottom_topics",
                              agg_type="terms",
                              field="topic_ids_bottom",
                              size=10)
    if criterion.value_range_from < 0:
        std.aggs['posneg'].bucket(name="source",
                                  agg_type="terms",
                                  field="document_source",
                                  size=20)
    else:
        # Source distributions
        std.aggs.bucket(name="source", agg_type="terms", field="document_source")
        std.aggs['source'].metric("source_value_sum", agg_type="sum", field="value")
        std.aggs['source'].metric("source_value_average", agg_type="avg", field="value")

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

    # Execute search
    std = std[:200]
    document_evals = std.execute()

    # Top_news ids - get minimum values
    top_news = set()
    top_news.update((d.document_es_id for d in document_evals))
    std_min = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{topic_modelling}_{criterion.id}") \
              .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}).filter("range", document_datetime={"lte": datetime.datetime.now().date()}) \
              .source(['document_es_id']).sort('value')
    if documents_ids_to_filter or analytical_query:
        std_min = std_min.filter("terms", **{'document_es_id': documents_ids_to_filter})
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
        s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{topic_modelling}_{criterion.id}")[:0]
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


def normalize_documents_eval_dynamics_with_virt_negative(document_evals, topic_modelling, granularity, criterion):
    s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{topic_modelling}_{criterion.id}_neg") \
        .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}).filter("range", document_datetime={"lte": datetime.datetime.now().date()}) \
        .source([])[:0]
    s.aggs.bucket(name="dynamics",
                    agg_type="date_histogram",
                    field="document_datetime",
                    calendar_interval=granularity) \
        .metric("dynamics_weight", agg_type="avg", field="value")
    r = s.execute()
    negative_values_dict = dict(
        (t.key_as_string, t.dynamics_weight.value) for t in r.aggregations.dynamics.buckets
    )
    for bucket in document_evals.aggregations.dynamics.buckets:
        if not bucket.dynamics_weight.value:
            bucket.dynamics_weight.value = 0
            continue
        val = bucket.dynamics_weight.value
        neg_val = negative_values_dict[bucket.key_as_string]
        try:
            bucket.dynamics_weight.value = (val / (val + neg_val))
        except ZeroDivisionError:
            bucket.dynamics_weight.value = val


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
    std = Search(using=ES_CLIENT, index=[f"{ES_INDEX_DOCUMENT_EVAL}_{topic_modelling}_{c.id}" for c in criterions]) \
            .filter("terms", **{'document_es_id': list(top_news_total)}) \
            .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}).filter("range", document_datetime={"lte": datetime.datetime.now().date()}) \
            .source(['document_es_id', 'value'])[:10000]
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
        criterion_id = int(td.meta.index.split("_")[-1])
        if td.value >= 0:
            documents_eval_dict[td.document_es_id][criterion_id] = \
                td.value / max_criterion_value_dict[criterion_id]["max_positive"]
        else:
            documents_eval_dict[td.document_es_id][criterion_id] = \
                td.value / -max_criterion_value_dict[criterion_id]["max_negative"]
    dict_vals = sorted(documents_eval_dict.items(), key=lambda x: sum(abs(i) for i in x[1].values() if type(i) == float), reverse=True)
    return dict(dict_vals[:400])


def get_documents_ids_filter(topics, keyword, topic_modelling, topic_weight_threshold):
    is_empty_search = False
    documents_ids_to_filter = []
    if topics:
        s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
                .filter("terms", **{"topic_id": topics}) \
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


def divide_posneg_source_buckets(buckets):
    sources_criterion_dict = {}
    for i, pn in enumerate(buckets):
        tonality = ["negative", "neutral", "positive"][i]
        for bucket in pn.source.buckets:
            if bucket.key not in sources_criterion_dict:
                sources_criterion_dict[bucket.key] = {}
                sources_criterion_dict[bucket.key]['key'] = bucket.key
                sources_criterion_dict[bucket.key]['positive'] = 0
                sources_criterion_dict[bucket.key]['neutral'] = 0
                sources_criterion_dict[bucket.key]['negative'] = 0
            sources_criterion_dict[bucket.key][tonality] = bucket.doc_count
    sources_criterion_dict = sorted(sources_criterion_dict.values(),
                                    key=lambda x: x['positive'] + x['negative'] + x['neutral'],
                                    reverse=True)
    return sources_criterion_dict


def get_topic_dict(topic_modelling):
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING) \
        .filter("term", **{"name": topic_modelling}) \
        .filter("term", **{"is_ready": True}).execute()[0]
    tm_info_dict = tm.to_dict()

    # Fill topic objects with meta data
    topic_info_dict = dict(
        (topic.id, topic.to_dict()) for topic in tm['topics']
    )
    del tm_info_dict['topics']
    return topic_info_dict, tm_info_dict


def normalize_buckets_main_topics(buckets, topics_dict, tm_dict, topic_weight_threshold, last_date):
    if not buckets:
        return buckets
    max_count = max((bucket.doc_count for bucket in buckets))

    total_metrics_dict = get_total_metrics(tm_dict['name'], "1w", topic_weight_threshold)
    for bucket in buckets:
        bucket.weight = bucket.doc_count / max_count
        bucket.info = topics_dict[bucket.key]

        # Dynamic danger analysis
        if 'period_maxes_mean' in bucket.info:
            bucket.resonance_score = (bucket.info['period_maxes_mean'] - tm_dict['period_maxes_mean_median']) / tm_dict['period_maxes_mean_std']
            bucket.period_score = (bucket.info['period_mean'] - tm_dict['period_median']) / tm_dict['period_std']
            bucket.period_days = bucket.info['period_mean']

            s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_dict['name']}") \
                    .filter("term", **{"topic_id": bucket.info.id}) \
                    .filter("range", topic_weight={"gte": topic_weight_threshold}) \
                    .filter("range", datetime={"gte": last_date - datetime.timedelta(days=365)}) \
                    .filter("range", datetime={"lte": last_date}) \
                    .source([])[:0]
            s.aggs.bucket(name="dynamics",
                          agg_type="date_histogram",
                          field="datetime",
                          calendar_interval="1w") \
                  .metric("dynamics_weight", agg_type="sum", field="topic_weight")
            r = s.execute()
            bs = r.aggregations.dynamics.buckets
            bs_signal = [b.dynamics_weight.value for b in bs]
            bs_signal = apply_fir_filter(bs_signal, granularity="1w")
            if len(bs) >= 4:
                total_weight_last = total_metrics_dict[bs[-2].key_as_string]['weight']
                total_weight_before_last = total_metrics_dict[bs[-4].key_as_string]['weight']
                y_delta = bs_signal[-2] / total_weight_last - bs_signal[-4] / total_weight_before_last
                bucket.trend_score = y_delta / (bucket.info['weight_change_std'] * 14)
            else:
                bucket.trend_score = 0
    return buckets


def get_low_volume_positive_topics(tm_dict, topics_dict, criterion, topic_weight_threshold, date_from=None, date_to=None):
    # Get topic evaluations
    evaluations = TopicsEval.objects.filter(criterion=criterion, topics__topic_modelling_name=tm_dict['name']) \
                    .distinct().prefetch_related('topics')
    topic_eval_dict = {}
    for evaluation in evaluations:
        if not evaluation.topics.exists():
            continue
        eval_topic_id = evaluation.topics.first().topic_id
        if eval_topic_id not in topic_eval_dict:
            topic_eval_dict[eval_topic_id] = []
        topic_eval_dict[eval_topic_id].append(evaluation.value)

    for t in topic_eval_dict.keys():
        topic_eval_dict[t] = sum(topic_eval_dict[t]) / len(topic_eval_dict[t])
    topic_eval_sorted = sorted(topic_eval_dict.items(), key=lambda x: x[1], reverse=True)
    range_center = (criterion.value_range_from + criterion.value_range_to) / 2
    neutrality_threshold = 0.1
    topic_eval_sorted = list(filter(lambda x: x[1] > range_center + neutrality_threshold, topic_eval_sorted))
    topic_eval_sorted = topic_eval_sorted[:(len(topic_eval_sorted) + 1) // 2]

    if len(topic_eval_sorted) == 0:
        return []

    # Get least highlighted topics
    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_dict['name']}") \
          .filter("terms", **{"topic_id": [t[0] for t in topic_eval_sorted]}) \
          .filter("range", topic_weight={"gte": topic_weight_threshold}) \
          .source([])[:0]
    if date_from:
        std = std.filter("range", datetime={"gte": date_from})
    if date_to:
        std = std.filter("range", datetime={"lte": date_to})
    std.aggs.bucket(name="topics", agg_type="terms", field="topic_id", size=len(topic_eval_sorted)) \
        .metric("topic_weight", agg_type="sum", field="topic_weight")
    r = std.execute()
    topics_sorted = sorted(((bucket.key, bucket.topic_weight.value) for bucket in r.aggregations.topics.buckets), key=lambda x: x[1] / topic_eval_dict[x[0]], reverse=False)
    topics_sorted = topics_sorted[:min(10, (len(topics_sorted) + 1) // 2)]

    # Creating result list
    res = [
        {
            "weight": topic[1] / topic_eval_dict[topic[0]],
            "resonance_score": (topics_dict[topic[0]]['period_maxes_mean'] - tm_dict['period_maxes_mean_median']) \
                               / tm_dict['period_maxes_mean_std'] if 'period_maxes_mean' in topics_dict[
                topic[0]] else None,
            "period_score": (topics_dict[topic[0]]['period_mean'] - tm_dict['period_median']) / tm_dict['period_std'] \
                if 'period_meain' in topics_dict[topic[0]] else None,
            "period_days": topics_dict[topic[0]]['period_mean'] \
                if 'period_meain' in topics_dict[topic[0]] else None,
            "info": topics_dict[topic[0]],
        } for topic in topics_sorted
    ]
    max_weight = max((t['weight'] for t in res)) if res else None
    for t in (res if res else []):
        t['weight'] /= max_weight
    return res


def get_total_group_dynamics(absoulte_values_dict, criterions, granularity, is_smooth):
    from collections import defaultdict

    # Dictionarize
    criterion_dynamics_dictionarized = {}
    all_ticks = set()
    for criterion in criterions:
        if not criterion.id in absoulte_values_dict:
            continue
        criterion_dynamics_dictionarized[criterion.id] = defaultdict(
            int,
            ((bucket.key_as_string, bucket.dynamics_weight.value) for bucket in absoulte_values_dict[criterion.id])
        )
        all_ticks.update(criterion_dynamics_dictionarized[criterion.id].keys())

    if not all_ticks:
        return {}

    # Calculate total group dynamics
    total_group_dynamics = {}
    for tick in all_ticks:
        total_group_dynamics[tick] = \
            sum((criterion_dynamics_dictionarized[c.id][tick] for c in criterions if c.id in absoulte_values_dict))

    # Sort, prepare, return
    ticks_sorted = sorted(list(all_ticks))
    dynamics = [total_group_dynamics[tick] for tick in ticks_sorted]
    if is_smooth:
        dynamics = apply_fir_filter(dynamics, granularity)
    return {
        "ticks": ticks_sorted,
        "dynamics": dynamics,
    }
