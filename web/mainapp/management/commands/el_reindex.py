
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from time import sleep
from django.conf import settings
from . import shards_mapping, get_mapping, SETTINGS_BODY
es = settings.ES_CLIENT


class Command(BaseCommand):

    def wr(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))

    def add_arguments(self, parser):
        parser.add_argument(
            '--prefix',
            action='store',
            type=str,
            help='Prefix of the index name',
        )

    def handle(self, *args, **options):
        self.wr('---- started')
        self.list_of_indexes_and_shards(options['prefix'])
        self.wr('---- finished')

    def list_of_indexes_and_shards(self, search_pattern: str):
        result = es.cat.indices(format='json')
        self.wr('Indexes')
        self.wr(result)
        indexes = {}
        for i in result:
            indexes[i['index']] = (i['pri'], i['rep'], i['docs.count'])

        for key, (pri, rep, docs_count) in indexes.items():
            if key.startswith(search_pattern):
                new_index = 'temp_'+key
                # sometimes indexes name is cached
                if docs_count is None:
                    continue
                # just in case
                if es.indices.exists('temp_'+new_index):
                    es.indices.delete(index='temp_'+new_index)
                    continue

                if es.indices.exists(new_index):
                    es.indices.delete(index=new_index)

                SETTINGS_BODY["settings"]["number_of_shards"] = shards_mapping(docs_count)
                SETTINGS_BODY["mappings"] = get_mapping(key)

                r = es.indices.create(index=new_index, body=settings)
        
                task = es.reindex(
                    body={
                        'source': {
                            'index': key
                        },
                        'dest': {
                            'index': new_index
                        }
                    },
                    timeout='5m',
                    scroll='30m',
                    wait_for_completion=False
                )
                self.wr(task)