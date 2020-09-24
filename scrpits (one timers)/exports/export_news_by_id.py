import csv

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_DOCUMENT_EVAL, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_TOPIC_MODELLING

from elasticsearch_dsl import Search

tm_name = "bigartm_two_years_main_and_gos2"
criterion_id = 37 # Соц (опросы)
ids_list = """
1481052
152220
15697638
"""
ids_list = [s.strip() for s in ids_list.split() if s.strip()]

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

try:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=tm_name).execute()[0]
except:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", **{"name.keyword": tm_name}).execute()[0]

tm_name_dict = dict(
    (topic.id, topic.name) for topic in tm.topics
)

output = []
for document_id in ids_list:
    s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter("term", id=int(document_id)).source(("id", "title", "url", "datetime"))[:1]
    doc = s.execute()[0]
    new_line = {
        "id": doc.id,
        "title": doc.title,
        "url": getattr(doc, 'url', None),
        "datetime": getattr(doc, 'datetime', None),
    }
    s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{tm_name}_{criterion_id}").filter("term", document_es_id=doc.meta.id).source(('value', ))[:1]
    try:
        eval = s.execute()[0]
        new_line['value'] = eval.value
    except:
        print("!!!!!! SKIP Eval ", doc.id, "!", hasattr(doc, "datetime"), hasattr(doc, "text_lemmatized"))
        continue
    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_name}")
    std = std.filter("term", document_es_id=doc.meta.id)
    std = std.sort('-topic_weight')[:500]
    topic_docs = std.execute()
    try:
        for i in range(5):
            new_line[f'topic_{i}'] = tm_name_dict[topic_docs[i]['topic_id']]
            new_line[f'weight_{i}'] = topic_info_dict[topic_docs[i]['topic_id']]['weight_sum']
            new_line[f'count_{i}'] = topic_info_dict[topic_docs[i]['topic_id']]['count']
    except:
        print("!!!!!! SKIP TM", doc.id)
    output.append(new_line)

keys = output[0].keys()
with open(f'/output_survey.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
