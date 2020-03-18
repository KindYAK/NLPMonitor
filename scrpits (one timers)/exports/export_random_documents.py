import json

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT

res = ES_CLIENT.search(index=ES_INDEX_DOCUMENT, size=50000, body={
    "query": {
        "function_score": {
            "functions": [
                {
                    "random_score": {
                        "seed": "saoddf;oj3049uf3049uf3049fu034f"
                    }
                }
            ]
        }
    },
})

output = []
for hit in res['hits']['hits']:
    output.append(
        {
            "id": hit['_source']['id'],
            "title": hit['_source']['title'],
            "text": hit['_source']['text'],
        }
    )

with open("/output.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(output))
