import datetime
from collections import defaultdict
from statistics import mean, pstdev

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


def calc_topics_resonance(topics, topic_modelling, topic_weight_threshold=0.05):
    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
              .filter("range", document_num_views={"gt": 0}) \
              .filter("range", topic_weight={"gt": topic_weight_threshold})[:0]
    std.aggs.bucket("documents", agg_type="terms", field="document_es_id", size=5_000_000) \
        .metric("document_resonance", agg_type="avg", field="document_num_views")
    r = std.execute()
    if not r.aggregations.documents.buckets:
        return

    resonances = [bucket.document_resonance.value for bucket in r.aggregations.documents.buckets]
    resonance_mean = mean(resonances)
    resonance_std = pstdev(resonances)
    resonance_threshold = resonance_mean + resonance_std

    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
              .filter("range", document_num_views={"gt": 0}) \
              .filter("range", topic_weight={"gt": topic_weight_threshold})[:0]
    std.aggs.bucket("topics", agg_type="terms", field="topic_id", size=1000) \
        .bucket("resonance", agg_type="range", field="document_num_views", ranges=
    [
        {"from": 1, "to": resonance_threshold},
        {"from": resonance_threshold},
    ])
    r = std.execute()
    topic_resonances = dict(
        (bucket.key,
         {
             "low": bucket.resonance.buckets[0].doc_count,
             "high": bucket.resonance.buckets[1].doc_count,
         }) for bucket in r.aggregations.topics
    )

    total_low_resonance = 0
    total_high_resonance = 0
    for res in topic_resonances.values():
        total_low_resonance += res['low']
        total_high_resonance += res['high']

    for topic in topics:
        if topic.id in topic_resonances:
            topic.low_resonance_score = topic_resonances[topic.id]['low'] / total_low_resonance
            topic.high_resonance_score = topic_resonances[topic.id]['high'] / total_high_resonance
            total_weight = topic.low_resonance_score + topic.high_resonance_score
            topic.low_resonance_score /= total_weight
            topic.high_resonance_score /= total_weight


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
            topic_word.word = "_".join((word[0].upper() + word[1:]) for word in topic_word.word.split("_"))  # Stub - upper case
        # Stub - topic name upper case
        topic.name = ", ".join([s[0].upper() + s[1:] for w in topic.name.split(", ") for s in w.split("_") ])

    # Normalize topic weights by max
    max_topic_weight = max((topic.weight for topic in topics))
    if max_topic_weight != 0:
        for topic in topics:
            topic.weight /= max_topic_weight

    # Normalize multi corpus weights
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

    # Add resonance to existing topics
    calc_topics_resonance(topics, topic_modelling, topic_weight_threshold)
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


def get_current_topics_metrics(topic_modelling, topics, granularity, topic_weight_threshold, intersection=False):
    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
              .filter("terms", topic_id=topics) \
              .filter("range", topic_weight={"gte": topic_weight_threshold}) \
              .filter("range", datetime={"gte": datetime.date(2000, 1, 1)}) \
              .filter("range", datetime={"lte": datetime.datetime.now().date()}) \
              .sort("-topic_weight") \
              .source(['document_es_id', 'topic_weight'])[:100]
    std.aggs.bucket(name="dynamics",
                    agg_type="date_histogram",
                    field="datetime",
                    calendar_interval=granularity) \
        .metric("dynamics_weight", agg_type="sum", field="topic_weight")
    std.aggs.bucket(name="source", agg_type="terms", field="document_source") \
        .metric("source_weight", agg_type="sum", field="topic_weight")
    if intersection:
        std_intersection = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
                  .filter("terms", topic_id=topics) \
                  .filter("range", topic_weight={"gte": topic_weight_threshold}) \
                  .filter("range", datetime={"gte": datetime.date(2000, 1, 1)}) \
                  .filter("range", datetime={"lte": datetime.datetime.now().date()}) \
                  .sort("-topic_weight") \
                  .source(['document_es_id', 'topic_id'])[:10000]
        td_intersection = std_intersection.execute()
        document_topics_dict = defaultdict(list)
        for td in td_intersection:
            document_topics_dict[td.document_es_id].append(td.topic_id)
        ids_to_filter = [document_id for document_id, topics in document_topics_dict.items() if len(topics) == 2]
        std = std.filter("terms", document_es_id=ids_to_filter)
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
