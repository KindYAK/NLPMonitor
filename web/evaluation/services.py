import datetime

from elasticsearch_dsl import Search, Q

from mainapp.services_es import filter_by_elscore
from nlpmonitor.settings import ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_DOCUMENT, ES_CLIENT, ES_INDEX_DOCUMENT_EVAL


def get_total_metrics(topic_modelling, criterion, granularity, documents_ids_to_filter):
    std_total = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
        .filter("term", topic_modelling=topic_modelling) \
        .filter("term", criterion_id=criterion.id) \
        .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)})
    if documents_ids_to_filter:
        std_total = std_total.filter("terms", **{'document_es_id.keyword': documents_ids_to_filter})
    if granularity:
        std_total.aggs.bucket(name="dynamics",
                              agg_type="date_histogram",
                              field="document_datetime",
                              calendar_interval=granularity)
    topic_documents_total = std_total.execute()
    total_metrics_dict = dict(
        (
            t.key_as_string, t.doc_count,
        ) for t in topic_documents_total.aggregations.dynamics.buckets
    )
    return total_metrics_dict


def get_current_document_evals(topic_modelling, criterion, granularity, documents_ids_to_filter, date_from=None, date_to=None):
    std = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
              .filter("term", **{'topic_modelling.keyword': topic_modelling}) \
              .filter("term", criterion_id=criterion.id).sort('-value') \
              .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}) \
              .source(['document_es_id'])
    if documents_ids_to_filter:
        std = std.filter("terms", **{'document_es_id.keyword': documents_ids_to_filter})
    if date_from:
        std = std.filter("range", document_datetime={"gte": date_from})
    if date_to:
        std = std.filter("range", document_datetime={"lte": date_to})
    std = std[:100]
    if granularity:
        std.aggs.bucket(name="dynamics",
                        agg_type="date_histogram",
                        field="document_datetime",
                        calendar_interval=granularity) \
                .metric("dynamics_weight", agg_type="avg", field="value")
    std.aggs.bucket(name="source", agg_type="terms", field="document_source.keyword") \
        .metric("source_value", agg_type="avg", field="value")
    document_evals = std.execute()

    # Top_news ids
    top_news = set()
    top_news.update((d.document_es_id for d in document_evals))
    std_min = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
              .filter("term", **{'topic_modelling.keyword': topic_modelling}) \
              .filter("term", criterion_id=criterion.id).sort('value') \
              .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}) \
              .source(['document_es_id'])
    if documents_ids_to_filter:
        std_min = std_min.filter("terms", **{'document_es_id.keyword': documents_ids_to_filter})
    if date_from:
        std_min = std_min.filter("range", document_datetime={"gte": date_from})
    if date_to:
        std_min = std_min.filter("range", document_datetime={"lte": date_to})
    std_min = std_min[:100]
    document_evals_min = std_min.execute()
    top_news.update((d.document_es_id for d in document_evals_min))
    return document_evals, top_news


def get_documents_with_values(top_news_total, criterions, topic_modelling, date_from=None, date_to=None):
    sd = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
             .filter('terms', _id=list(top_news_total)) \
             .source(('id', 'title', 'source', 'datetime',))[:1000]
    if date_from:
        sd = sd.filter("range", document_datetime={"gte": date_from})
    if date_to:
        sd = sd.filter("range", document_datetime={"lte": date_to})
    documents = sd.scan()
    documents_dict = dict((d.meta.id, d) for d in documents)
    std = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
            .filter("terms", **{'document_es_id.keyword': list(top_news_total)}) \
            .filter("terms", **{'criterion_id': [c.id for c in criterions]}) \
            .filter("term", **{'topic_modelling.keyword': topic_modelling}) \
            .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}) \
            .source(['document_es_id', 'value', 'criterion_id'])[:1000]
    document_evals = std.execute()

    documents_eval_dict = {}
    for td in document_evals:
        if td.document_es_id not in documents_eval_dict:
            documents_eval_dict[td.document_es_id] = {}
            documents_eval_dict[td.document_es_id]['document'] = documents_dict[td.document_es_id]
        documents_eval_dict[td.document_es_id][td.criterion_id] = td.value
    return documents_eval_dict


def normalize_topic_documnets(topic_documents, total_metrics_dict):
    for bucket in topic_documents.aggregations.dynamics.buckets:
        total_size = total_metrics_dict[bucket.key_as_string]
        if total_size != 0:
            bucket.doc_count_normal = bucket.doc_count / total_size
        else:
            bucket.doc_count_normal = 0


def get_documents_ids_filter(topics, keyword, topic_modelling):
    is_empty_search = False
    documents_ids_to_filter = []
    if topics:
        s = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
                .filter("terms", **{"topic_id.keyword": topics}) \
                .filter("term", **{"topic_modelling.keyword": topic_modelling}) \
                .filter("range", topic_weight={"gte": 0.1}) \
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
        s = s[:500000]
        r = s.execute()
        cutoff = filter_by_elscore([d.meta.score for d in r], "SEARCH_LVL_HARD")
        keyword_ids_to_filter = [d.meta.id for d in r[:cutoff]]
        if topics:
            documents_ids_to_filter = list(set(documents_ids_to_filter).intersection(set(keyword_ids_to_filter)))
        else:
            documents_ids_to_filter = keyword_ids_to_filter
        if not documents_ids_to_filter:
            is_empty_search = True
    return is_empty_search, documents_ids_to_filter
