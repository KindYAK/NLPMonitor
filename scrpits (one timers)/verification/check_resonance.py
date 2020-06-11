from elasticsearch_dsl import Search

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT_EVAL, ES_INDEX_DOCUMENT

from sklearn.metrics import classification_report

tm_name = "bigartm_two_years_old_parse"
criterion_id = 35

s = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{tm_name}_{criterion_id}")
s = s.source(('value', 'document_es_id'))

# Values
document_values = dict((h.document_es_id, h.value) for h in s.scan())

# Resonance thresholds
std = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT}") \
          .filter("range", num_views={"gt": 0})
std.aggs.bucket("sources", agg_type="terms", field="source", size=100) \
    .metric("stats", agg_type="extended_stats", field="num_views")
r = std.execute()

source_resonances = dict(
    (bucket.key, bucket.stats) for bucket in r.aggregations.sources.buckets
)
source_resonance_means = dict(((source, stats.avg) for source, stats in source_resonances.items()))
source_resonance_stds = dict(((source, stats.std_deviation) for source, stats in source_resonances.items()))
sigma_threshold = 1
source_resonance_thresholds = dict(((source, source_resonance_means[source] + sigma_threshold * source_resonance_stds[source]) for source in source_resonances.keys()))

# Ground truth
document_ground_truth = dict()
total = len(document_values.keys())
for i, document_es_id in enumerate(document_values.keys()):
    if i % 1000 == 0:
        print(i, total)
    try:
        d = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter("term", _id=document_es_id).source(('num_views', 'source')).execute()[0]
    except:
        continue
    if getattr(d, 'num_views', False):
        document_ground_truth[document_es_id] = d.num_views >= source_resonance_thresholds[d.source]

# Dataset to verify
x_y = []
for document_es_id in document_values:
    if document_es_id not in document_ground_truth:
        continue
    # if 0.2 < document_values[document_es_id] < 0.7:
    #     continue
    x_y.append((document_values[document_es_id], document_ground_truth[document_es_id]))

x, y = [], []
for a, b in x_y:
    x.append(bool(round(a)))
    y.append(b)

# Verification
print(classification_report(x, y))
