import datetime
from collections import defaultdict

from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_TOPIC_MODELLING


def get_topics_aggregations(topic_modelling, topic_weight_threshold, is_multi_corpus):

    s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
        .filter("range", topic_weight={"gte": topic_weight_threshold})
    s.aggs.bucket(name='topics', agg_type="terms", field='topic_id', size=10000) \
        .metric("topic_weight", agg_type="sum", field="topic_weight")
    if is_multi_corpus:
        s.aggs['topics'].bucket(name="corpus", agg_type="terms", field="document_corpus", size=10000) \
            .metric("topic_weight", agg_type="sum", field="topic_weight")
    result = s.execute()
    topic_info_dict = dict(
        (bucket.key, {
            "count": bucket.doc_count,
            "weight_sum": bucket.topic_weight.value,
            "corpus_weights": dict((
                (bucket_corpus.key,
                {
                    "count": bucket_corpus.doc_count,
                    "weight_sum": bucket_corpus.topic_weight.value,
                }) for bucket_corpus in bucket.corpus.buckets)
               ) if is_multi_corpus else None
        }) for bucket in result.aggregations.topics.buckets
    )
    return topic_info_dict


def get_topics_with_meta(topic_modelling, topic_weight_threshold, is_multi_corpus):
    topic_info_dict = get_topics_aggregations(topic_modelling,
                                              topic_weight_threshold,
                                              is_multi_corpus)
    # Get actual topics
    topics = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING) \
        .filter("term", **{"name": topic_modelling}) \
        .filter("term", **{"is_ready": True}).execute()[0]['topics']
    # Fill topic objects with meta data
    for topic in topics:
        if topic.id in topic_info_dict:
            topic.size = topic_info_dict[topic.id]['count']
            topic.weight = topic_info_dict[topic.id]['weight_sum']
            # Multi corpus info:
            if is_multi_corpus:
                topic.corpus_weights = topic_info_dict[topic.id]['corpus_weights']
        else:
            topic.size, topic.weight = 0, 0
        if not topic.topic_words:
            continue
        max_word_weight = max((word.weight for word in topic.topic_words))
        for topic_word in topic.topic_words:
            topic_word.weight /= max_word_weight
            topic_word.word = topic_word.word[0].upper() + topic_word.word[1:]  # Stub - upper case
        # Stub - topic name upper case
        topic.name = ", ".join([w[0].upper() + w[1:] for w in topic.name.split(", ")])

    # Normalize topic weights by max
    max_topic_weight = max((topic.weight for topic in topics))
    if max_topic_weight != 0:
        for topic in topics:
            topic.weight /= max_topic_weight

    # Normalize corpus weights
    if is_multi_corpus:
        corpus_total_weights = defaultdict(int)
        for topic in topics:
            if not hasattr(topic, "corpus_weights"):
                continue
            for key, value in topic.corpus_weights.to_dict().items():
                corpus_total_weights[key] += value['weight_sum']
        for topic in topics:
            if not hasattr(topic, "corpus_weights"):
                continue
            total_weight = 0
            for corpus in corpus_total_weights.keys():
                if corpus in topic.corpus_weights:
                    topic.corpus_weights[corpus].weight_sum /= corpus_total_weights[corpus]
                    total_weight += topic.corpus_weights[corpus].weight_sum
            for corpus in corpus_total_weights.keys():
                if corpus in topic.corpus_weights:
                    topic.corpus_weights[corpus].weight_sum /= total_weight
    return topics


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
              .filter("range", datetime={"lte": datetime.datetime.now().date()}) \
              .source(['document_es_id', 'topic_weight'])[:100]
    std.aggs.bucket(name="dynamics",
                    agg_type="date_histogram",
                    field="datetime",
                    calendar_interval=granularity) \
        .metric("dynamics_weight", agg_type="sum", field="topic_weight")
    std.aggs.bucket(name="source", agg_type="terms", field="document_source") \
        .metric("source_weight", agg_type="sum", field="topic_weight")
    topic_documents = std.execute()
    return topic_documents, std.count().value


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
