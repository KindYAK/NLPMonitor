import datetime

from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_DOCUMENT


def normalize_topic_documnets(topic_documents, total_metrics_dict):
    for bucket in topic_documents.aggregations.dynamics.buckets:
        total_weight = total_metrics_dict[bucket.key_as_string]['weight']
        total_size = total_metrics_dict[bucket.key_as_string]['size']
        if total_weight != 0:
            bucket.dynamics_weight.value /= total_weight
        if total_size != 0:
            bucket.doc_count_normal = bucket.doc_count / total_size
        else:
            bucket.doc_count_normal = 0


def get_documents_with_weights(topic_documents):
    sd = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
             .filter('terms', _id=[d.document_es_id for d in topic_documents]) \
             .source(('id', 'title', 'source', 'datetime',))[:100]
    documents = sd.execute()
    weight_dict = {}
    for td in topic_documents:
        if td.document_es_id not in weight_dict:
            weight_dict[td.document_es_id] = td.topic_weight
        else:
            weight_dict[td.document_es_id] += td.topic_weight
    for document in documents:
        document.weight = weight_dict[document.meta.id]
    documents = sorted(documents, key=lambda x: x.weight, reverse=True)
    return documents


def get_current_topics_metrics(topic_modelling, topics, granularity, topic_weight_threshold):
    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
              .filter("terms", topic_id=topics).sort("-topic_weight") \
              .filter("range", topic_weight={"gte": topic_weight_threshold}) \
              .filter("range", datetime={"gte": datetime.date(2000, 1, 1)}) \
              .source(['document_es_id', 'topic_weight'])[:100]
    std.aggs.bucket(name="dynamics",
                    agg_type="date_histogram",
                    field="datetime",
                    calendar_interval=granularity) \
        .metric("dynamics_weight", agg_type="sum", field="topic_weight")
    std.aggs.bucket(name="source", agg_type="terms", field="document_source") \
        .metric("source_weight", agg_type="sum", field="topic_weight")
    topic_documents = std.execute()
    return topic_documents


def get_total_metrics(topic_modelling, granularity, topic_weight_threshold):
    std_total = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
        .filter("range", topic_weight={"gte": topic_weight_threshold}) \
        .filter("range", datetime={"gte": datetime.date(2000, 1, 1)})
    std_total.aggs.bucket(name="dynamics",
                          agg_type="date_histogram",
                          field="datetime",
                          calendar_interval=granularity) \
                  .metric("dynamics_weight", agg_type="sum", field="topic_weight")
    topic_documents_total = std_total.execute()
    total_metrics_dict = dict(
        (
            t.key_as_string,
            {
                "size": t.doc_count,
                "weight": t.dynamics_weight.value
            }
        ) for t in topic_documents_total.aggregations.dynamics.buckets
    )
    return total_metrics_dict
