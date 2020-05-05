import csv
import datetime
import json

from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_DOCUMENT_EVAL

corpus = ["rus", "rus_propaganda"]
datetime_from = datetime.datetime(2018, 1, 1)
res = ES_CLIENT.search(index=ES_INDEX_DOCUMENT, size=2000, body={
    "query": {
        "function_score": {
            "functions": [
                {
                    "random_score": {
                        "seed": "294j5bw[oamvrin"
                    }
                }
            ],
            "query": {
                "bool": {
                    "must": [
                        {
                            "terms": {
                                "corpus": corpus
                            },
                        },
                        {
                            "range": {
                                "datetime": {
                                    "gte": datetime_from
                                }
                            }
                        }
                    ]
                }
            },
        }
    }
})

tm = "bigartm_two_years_rus_and_rus_propaganda"
criterion_id = 32

s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{tm}_{criterion_id}")
s = s.filter('terms', document_es_id=[hit['_id'] for hit in res['hits']['hits']])
s = s.source(('document_es_id', 'value', ))

document_eval_dict = dict(
    (hit.document_es_id, hit.value) for hit in s.scan()
)

output = []
for hit in res['hits']['hits']:
    if hit['_id'] not in document_eval_dict:
        continue
    output.append(
        {
            "id": hit['_source']['id'],
            "title": hit['_source']['title'],
            "datetime": hit['_source']['datetime'],
            "source": hit['_source']['source'],
            "url": hit['_source']['url'] if 'url' in hit['_source'] else "",
            "value": document_eval_dict[hit['_id']],
        }
    )

# with open("/output_propa.json", "w", encoding="utf-8") as f:
#     f.write(json.dumps(output))

keys = output[0].keys()
with open(f'/output.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
