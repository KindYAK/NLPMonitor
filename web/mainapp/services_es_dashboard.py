from elasticsearch_dsl import Search, Q
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DASHOBARD
from .documents import *


SOURCE_FIELDS = ('values', 'datetime_generated', 'tag', )


def get_publications_by_tag(search_request):
    s = Search(using=ES_CLIENT, index=ES_INDEX_DASHOBARD)
    s = s.source(include=SOURCE_FIELDS)
    s = s.filter("term", **{"type": DASHBOARD_TYPE_NUM_PUBLICATIONS_BY_TAG})
    s = s.filter("term", **{"is_ready": True})
    for key, value in search_request.items():
        if not value:
            continue
        if key == "tags":
            s = s.filter("terms", **{"tag": [v.name for v in value]})

    s = s[:None]
    esresult = s.execute().to_dict()
    total_found = esresult['hits']['total']
    response = dict()
    response['size'] = total_found
    esresult = [
        {
            'source': l['_source'],
            'score': l.get('_score')
        } for l in esresult['hits']['hits']
    ]
    response['hits'] = esresult
    return response
