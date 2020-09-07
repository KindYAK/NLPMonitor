import csv

from elasticsearch_dsl import Search, Q

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_DOCUMENT_EVAL

tm = "bigartm_two_years_main_and_gos2"
name = "social"
corpus = "main"
criterion_id = "34_m4a" # 34 - соц значимость, 35 - резонансность, 1 - тональность, 36 - целевой класс
low_threshold = 10
high_threshold = 90

s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{tm}_{criterion_id}")[:0]
s.aggs.metric("percents", agg_type="percentiles", field="value", percents=[low_threshold, high_threshold])
# s.aggs.metric("percents", agg_type="percentiles", field="value", percents=[i for i in range(0, 105, 5)])
r = s.execute()

# for b in r.aggregations.percents.values:
#     print(b, r.aggregations.percents.values[b])

s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{tm}_{criterion_id}")
q1 = Q("range", value={
    "gt": r.aggregations.percents.values[f'{high_threshold}.0'],
})
q2 = Q("range", value={
    "lt": r.aggregations.percents.values[f'{low_threshold}.0'],
})
s = s.query(q1 | q2)
s = s.query({
    "function_score": {
        "functions": [
            {
                "random_score": {
                    "seed": "iivtiicthelyon1488"
                }
            }
        ],
    }
})
s = s.source(('document_es_id', 'value'))[:2000]
r = s.execute()

document_eval_dict = dict(
    (hit.document_es_id, hit.value) for hit in r
)

s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
s = s.filter("terms", _id=list(document_eval_dict.keys()))
s = s.filter("term", corpus=corpus)
s = s.source(("id", "title", "datetime", "source", "url", "value"))

output = []
seen_ids = set()
seen_titles = set()
for hit in s.scan():
    if len(output) >= 1000:
        break
    if hit.id in seen_ids:
        continue
    if hit.title in seen_titles:
        continue
    if hit.meta.id not in document_eval_dict:
        continue
    output.append(
        {
            "id": hit.id,
            "title": hit.title,
            "datetime": getattr(hit, 'datetime', ""),
            "source": hit.source,
            "url": getattr(hit, "url", ""),
            "value": document_eval_dict[hit.meta.id],
        }
    )
    seen_ids.add(output[-1]["id"])
    seen_titles.add(output[-1]["title"])

keys = output[0].keys()
with open(f'/{name}.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
