import pickle

from elasticsearch_dsl import Search
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_DOCUMENT

# topic_modelling = "bigartm_test"
topic_modelling = "bigartm_two_years"
topic_weight_threshold = 0.05

tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=topic_modelling).execute()[0]
topic_names = {}
for topic in tm.topics:
    topic_names[topic.id] = topic.name

with open(f'topic_names_{topic_modelling}.pickle', 'wb') as f:
    pickle.dump(topic_names, f)


std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
    .filter("range", topic_weight={"gte": topic_weight_threshold})
n = std.count()

topic_documents = {}
for i, td in enumerate(std.scan()):
    if i % 10000 == 0:
        print(f"{i}/{n} processed")
    if td.document_es_id not in topic_documents:
        d = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter("term", _id=td.document_es_id).execute()[0]
        topic_documents[td.document_es_id] = {
            "title": d.title,
            "text": d.text,
            "source": d.source,
            "datetime": d.datetime,
            "topics": [],
        }
    topic_documents[td.document_es_id]['topics'].append(
        {
            "id": td.topic_id,
            "weight": td.topic_weight,
            "name": topic_names[td.topic_id],
        }
    )

with open(f'topic_documents_{topic_modelling}.pickle', 'wb') as f:
    pickle.dump(topic_documents, f)
