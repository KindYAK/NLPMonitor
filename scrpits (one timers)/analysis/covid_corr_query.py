import datetime
from collections import defaultdict

import pandas as pd
from elasticsearch_dsl import Search
from scipy.stats import pearsonr, spearmanr

from mainapp.models import Corpus
from mainapp.services import apply_fir_filter
from mainapp.services_es_documents import execute_search, es_filter
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT

granularity = "1d"
smooth = True
datetime_from = datetime.datetime(2020, 3, 13)  # Kaz
# datetime_from = datetime.datetime(2020, 1, 31) # Rus
datetime_to = datetime.datetime(2021, 2, 25)  # Add One
corpus = [1] # Kaz
# corpus = [38, 39] # RUS
country = "Kazakhstan"
# country = "Russia"
fields = [
    "new_cases_smoothed",
    "new_deaths_smoothed",
    "reproduction_rate",
    "new_tests",
    "positive_rate",
    "tests_per_case",
    "stringency_index",
]
sd_total = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
sd_total = es_filter(sd_total, "corpuses", Corpus.objects.filter(id__in=corpus))
sd_total.aggs.bucket(name="dynamics",
                     agg_type="date_histogram",
                     field="datetime",
                     calendar_interval=granularity)
documents_total = sd_total.execute()
total_metrics_dict = dict(
    (
        t.key_as_string,
        {
            "size": t.doc_count
        }
    ) for t in documents_total.aggregations.dynamics.buckets
)
# correlations = []

correlations = defaultdict(list)
for query in [
    "фейк ложная информация дезинформация",
    "безработица бедность",
    "кризис упадок падение",
    "нищета голод бездомный",
    "удалённое образование удалёнка",
    "фриланс зарубеж удалённая работа утечка мозгов",
    "преступность воровство кражи разбой",
    "кризис кредитование долг микрокредитные",
    "здравоохранение больницы проблемы скандал",
    "вакцинация вакцины прививка COVID"
]:
    print(query)
    # df = pd.read_csv("/owid-covid-data.csv")
    # df = df[df.location == country].fillna(0)
    search_request = {}
    search_request['datetime_from'] = datetime_from
    search_request['datetime_to'] = datetime_to
    search_request['corpuses'] = Corpus.objects.filter(id__in=corpus)
    search_request['text'] = query
    s = execute_search(search_request, return_search_obj=True)[:0]
    s.aggs.bucket(name="dynamics",
                  agg_type="date_histogram",
                  field="datetime",
                  calendar_interval=granularity) \
        .metric("dynamics_weight", agg_type="sum", script="_score")
    results = s.execute()
    # Normalize dynamics
    for bucket in results.aggregations.dynamics.buckets:
        total_size = total_metrics_dict[bucket.key_as_string]['size']
        if total_size != 0:
            bucket.doc_count_normal = bucket.doc_count / total_size
            bucket.dynamics_weight.value /= total_size
        else:
            bucket.doc_count_normal = 0
    # Separate signals
    absolute_power = [bucket.doc_count for bucket in results.aggregations.dynamics.buckets]
    relative_power = [bucket.doc_count_normal for bucket in results.aggregations.dynamics.buckets]
    relative_weight = [bucket.dynamics_weight.value for bucket in results.aggregations.dynamics.buckets]
    # Smooth
    if smooth:
        absolute_power = apply_fir_filter(absolute_power, granularity=granularity)
        relative_power = apply_fir_filter(relative_power, granularity=granularity)
        relative_weight = apply_fir_filter(relative_weight, granularity=granularity)
    for dynamics_name, dynamics in [
        # ("absolute_power", absolute_power),
        # ("relative_power", relative_power),
        ("relative_weight", relative_weight),
    ]:
        print(dynamics_name)
        for field in fields:
            print("!", field)
            if len(dynamics) < len(df[field]):
                diff = len(df[field]) - len(dynamics)
                dynamics = [0] * diff + list(dynamics)
            elif len(dynamics) > len(df[field]):
                dynamics = dynamics[:len(df[field])]
            try:
                correlations[field].append(
                    {
                        "corr": spearmanr(dynamics, df[field])[0],
                        "field": field,
                        "query": query
                    }
                )
            except:
                print("SAD :(")
                import random
                correlations[field].append(
                    {
                        "corr": random.random(),
                        "field": field,
                        "query": query,
                    }
                )
                continue
        # with open(f"/covid/queries-{country}-{dynamics_name}-{query}.txt", "w") as f:
        #     for corr in sorted(correlations, key=lambda x: x['corr'], reverse=True)[:25]:
        #         f.write(f"{corr['corr']} - {corr['field']}\n")

# pd.DataFrame(correlations).to_json("/corr_mat_queries.json")


for key in correlations.keys():
    print(key)
    top = sorted(correlations[key], key=lambda x: x['corr'], reverse=True)[0]
    query = top['query']
    search_request = {}
    search_request['datetime_from'] = datetime_from
    search_request['datetime_to'] = datetime_to
    search_request['corpuses'] = Corpus.objects.filter(id__in=corpus)
    search_request['text'] = query
    s = execute_search(search_request, return_search_obj=True)[:0]
    s.aggs.bucket(name="dynamics",
                  agg_type="date_histogram",
                  field="datetime",
                  calendar_interval=granularity) \
        .metric("dynamics_weight", agg_type="sum", script="_score")
    results = s.execute()
    # Normalize dynamics
    for bucket in results.aggregations.dynamics.buckets:
        total_size = total_metrics_dict[bucket.key_as_string]['size']
        if total_size != 0:
            bucket.doc_count_normal = bucket.doc_count / total_size
            bucket.dynamics_weight.value /= total_size
        else:
            bucket.doc_count_normal = 0
    # Separate signals
    relative_weight = [bucket.dynamics_weight.value for bucket in results.aggregations.dynamics.buckets]
    # Smooth
    if smooth:
        relative_weight = apply_fir_filter(relative_weight, granularity=granularity)
    pickle.dump({
        "covid": df[key],
        "topic": relative_weight,
        "query": query,
    }, open(f"/export/query_{key}.pkl", "wb"))
