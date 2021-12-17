import csv, datetime

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT

from elasticsearch_dsl import Search

corpus = ["main"]

s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
s = s.filter("terms", corpus=corpus)
s = s.source(("id", "text", "title", "datetime", "url", "source", "num_views"))
output = []
skipped = 0
total = s.count()
ids_already = set()
for i, doc in enumerate(s.scan()):
    if i % 100_000 == 0:
        print(f"{i}/{total}", datetime.datetime.now())
    if doc.id in ids_already:
        continue
    ids_already.add(doc.id)
    new_line = {
        "id": doc.id,
        "text": doc.text,
        "title": doc.title,
        "datetime": doc.datetime if hasattr(doc, "datetime") else None,
        "url": doc.url if hasattr(doc, "url") else None,
        "source": doc.source,
        "num_views": doc.num_views if hasattr(doc, "num_views") else None,
    }
    output.append(new_line)

keys = output[0].keys()
batch_len = 250_000
for i in range(len(output) // batch_len + (0 if len(output) % batch_len == 0 else 1)):
    print("!!!", i * batch_len, min((i + 1) * batch_len, len(output)))
    batch = output[i * batch_len:(i + 1) * batch_len]
    with open(f'/output/output_2021_dec{i * batch_len}-{min((i + 1) * batch_len, len(output))}.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(batch)


keys = output[0].keys()
with open(f'/output_2021_dec.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
