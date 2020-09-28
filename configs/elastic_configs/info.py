from elasticsearch import Elasticsearch
from time import sleep
es = Elasticsearch()


def first_check():
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
    



def run():
    first_check()


if __name__ == "__main__":
    run()
