
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from time import sleep
from django.conf import settings

es = settings.ES_CLIENT


class Command(BaseCommand):

    def wr(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))
    
    def er(self, msg):
        self.stdout.write(self.style.ERROR(msg))

    def handle(self, *args, **options):
        self.wr('---- started')
        self.remove_old()
        self.wr('---- finished')

    def remove_old(self):
        result = es.cat.indices(format='json')
        self.wr('Indexes')
        self.wr(result)
        indexes = {}

        for i in result:
            indexes[i['index']] = (i['pri'], i['rep'], i['docs.count'])

        for key, (pri, rep, docs_count) in indexes.items():
            if key.startswith('temp_'):
                es.indices.delete(index=key)
