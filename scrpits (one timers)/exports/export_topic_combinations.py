import csv

from collections import defaultdict

from elasticsearch_dsl import Search
from nlpmonitor.settings import (
    ES_CLIENT,
    ES_INDEX_TOPIC_DOCUMENT,
    ES_INDEX_DOCUMENT,
    ES_INDEX_TOPIC_MODELLING,
    ES_INDEX_TOPIC_COMBOS
)

# #################### INIT ##########################################
topic_modelling = "bigartm_education_two_years"
topic_weight_threshold = 0.05
MAX_L = 4
news_to_export = 5
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
stc = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_COMBOS}_{topic_modelling}")

# #################### OUTPUT ##########################################
output = []
for topic_combo in stc.scan():
    if any(topic not in topic_info_dict for topic in topic_combo.topic_ids):
        continue
    doc = defaultdict(int)
    doc.update({
        "volume": len(topic_combo.common_docs_ids)
    })
    # Topics in combo
    for i in range(MAX_L):
        if i >= len(topic_combo.topic_ids):
            doc[f"topic_{i}_id"] = ""
            doc[f"topic_{i}_words"] = ""
        else:
            doc[f"topic_{i}_id"] = topic_combo.topic_ids[i]
            doc[f"topic_{i}_words"] = ", ".join([word['word']
                                                 for word in topic_info_dict[topic_combo.topic_ids[i]]['words']])
    # Top news
    s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
            .filter("terms", _id=list(topic_combo.common_docs_ids)) \
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
