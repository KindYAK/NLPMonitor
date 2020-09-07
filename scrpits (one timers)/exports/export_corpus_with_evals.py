import csv
from collections import defaultdict

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_DOCUMENT_EVAL, ES_INDEX_TOPIC_DOCUMENT
from evaluation.models import EvalCriterion

from elasticsearch_dsl import Search

tm_name = "bigartm_hate"
corpus = ["hate_hate", "hate_offensive", "hate_neither", "hate_test"]
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

# Document_topic_dict
document_topic_dict = defaultdict(lambda: defaultdict(float))
s = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{tm_name}").source(("topic_weight", "topic_id", "document_es_id"))
total = s.count()
for i, td in enumerate(s.scan()):
    if i % 10000 == 0:
        print(f"{i}/{total} processed")
    document_topic_dict[td.document_es_id][td.topic_id] = td.topic_weight

number_of_topics = 100

s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
s = s.filter("terms", corpus=corpus)
s = s.filter("exists", field="text_ngramized_en_lemminflect")
s = s.source(("text_ngramized_en_lemminflect", "class_label", "corpus"))

output = []
skipped = 0
for doc in s.scan():
    new_line = {
        "document_es_id": doc.meta.id,
        "ground_truth": doc.class_label,
        "text": doc.text_ngramized_en_lemminflect,
        "corpus": doc.corpus,
    }
    for criterion_id in criterion_ids:
        if doc.meta.id not in criterion_dicts[criterion_id]:
            skipped += 1
            new_line[criterion_names[criterion_id]] = 0
            continue
        new_line[criterion_names[criterion_id]] = criterion_dicts[criterion_id][doc.meta.id]
    for i in range(number_of_topics):
        new_line[f"topic_{i}"] = document_topic_dict[doc.meta.id][f"topic_{i}"]
    output.append(new_line)

print("Skipped", skipped)

output = list(filter(lambda x: not all([x[f"topic_{i}"] == 0 for i in range(100)]), output))

keys = output[0].keys()
with open(f'/output_hate_full.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
