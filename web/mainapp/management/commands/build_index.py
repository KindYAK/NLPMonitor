from django.core.management.base import BaseCommand
from elasticsearch.helpers import streaming_bulk

from mainapp.models import *
from mainapp.documents import Document as ESDocument
from mainapp.services import batch_qs
import elasticsearch_dsl as es
from nlpmonitor.settings import ES_INDEX, ES_CLIENT


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.batch_size = 50000
        ESDocument.init()
        self.parse_csv()

    def document_generator(self, qs):
        for batch in batch_qs(qs, batch_size=self.batch_size):
            for document in batch:
                obj = ESDocument()
                obj.init_from_model(document)
                yield obj.to_dict()

    def parse_csv(self):
        success = 0
        failed = 0
        qs = Document.objects.all()
        for ok, result in streaming_bulk(ES_CLIENT, self.document_generator(qs), index=ES_INDEX, chunk_size=self.batch_size, raise_on_error=False):
            if ok:
                success += 1
            else:
                failed += 1
                action, result = result.popitem()
                print("!!!", action, result)

            if (success + failed) % self.batch_size == 0:
                print(f'{success+failed}/{qs.count()} processed')
