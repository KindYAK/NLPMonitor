from time import sleep

from django.conf import settings
from django.core.management.base import BaseCommand

es = settings.ES_CLIENT


def shards_mapping(doc_count: int) -> int:
    if isinstance(doc_count, str):
        doc_count = int(doc_count)

    if doc_count > 10_000_000:
        return 5
    elif doc_count > 1_000_000:
        return 3
    elif doc_count > 100_000:
        return 2
    else:
        return 1


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

    def first_check(self):
        # ignore 400 cause by IndexAlreadyExistsException when creating an index
        r = es.indices.create(index='test-index', ignore=400)
        assert r['acknowledged'] == True
        sleep(1)
        r = es.indices.delete(index='test-index')
        assert r['acknowledged'] == True 
        # only wait for 1 second, regardless of the client's default
        r = es.cluster.health(wait_for_status='green', request_timeout=1)
        assert r['timed_out'] == False

        print('-> Elasticsearch communication is successful 😃')

        for key, value in r.items():
            print(f'\t- {key}: {value}')

    def list_of_indexes_and_shards(self, search_pattern: str):

        settings = {
            "settings": {
                "number_of_shards": None,
                "number_of_replicas": 1
            }
        }

        result = es.cat.indices(format='json')
        self.wr('Indexes')
        self.wr(result)
        indexes = {}
        for i in result:
            indexes[i['index']] = (i['pri'], i['rep'], i['docs.count'])

        for key, (pri, rep, docs_count) in indexes.items():
            if key.startswith(search_pattern):
                new_index = 'temp_' + key
                # sometimes indexes name is cached
                if docs_count is None:
                    continue
                # just in case
                if es.indices.exists('temp_' + new_index):
                    es.indices.delete(index='temp_' + new_index)
                    continue

                if es.indices.exists(new_index):
                    es.indices.delete(index=new_index)

                settings["settings"]["number_of_shards"] = shards_mapping(docs_count)

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
