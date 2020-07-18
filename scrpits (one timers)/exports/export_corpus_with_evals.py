import csv
from collections import defaultdict

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_DOCUMENT_EVAL, ES_INDEX_TOPIC_DOCUMENT
from evaluation.models import EvalCriterion

from elasticsearch_dsl import Search

tm_name = "bigartm_hate"
# corpus = "hate"
criterion_ids = [4, 5, 6]

criterion_dicts = defaultdict(dict)
criterion_names = dict()
for criterion_id in criterion_ids:
    criterion_names[criterion_id] = EvalCriterion.objects.get(id=criterion_id).name
    s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{tm_name}_{criterion_id}")
    s = s.source(('value', 'document_es_id'))
    criterion_dicts[criterion_id] = dict(
        (doc.document_es_id, doc.value) for doc in s.scan()
    )

s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
# s = s.filter("term", corpus=corpus)
s = s.source(("text", "class_label"))

output = []
skipped = 0
for doc in s.scan():
    new_line = {
        "document_es_id": doc.meta.id,
        "ground_truth": doc.class_label,
        "text": doc.text,
    }
    for criterion_id in criterion_ids:
        if doc.meta.id not in criterion_dicts[criterion_id]:
            skipped += 1
            continue
        new_line[criterion_names[criterion_id]] = criterion_dicts[criterion_id][doc.meta.id]
    output.append(new_line)

print("Skipped", skipped)

keys = output[0].keys()
with open(f'/output_hate.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
