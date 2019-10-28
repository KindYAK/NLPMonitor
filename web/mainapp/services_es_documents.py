from elasticsearch_dsl import Search, Q
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT


TERM_FIELDS = (('corpuses', 'corpus'),
               ('sources', 'source'),
               ('authors', 'author'),
               ('tags', 'tags'),
               ('categories', 'categories'),)
TERMS_FIELDS_DICT = dict(TERM_FIELDS)
MATCH_FIELDS = ('title', 'id')
MULTI_FIELDS = ('text', )
RANGE_FROM_FIELDS = ('datetime_from', 'num_views_from', 'num_shares_from', 'num_comments_from', 'num_likes_from',)
RANGE_TO_FIELDS = ('datetime_to', 'num_views_to', 'num_shares_to', 'num_comments_to', 'num_likes_to',)

SOURCE_FIELDS = ('id', 'datetime', 'title', 'source', )


def es_filter(search, key, value):
    query = 'terms'
    value = list([v.name for v in value])
    key = TERMS_FIELDS_DICT[key]
    return search.filter(query, **{key: value})


def execute_search(search_request, return_search_obj=False):
    s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
    s = s.source(include=SOURCE_FIELDS)

    for key, value in search_request.items():
        if not value:
            continue
        if key in TERMS_FIELDS_DICT:
            s = es_filter(s, key, value)
        elif key in MATCH_FIELDS:
            s = s.query('match', **{key: value})
        elif key in MULTI_FIELDS:
            if isinstance(value, list):
                value = value[0]
            q = Q('multi_match',
                  query=value,
                  fields=['title^10',
                          'tags^3',
                          'categories^3',
                          'text^2'])
            s = s.query(q)
        elif key in RANGE_TO_FIELDS:
            s = s.filter('range', **{key.replace("_to", ""): {'lte': value}})
        elif key in RANGE_FROM_FIELDS:
            s = s.filter('range', **{key.replace("_from", ""): {'gte': value}})

    if return_search_obj:
        return s
    s = s[:1000]
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
