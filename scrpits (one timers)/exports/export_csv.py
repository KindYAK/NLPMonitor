import csv
import datetime
from collections import defaultdict

from mainapp.models import Document
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_DOCUMENT_EVAL, ES_INDEX_TOPIC_DOCUMENT


def generate_batches(iterable, size=1_000_000):
    l = len(iterable)
    for ndx in range(0, l, size):
        yield iterable[ndx:min(ndx + size, l)]


for batch_n, batch in enumerate(
        generate_batches(Document.objects.filter(source__corpus__id=1).order_by('id'), size=1_000_000)
    ):
    if batch_n % 10 == 0 or batch_n < 10:
        print(batch_n)
    output = [
        {
            "id": document.id,
            "datetime": document.datetime,
            "title": document.title,
            "source": document.source.name,
            "url": document.url,
            "html": document.html,
            "text": document.text,
        } for document in batch
    ]
    keys = output[0].keys()
    with open(f'/output_{batch_n}.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(output)
