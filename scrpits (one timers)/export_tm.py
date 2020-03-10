import csv

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_TOPIC_DOCUMENT

from elasticsearch_dsl import Search

tm_name = "bigartm_two_years"
try:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=tm_name).execute()[0]
except:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", **{"name.keyword": tm_name}).execute()[0]

std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_name}") \
    .filter("range", topic_weight={"gte": 0.05})[:0]
std.aggs.bucket(name='topics', agg_type="terms", field='topic_id', size=10000) \
            .metric("topic_weight", agg_type="sum", field="topic_weight")
r = std.execute()

topic_info_dict = dict(
            (bucket.key, {
                "count": bucket.doc_count,
                "weight_sum": bucket.topic_weight.value
            }) for bucket in r.aggregations.topics.buckets
        )

output = []
for topic in tm.topics:
    words = list(sorted(topic.topic_words, key=lambda x: x.weight, reverse=True))[:10]
    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_name}") \
        .filter("term", topic_id=topic.id).sort('-topic_weight')[:3]
    top_news_ids = [r.document_es_id for r in std.execute()]
    s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter("terms", _id=top_news_ids).source(('title', 'url', ))[:3]
    top_news = s.execute()
    output.append({
        "id": topic.id,
        "words": ",".join([word.word for word in words]),
        "volume": topic_info_dict[topic.id]['count'] if topic.id in topic_info_dict else "-",
        "weight": topic_info_dict[topic.id]['weight_sum'] if topic.id in topic_info_dict else "-",
        "top_new_1_title": top_news[0].title,
        "top_new_1_url": top_news[0].url if hasattr(top_news[0], 'url') else "",
        "top_new_2_title": top_news[1].title,
        "top_new_2_url": top_news[1].url if hasattr(top_news[1], 'url') else "",
        "top_new_3_title": top_news[2].title,
        "top_new_3_url": top_news[2].url if hasattr(top_news[2], 'url') else "",
    })

keys = output[0].keys()
with open(f'{tm_name}.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
