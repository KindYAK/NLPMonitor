import datetime
import random
import pandas as pd
import pickle

from elasticsearch_dsl import Search
from scipy.stats import pearsonr

from mainapp.services import apply_fir_filter
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_TOPIC_MODELLING

topic_modelling = "bigartm_2020_2022_rus_kaz_health_2"
topic_weight_threshold = 0.05
granularity = "1d"
smooth = True
datetime_from = datetime.datetime(2020, 3, 13) # Kaz
# datetime_from = datetime.datetime(2020, 1, 31) # Rus
datetime_to = datetime.datetime(2022, 2, 23) # Add One
corpus = ["main"]
# corpus = ["rus", "rus_propaganda"]
country = "Kazakhstan"
# country = "Russia"
fields = [
    "new_cases_smoothed",
    "new_deaths_smoothed",
    "reproduction_rate",
    "new_tests",
    "positive_rate",
    "tests_per_case",
    "stringency_index",
]


def get_total_metrics(granularity, topic_weight_threshold):
    std_total = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
        .filter("range", topic_weight={"gte": topic_weight_threshold}) \
        .filter("range", datetime={"gte": datetime_from}) \
        .filter("range", datetime={"lte": datetime_to}) \
        .filter("terms", document_corpus=corpus)
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
              .filter("terms", document_corpus=corpus) \
              .filter("range", topic_weight={"gte": topic_weight_threshold}) \
              .filter("range", datetime={"gte": datetime_from}) \
              .filter("range", datetime={"lte": datetime_to}) \
              .source(['document_es_id', 'topic_weight'])[:1000000]
    std.aggs.bucket(name="dynamics",
                    agg_type="date_histogram",
                    field="datetime",
                    calendar_interval=granularity) \
        .metric("dynamics_weight", agg_type="sum", field="topic_weight")
    std.aggs.bucket(name="source", agg_type="terms", field="document_source") \
        .metric("source_weight", agg_type="sum", field="topic_weight")
    topic_documents = std.execute()
    return topic_documents


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
    print("! Start")
    s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
        .filter("range", topic_weight={"gte": topic_weight_threshold}) \
        .filter("range", datetime={"gte": datetime_from}) \
        .filter("range", datetime={"lte": datetime_to}) \
        .filter("terms", document_corpus=corpus)
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
        "details": get_topic_details(topic.id)
    }) for topic in topics)


def get_topic_details(topic_id):
    print("! Topic details", topic_id)
    # Total metrics
    total_metrics_dict = get_total_metrics(granularity, topic_weight_threshold)
    # Current topic metrics
    topic_documents = get_current_topics_metrics([topic_id], granularity, topic_weight_threshold)
    # Normalize
    normalize_topic_documnets(topic_documents, total_metrics_dict)
    # Separate signals
    # absolute_power = [bucket.doc_count for bucket in topic_documents.aggregations.dynamics.buckets]
    # relative_power = [bucket.doc_count_normal for bucket in topic_documents.aggregations.dynamics.buckets]
    relative_weight = [bucket.dynamics_weight.value for bucket in topic_documents.aggregations.dynamics.buckets]
    # Smooth
    if smooth:
        # absolute_power = apply_fir_filter(absolute_power, granularity=granularity)
        # relative_power = apply_fir_filter(relative_power, granularity=granularity)
        relative_weight = apply_fir_filter(relative_weight, granularity=granularity)
    # Create context
    topic_info = {}
    topic_info['date_ticks'] = [bucket.key_as_string for bucket in topic_documents.aggregations.dynamics.buckets]
    # topic_info['absolute_power'] = absolute_power
    # topic_info['relative_power'] = relative_power
    topic_info['relative_weight'] = relative_weight
    topic_info['source_weight'] = sorted([bucket.to_dict() for bucket in topic_documents.aggregations.source.buckets],
                                         key=lambda x: x['source_weight']['value'],
                                         reverse=True)
    # topic_info['topic_info'] = topics_info[topic_id]
    return topic_info


topics_info = get_topics_info()

df = pd.read_excel("/owid-covid-data.xlsx")
df = df[df.location == country].fillna(0)
correlations = []
for field in fields:
    print("!", field)
    # correlations = []
    for topic in topics_info.keys():
        topic_dynamics = topics_info[topic]['details']['relative_weight']
        if len(topic_dynamics) < len(df[field]):
            diff = len(df[field]) - len(topic_dynamics)
            topic_dynamics = [0] * diff + list(topic_dynamics)
            if diff > 10:
                continue
            print("!DIFF", diff)
        try:
            correlations.append(
                {
                    "field": field,
                    "corr": pearsonr(topic_dynamics, df[field])[0],
                    "topic_id": topic,
                    "words": ", ".join([w['word'] for w in topics_info[topic]['words'][:7]]),
                    "size": topics_info[topic]['size'],
                }
            )
        except:
            print("SAD :(")
            correlations.append(
                {
                    "field": field,
                    "corr": random.random(),
                    "topic_id": topic,
                    "words": ", ".join([w['word'] for w in topics_info[topic]['words'][:7]]),
                    "size": topics_info[topic]['size'],
                }
            )
            continue
    top = sorted(correlations, key=lambda x: x['corr'], reverse=True)[0]
    topic_dynamics = topics_info[top['topic_id']]['details']['relative_weight']
    print("!!!!!!!!!!!!!!! TOP!!!!!!!!!!!!!", len(topic_dynamics))
    if len(topic_dynamics) < len(df[field]):
        diff = len(df[field]) - len(topic_dynamics)
        topic_dynamics = [0] * diff + list(topic_dynamics)
    pickle.dump({
        "covid": df[field],
        "topic": topic_dynamics,
        "words": top['words'],
    }, open(f"/export/topic_{field}.pkl", "wb"))
    # with open(f"/covid/{country}-{topic_modelling}-{field}-top.txt", "w") as f:
    #     for corr in sorted(correlations, key=lambda x: x['corr'], reverse=True)[:25]:
    #         f.write(f"{corr['corr']} - {corr['topic_id']} - {corr['words']} ({corr['size']} documents)\n")
    # with open(f"/covid/{country}-{topic_modelling}-{field}-bottom.txt", "w") as f:
    #     for corr in sorted(correlations, key=lambda x: x['corr'], reverse=False)[:25]:
    #         f.write(f"{corr['corr']} - {corr['topic_id']} - {corr['words']} ({corr['size']} documents)\n")


pd.DataFrame(correlations).to_json("/corr_mat_tm.json")