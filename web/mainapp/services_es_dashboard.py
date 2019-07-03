from elasticsearch_dsl import Search
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DASHOBARD


SOURCE_FIELDS = ('values', 'datetime_generated', 'tag', )


def get_publication_by_tag(tag_names, date_from=None, date_to=None):
    s = Search(using=ES_CLIENT, index=ES_INDEX_DASHOBARD)
    s = s.source(include=SOURCE_FIELDS)
    s = s.filter("terms", **{"tag": tag_names})
    if date_from:
        s = s.filter('range', **{"values.datetime": {'gte': date_from}})
    if date_to:
        s = s.filter('range', **{"values.datetime": {'lte': date_to}})

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
