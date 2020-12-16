import csv

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT

from elasticsearch_dsl import Search

corpus = ["main", "rus", "rus_propaganda"]

s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
s = s.filter("terms", corpus=corpus)
s = s.source(("text", "title", "datetime", "url", "source", "num_views", "corpus"))
output = []
skipped = 0
total = s.count()
for i, doc in enumerate(s.scan()):
    if i % 100_000 == 0:
        print(f"{i}/{total}")
    new_line = {
        "document_es_id": doc.meta.id,
        "text": doc.text,
        "text_lemmatized": doc.text_lemmatized if hasattr(doc, "text_lemmatized") else None,
        "title": doc.title,
        "datetime": doc.datetime if hasattr(doc, "datetime") else None,
        "url": doc.url if hasattr(doc, "url") else None,
        "source": doc.source,
        "num_views": doc.num_views if hasattr(doc, "num_views") else None,
        "type": "News" if doc.corpus == "main" else "Governmental program",
    }
    output.append(new_line)

output = sorted(output, key=lambda x: x['datetime'] if x['datetime'] else "")

keys = output[0].keys()
with open(f'/output_data_kz_rus.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)


keys = output[0].keys()
batch_len = 250_000
for i in range(len(output) // batch_len + (0 if len(output) % batch_len == 0 else 1)):
    print("!!!", i * batch_len, min((i + 1) * batch_len, len(output)))
    batch = output[i * batch_len:(i + 1) * batch_len]
    with open(f'/output/output_data_kz_rus_{i * batch_len}-{min((i + 1) * batch_len, len(output))}.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(batch)
