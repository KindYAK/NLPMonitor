import datetime
import pandas as pd
from elasticsearch_dsl import Search

from scipy.stats import pearsonr

from evaluation.services import normalize_documents_eval_dynamics, smooth_buckets
from mainapp.models import Source
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT_EVAL

topic_modelling = "bigartm_2020_2021_rus_kaz_health_2"
criterion_id = 1
topic_weight_threshold = 0.05
granularity = "1d"
smooth = True
# datetime_from = datetime.datetime(2020, 3, 13) # Kaz
datetime_from = datetime.datetime(2020, 1, 31) # Rus
datetime_to = datetime.datetime(2021, 2, 25) # Add One
# corpus = ["main"]
corpus = ["rus", "rus_propaganda"]
# country = "Kazakhstan"
country = "Russia"
fields = [
    "new_cases_smoothed",
    "new_deaths_smoothed",
    "reproduction_rate",
    "new_tests",
    "positive_rate",
    "tests_per_case",
    "stringency_index",
]

def get_current_document_evals(topic_modelling, granularity, sources, top_news_num=5):
    # Basic search object
    std = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{topic_modelling}_{criterion_id}") \
              .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)})\
              .filter("range", document_datetime={"lte": datetime.datetime.now().date()}) \
              .source(['document_es_id']) \
              .sort('-value')
    if sources:
        std = std.filter("terms", document_source=[source for source in sources])
    # Range selection
    if datetime_from:
        std = std.filter("range", document_datetime={"gte": datetime_from})
    if datetime_to:
        std = std.filter("range", document_datetime={"lte": datetime_to})
    # Posneg distribution
    range_center = 0
    neutral_neighborhood = 0.1
    std.aggs.bucket(
        name="posneg",
        agg_type="range",
        field="value",
        ranges=
        [
            {"from": -1, "to": range_center - neutral_neighborhood},
            {"from": range_center - neutral_neighborhood, "to": range_center + neutral_neighborhood},
            {"from": range_center + neutral_neighborhood, "to": 1},
        ]
    )
    # Dynamics
    if granularity:
        # Average dynamics
        std.aggs.bucket(name="dynamics",
                        agg_type="date_histogram",
                        field="document_datetime",
                        calendar_interval=granularity) \
                .metric("dynamics_weight", agg_type="avg", field="value")
        # Positive-negative distribution
        # Positive/negative dynamics
        std.aggs['posneg'].bucket(name="dynamics",
                                  agg_type="date_histogram",
                                  field="document_datetime",
                                  calendar_interval=granularity) \
            .metric("dynamics_weight", agg_type="avg", field="value")
    # Execute search
    std = std[:top_news_num]
    document_evals = std.execute()
    # Top_news ids - get minimum values
    top_news = set()
    top_news.update((d.document_es_id for d in document_evals))
    std_min = Search(using=ES_CLIENT, index=f"{ES_INDEX_DOCUMENT_EVAL}_{topic_modelling}_{criterion_id}") \
              .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}).filter("range", document_datetime={"lte": datetime.datetime.now().date()}) \
              .source(['document_es_id']).sort('value')
    if sources:
        std_min = std.filter("terms", document_source=[source for source in sources])
    if datetime_from:
        std_min = std_min.filter("range", document_datetime={"gte": datetime_from})
    if datetime_to:
        std_min = std_min.filter("range", document_datetime={"lte": datetime_to})
    std_min = std_min[:top_news_num]
    document_evals_min = std_min.execute()
    top_news.update((d.document_es_id for d in document_evals_min))
    return document_evals, top_news


document_evals, top_news = get_current_document_evals(
    topic_modelling,
    granularity,
    [s.name for s in Source.objects.filter(corpus__name__in=corpus)]
)

# Normalize
normalize_documents_eval_dynamics(document_evals, None)

absolute_value = document_evals.aggregations.dynamics.buckets
negative = list(document_evals.aggregations.posneg.buckets[0].dynamics.buckets)
positive = list(document_evals.aggregations.posneg.buckets[-1].dynamics.buckets)
# Equalize periods
positive_ticks = set([bucket.key_as_string for bucket in positive])
negative_ticks = set([bucket.key_as_string for bucket in negative])

class Bucket(object):
    pass


for tick in positive_ticks - negative_ticks:
    bucket = Bucket()
    setattr(bucket, "key_as_string", tick)
    setattr(bucket, "doc_count", 0)
    negative.append(bucket)


for tick in negative_ticks - positive_ticks:
    bucket = Bucket()
    setattr(bucket, "key_as_string", tick)
    setattr(bucket, "doc_count", 0)
    positive.append(bucket)


positive = sorted(positive, key=lambda x: x.key_as_string)
negative = sorted(negative, key=lambda x: x.key_as_string)

if smooth:
    smooth_buckets(absolute_value,
                   is_posneg=False,
                   granularity=granularity)
    smooth_buckets(positive,
                   is_posneg=True,
                   granularity=granularity)
    smooth_buckets(negative,
                   is_posneg=True,
                   granularity=granularity)

df = pd.read_csv("/owid-covid-data.csv")
df = df[df.location == country].fillna(0)
for name, dynamic in {
    "absolute": absolute_value,
    "negative": negative,
    "positive": positive,
}.items():
    if name == "absolute":
        dynamic = [d.dynamics_weight.value for d in dynamic]
    else:
        dynamic = [d.doc_count for d in dynamic]
    print("!!!", name)
    correlations = []
    for field in fields:
        print("!", field)
        if len(dynamic) < len(df[field]):
            diff = len(df[field]) - len(dynamic)
            dynamic = [0] * diff + list(dynamic)
            print("!DIFF", diff)
        try:
            correlations.append(
                {
                    "corr": pearsonr(dynamic, df[field])[0],
                    "field": field,
                }
            )
        except:
            print("SAD :(")
            continue
    with open(f"/covid/sentiment-{name}-{country}-{topic_modelling}-top.txt", "w") as f:
        for corr in sorted(correlations, key=lambda x: x['corr'], reverse=True)[:25]:
            f.write(f"{corr['corr']} - {corr['field']}\n")
    with open(f"/covid/sentiment-{name}-{country}-{topic_modelling}-bottom.txt", "w") as f:
        for corr in sorted(correlations, key=lambda x: x['corr'], reverse=False)[:25]:
            f.write(f"{corr['corr']} - {corr['field']}\n")
