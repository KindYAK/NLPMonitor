import csv
from collections import defaultdict

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_TOPIC_DOCUMENT

from elasticsearch_dsl import Search

from topicmodelling.services import calc_topics_resonance

tm_name = "bigartm_2020_2022_rus_kaz_health_2"
try:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=tm_name).execute()[0]
except:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", **{"name.keyword": tm_name}).execute()[0]

std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_name}")[:0]
std.aggs.bucket(name='topics', agg_type="terms", field='topic_id', size=500) \
            .metric("topic_weight", agg_type="sum", field="topic_weight")
std.aggs['topics'].bucket(name="corpus", agg_type="terms", field="document_corpus", size=10000) \
            .metric("topic_weight", agg_type="sum", field="topic_weight")
r = std.execute()

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
        ),
    }) for bucket in r.aggregations.topics.buckets
)
corpuses = set()
for bucket in topic_info_dict.values():
    for key in bucket['corpus_weights']:
        corpuses.add(key)

if corpuses:
    corpus_total_weights = defaultdict(int)
    for key in topic_info_dict.keys():
        if not topic_info_dict[key]["corpus_weights"]:
            continue
        for key, value in topic_info_dict[key]["corpus_weights"].items():
            corpus_total_weights[key] += value['weight_sum']
    for key in topic_info_dict.keys():
        if not topic_info_dict[key]["corpus_weights"]:
            continue
        total_weight = 0
        for corpus in corpuses:
            if corpus in topic_info_dict[key]["corpus_weights"]:
                topic_info_dict[key]["corpus_weights"][corpus]['weight_sum'] /= corpus_total_weights[corpus]
                total_weight += topic_info_dict[key]["corpus_weights"][corpus]['weight_sum']
        for corpus in corpuses:
            if corpus in topic_info_dict[key]["corpus_weights"]:
                topic_info_dict[key]["corpus_weights"][corpus]['weight_sum'] /= total_weight

topics = tm.topics
calc_topics_resonance(topics, tm_name)

output = []
for topic in topics:
    if topic.id not in topic_info_dict:
        continue
    words = list(sorted(topic.topic_words, key=lambda x: x.weight, reverse=True))[:30]
    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_name}") \
        .filter("term", topic_id=topic.id).sort('-topic_weight')[:25]
    top_news_ids = [r.document_es_id for r in std.execute()]
    s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter("terms", _id=top_news_ids).source(('title', 'url', ))[:25]
    top_news = s.execute()
    top_news_to_write = []
    titles_seen = set()
    news_to_export = 7
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
    doc = defaultdict(int)
    doc.update({
        "id": topic.id,
        "words": ", ".join([word.word for word in words]),
        "volume": topic_info_dict[topic.id]['count'] if topic.id in topic_info_dict else "-",
        "weight": topic_info_dict[topic.id]['weight_sum'] if topic.id in topic_info_dict else "-",
        "resonance": topic.high_resonance_score,
    })
    # Top news
    for i in range(news_to_export):
        if i >= len(top_news_to_write):
            doc[f"top_new_{i}_title"] = ""
            doc[f"top_new_{i}_url"] = ""
        else:
            doc[f"top_new_{i}_title"] = top_news_to_write[i].title
            doc[f"top_new_{i}_url"] = top_news_to_write[i].url if hasattr(top_news_to_write[i], 'url') else ""
    # Multi corpus
    corpus_weights = topic_info_dict[topic.id]['corpus_weights']
    if corpus_weights:
        for corpus in corpuses:
            doc[f"corpus_weight_{corpus}"] = corpus_weights[corpus]['weight_sum'] if corpus in corpus_weights else 0
    output.append(doc)

keys = output[0].keys()
with open(f'/{tm_name}.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
