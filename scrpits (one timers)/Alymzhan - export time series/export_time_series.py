import datetime
import json

from elasticsearch_dsl import Search

from mainapp.services import apply_fir_filter
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_DOCUMENT

topic_modelling = "bigartm_two_years"
topic_weight_threshold = 0.05
granularity = "1w"
smooth = False


def get_total_metrics(granularity, topic_weight_threshold):
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


def get_current_topics_metrics(topics, granularity, topic_weight_threshold):
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


def get_topics_info():
    s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
        .filter("range", topic_weight={"gte": topic_weight_threshold}) \
        .filter("range", datetime={"gte": datetime.date(2000, 1, 1)})
    s.aggs.bucket(name='topics', agg_type="terms", field='topic_id', size=10000) \
        .metric("topic_weight", agg_type="sum", field="topic_weight")
    result = s.execute()
    topic_info_dict = dict(
        (bucket.key, {
            "count": bucket.doc_count,
            "weight_sum": bucket.topic_weight.value
        }) for bucket in result.aggregations.topics.buckets
    )
    # Get actual topics
    topics = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING) \
        .filter("term", **{"name": topic_modelling}) \
        .filter("term", **{"is_ready": True}).execute()[0]['topics']
    # Fill topic objects with meta data
    for topic in topics:
        if topic.id in topic_info_dict:
            topic.size = topic_info_dict[topic.id]['count']
            topic.weight = topic_info_dict[topic.id]['weight_sum']
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
    return dict((topic.id, {
        "size": topic.size,
        "weight": topic.weight,
        "words": [words.to_dict() for words in list(topic.topic_words)],
    }) for topic in topics)


def get_topic_details(topic_id):
    # Total metrics
    total_metrics_dict = get_total_metrics(granularity, topic_weight_threshold)
    # Current topic metrics
    topic_documents = get_current_topics_metrics([topic_id], granularity, topic_weight_threshold)
    # Get documents, set weights
    documents = get_documents_with_weights(topic_documents)
    # Normalize
    normalize_topic_documnets(topic_documents, total_metrics_dict)
    # Separate signals
    absolute_power = [bucket.doc_count for bucket in topic_documents.aggregations.dynamics.buckets]
    relative_power = [bucket.doc_count_normal for bucket in topic_documents.aggregations.dynamics.buckets]
    relative_weight = [bucket.dynamics_weight.value for bucket in topic_documents.aggregations.dynamics.buckets]
    # Smooth
    if smooth:
        absolute_power = apply_fir_filter(absolute_power, granularity=granularity)
        relative_power = apply_fir_filter(relative_power, granularity=granularity)
        relative_weight = apply_fir_filter(relative_weight, granularity=granularity)
    # Create context
    topic_info = {}
    topic_info['date_ticks'] = [bucket.key_as_string for bucket in topic_documents.aggregations.dynamics.buckets]
    topic_info['absolute_power'] = absolute_power
    topic_info['relative_power'] = relative_power
    topic_info['relative_weight'] = relative_weight
    topic_info['source_weight'] = sorted([bucket.to_dict() for bucket in topic_documents.aggregations.source.buckets],
                                         key=lambda x: x['source_weight']['value'],
                                         reverse=True)
    topic_info['topic_info'] = topics_info[topic_id]
    return topic_info


s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}").source([])[:0]
s.aggs.bucket(name="topic_ids", agg_type="terms", field="topic_id", size=5000000)
r = s.execute()

topics_info = get_topics_info()

output = []
for topic_id in r.aggregations.topic_ids.buckets:
    topic_info = get_topic_details(topic_id.key)
    output.append(topic_info)


with open(f"/output-topics-dynamics-{topic_modelling}.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(output))
