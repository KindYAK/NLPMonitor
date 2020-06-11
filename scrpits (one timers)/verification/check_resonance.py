from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT_EVAL

tm_name = "bigartm_two_years"
criterion_id = 35

s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{tm_name}_{criterion_id}")
s = s.source(('value', 'num_views'))

x_y = ((h.value, h.num_views) for h in s.scan())

