import csv
import itertools
import numpy as np

from collections import defaultdict

from elasticsearch_dsl import Search
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_MODELLING

# #################### INIT ##########################################
def geometrical_mean(data):
    a = np.log(data)
    return np.exp(a.sum() / len(a))

topic_modelling = "bigartm_two_years"
topic_weight_threshold = 0.05
try:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=topic_modelling).execute()[0]
except:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", **{"name.keyword": topic_modelling}).execute()[0]

std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}")[:0]
std.aggs.bucket(name='topics', agg_type="terms", field='topic_id', size=500) \
            .metric("topic_weight", agg_type="sum", field="topic_weight")
r = std.execute()

topic_words_dict = dict(
    (t.id,
     {
         "words": t.topic_words
     }
     ) for t in tm.topics
)

topic_info_dict = dict(
    (bucket.key, {
        "count": bucket.doc_count,
        "weight_sum": bucket.topic_weight.value,
    }) for bucket in r.aggregations.topics.buckets
)

for topic_id in topic_info_dict.keys():
    topic_words = topic_words_dict[topic_id]['words']
    topic_info_dict[topic_id]['words'] = list(sorted(topic_words, key=lambda x: x.weight, reverse=True))[:30]

# #################### COMBINATIONS ##########################################
std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
    .filter("range", topic_weight={"gte": topic_weight_threshold}).source(('topic_id', 'document_es_id'))
n = std.count()

topic_docs_dict = defaultdict(set)
overall_docs = set()
overall_topic_ids = set()
for i, td in enumerate(std.scan()):
    topic_docs_dict[td.topic_id].add(td.document_es_id)
    overall_docs.add(td.document_es_id)
    overall_topic_ids.add(td.topic_id)
    if i % 10000 == 0:
        print(f"{i}/{n} processed")

topic_combinations = []
# average_topic_len = sum((len(docs) for docs in topic_docs_dict.values())) / len(topic_docs_dict.keys())
# average_topic_len = geometrical_mean([len(docs) for docs in topic_docs_dict.values()])
MAX_L = 3
MIN_VOLUME = 1 / len(overall_topic_ids)
average_topic_len = len(overall_docs) * MIN_VOLUME
for L in range(2, MAX_L + 1):
    print(f"L = {L}")
    for topics in itertools.combinations(topic_docs_dict.items(), L):
        if L >= 3 and not any(any(topic_id in c['topics'] for c in topic_combinations) for topic_id, _ in topics):
            continue
        common_docs = None
        topic_ids = set()
        for topic_id, docs in topics:
            if common_docs is None:
                common_docs = set(docs)
            else:
                common_docs = common_docs.intersection(docs)
            topic_ids.add(topic_id)
        if len(common_docs) > average_topic_len / L:
            topic_combinations.append(
                {
                    "topics": topic_ids,
                    "common_docs": common_docs,
                }
            )
            if len(topic_combinations) % 100 == 0:
                print(f"{len(topic_combinations)} in list")

# #################### OUTPUT ##########################################
output = []
for topic_combo in topic_combinations:
    topics = list(topic_combo['topics'])
    if any(topic not in topic_info_dict for topic in topics):
        continue
    doc = defaultdict(int)
    doc.update({
        "volume": len(topic_combo['common_docs'])
    })
    # Topics in combo
    for i in range(MAX_L):
        if i >= len(topics):
            doc[f"topic_{i}_id"] = ""
            doc[f"topic_{i}_words"] = ""
        else:
            doc[f"topic_{i}_id"] = topics[i]
            doc[f"topic_{i}_words"] = ", ".join([word['word'] for word in topic_info_dict[topics[i]]['words']])
    # Top news
    news_to_export = 5
    s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
            .filter("terms", _id=list(topic_combo['common_docs'])) \
            .source(('title', 'url',))[:news_to_export*5]
    top_news = s.execute()
    top_news_to_write = []
    titles_seen = set()
    for news in top_news:
        title = news.title.strip()
        if len(title) < 3:
            continue
        if title in titles_seen:
            continue
        top_news_to_write.append(news)
        titles_seen.add(title)
        if len(top_news_to_write) >= news_to_export:
            break
    for i in range(news_to_export):
        if i >= len(top_news_to_write):
            doc[f"top_new_{i}_title"] = ""
            doc[f"top_new_{i}_url"] = ""
        else:
            doc[f"top_new_{i}_title"] = top_news_to_write[i].title
            doc[f"top_new_{i}_url"] = top_news_to_write[i].url if hasattr(top_news_to_write[i], 'url') else ""
    output.append(doc)

keys = output[0].keys()
with open(f'/{topic_modelling}.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
