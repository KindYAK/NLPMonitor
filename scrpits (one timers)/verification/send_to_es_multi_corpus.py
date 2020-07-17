import random

from elasticsearch.helpers import parallel_bulk

from mainapp.documents import Document as ESDocument
from mainapp.models import *
from mainapp.services import batch_qs
from nlpmonitor.settings import ES_INDEX_DOCUMENT, ES_CLIENT

batch_size = 2500
corpus = "hate"
percent_test = 10


def document_generator(qs):
    for batch in batch_qs(qs, batch_size=batch_size):
        for document in batch:
            obj = ESDocument()
            obj.init_from_model(document)
            obj = obj.to_dict()
            obj['corpus'] = f"hate_{obj['class_label']}"
            if random.randint(1, 100) <= percent_test:
                obj['corpus'] = "hate_test"
            yield obj


success = 0
failed = 0
qs = Document.objects.all()
qs = qs.filter(source__corpus__name=corpus).order_by('id')
number_of_documents = qs.count()
for ok, result in parallel_bulk(ES_CLIENT, document_generator(qs), index=ES_INDEX_DOCUMENT,
                                chunk_size=batch_size, raise_on_error=False, thread_count=6):
    if ok:
        success += 1
    else:
        failed += 1
        action, result = result.popitem()
        print("!!!", action, result)

    if failed > 3:
        raise Exception("Too many failed!!")
    if (success + failed) % batch_size == 0:
        print(f'{success + failed}/{number_of_documents} processed')
