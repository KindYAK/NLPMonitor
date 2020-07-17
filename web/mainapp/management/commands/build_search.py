import elasticsearch_dsl as es
from django.core.management.base import BaseCommand
from elasticsearch.helpers import parallel_bulk

from mainapp.documents import Document as ESDocument
from mainapp.models import *
from mainapp.services import batch_qs
from nlpmonitor.settings import ES_INDEX_DOCUMENT, ES_CLIENT


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('batch_size', type=int)

    def handle(self, *args, **options):
        self.batch_size = options['batch_size']
        self.from_id = 0
        if "from_id" in options:
            self.from_id = options['from_id']
        self.to_id = None
        if "to_id" in options:
            self.to_id = options['to_id']
        self.client = ES_CLIENT
        if not self.from_id:
            print("Deleting index")
            index = es.Index(ES_INDEX_DOCUMENT, using=self.client)
            index.delete(ignore=404)
            print("Creating index")
            ESDocument.init()
        self.send_elastic()

    def document_generator(self, qs):
        for batch in batch_qs(qs, batch_size=self.batch_size):
            for document in batch:
                obj = ESDocument()
                obj.init_from_model(document)
                yield obj.to_dict()

    def send_elastic(self):
        success = 0
        failed = 0
        qs = Document.objects.filter(id__gt=self.from_id)
        if self.to_id:
            qs = qs.filter(id__lte=self.to_id)
        qs = qs.order_by('id')
        # import datetime
        # qs = qs.filter(datetime__gte=datetime.date(2018, 10, 1), datetime__lte=datetime.date(2018, 10, 10)).order_by('id')
        # qs = qs.filter(source__corpus__name="gos").order_by('id')
        print("Start build")
        number_of_documents = qs.count()
        for ok, result in parallel_bulk(self.client, self.document_generator(qs), index=ES_INDEX_DOCUMENT,
                                        chunk_size=self.batch_size, raise_on_error=False, thread_count=6):
            if ok:
                success += 1
            else:
                failed += 1
                action, result = result.popitem()
                print("!!!", action, result)

            if failed > 3:
                raise Exception("Too many failed!!")
            if (success + failed) % self.batch_size == 0:
                print(f'{success+failed}/{number_of_documents} processed')
