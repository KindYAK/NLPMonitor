
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from time import sleep
from django.conf import settings
from . import shards_mapping, get_mapping, SETTINGS_BODY

es = settings.ES_CLIENT


class Command(BaseCommand):

    def wr(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))
    
    def er(self, msg):
        self.stdout.write(self.style.ERROR(msg))

    def handle(self, *args, **options):
        self.wr('---- started')
        self.list_of_indexes_and_shards_delete()
        self.wr('---- finished')

    def list_of_indexes_and_shards_delete(self):
        result = es.cat.indices(format='json')
        self.wr('Indexes')
        self.wr(result)
        indexes = {}

        for i in result:
            indexes[i['index']] = (i['pri'], i['rep'], i['docs.count'])

        for key, (pri, rep, docs_count) in indexes.items():
            if key.startswith('temp_'):
                old_index_name = key[len('temp_'):]

                if not es.indices.exists(old_index_name):
                    self.er(f"{old_index_name} does not exists")
                    continue

                es.indices.delete(index=old_index_name)
                
                if docs_count is None:
                    self.er(f"{key} index docs_count is None")
                    continue

                SETTINGS_BODY["settings"]["number_of_shards"] = shards_mapping(docs_count)
                SETTINGS_BODY["mappings"] = get_mapping(key)
                r = es.indices.create(index=old_index_name, body=SETTINGS_BODY)
        
                task = es.reindex(
                    body={
                        'source': {
                            'index': key
                        },
                        'dest': {
                            'index': old_index_name
                        }
                    },
                    timeout='5m',
                    scroll='30m',
                    wait_for_completion=False
                )
                self.wr(task)