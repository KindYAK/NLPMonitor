import csv
from collections import defaultdict

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_TOPIC_DOCUMENT

from elasticsearch_dsl import Search

tm_name = "bigartm_two_years"
try:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=tm_name).execute()[0]
except:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", **{"name.keyword": tm_name}).execute()[0]

for topic in tm.topics:
    name = ", ".join([w.word for w in list(sorted(topic.topic_words, key=lambda x: x.weight, reverse=True))[:10]])
    print("!!!", name)
    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_name}") \
        .filter("term", topic_id=topic.id).sort('-topic_weight')[:1000]
    top_news_ids = [r.document_es_id for r in std.execute()]
    s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter("terms", _id=top_news_ids).filter("exists", field="url").source(('title', 'url', 'datetime', 'id'))[:1000]
    top_news = s.execute()
    top_news_to_write = []
    titles_seen = set()
    news_to_export = 7
    output = []
    for news in top_news:
        title = news.title.strip()
        if len(title) < 3:
            continue
        if title in titles_seen:
            continue
        if len(output) >= 500:
            break
        titles_seen.add(title)
        output.append(
            {
                "id": news.id,
                "datetime": news.datetime,
                "title": news.title,
                "url": news.url,
            }
        )
    keys = output[0].keys()
    with open(f'/exports/{name}.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(output)
