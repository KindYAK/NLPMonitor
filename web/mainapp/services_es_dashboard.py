from elasticsearch_dsl import Search
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DASHOBARD
from .dashboard_types import *
from .documents import *


SOURCE_FIELDS = ('values', 'datetime_generated', 'tag', )


def get_dashboard(search_request):
    s = Search(using=ES_CLIENT, index=ES_INDEX_DASHOBARD)
    s = s.source(include=SOURCE_FIELDS)
    s = s.filter("term", **{"type": search_request['type']})
    s = s.filter("term", **{"is_ready": True})
    for key, value in search_request.items():
        if not value:
            continue
        if key == "tags":
            s = s.filter("terms", **{"tag": [v.name for v in value]})
        elif key in ["corpus"]:
            s = s.filter("term", **{key: value.name})

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


def get_kibana_dashboards():
    s = Search(using=ES_CLIENT, index='.kibana')
    s = s.filter("term", **{"type": "dashboard"})
    s = s.execute()

    esresult = s.to_dict()

    response = dict()

    response = [
        {
            'id': l['_id'].split(":")[1],
            'title': l['_source']['dashboard']['title']
        } for l in esresult['hits']['hits']
    ]
    # NOTE: Added first element as `null dashboard`
    # This dashboard does not contain anything
    form_response = [('', '-')] + [
        (p['id'], p['title']) for p in response
    ]

    return form_response
