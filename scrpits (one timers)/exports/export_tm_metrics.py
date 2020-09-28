import csv

from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_MODELLING

output = []
for i in range(10, 301, 10):
    tm_name = f"bigartm_two_years_{i}"
    try:
        tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=tm_name).execute()[0]
    except:
        try:
            tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", **{"name.keyword": tm_name}).execute()[0]
        except:
            continue
    output.append({
        'tm_name': tm_name,
        'number_of_topics': tm.number_of_topics,
        'purity': tm.purity,
        'contrast': tm.contrast,
        'coherence': tm.coherence,
        'perplexity': tm.perplexity,
    })

keys = output[0].keys()
with open(f'/metrics.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(output)
