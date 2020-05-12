from collections import defaultdict
from statistics import mean, pstdev

from annoying.functions import get_object_or_None
from django.contrib.auth.models import User
from elasticsearch_dsl import Search

from evaluation.models import EvalCriterion, TopicsEval, TopicIDEval
from mainapp.models_user import TopicID
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_MODELLING, ES_INDEX_TOPIC_DOCUMENT

# topic_modelling = "bigartm_two_years_old_parse"
topic_modelling = "bigartm_test"
criterion_name = "Резонансность"

tm_index = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=topic_modelling).execute()[0]
topics = tm_index.topics

std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
    .filter("range", document_num_views={"gt": 0})[:0]
std.aggs.bucket("documents", agg_type="terms", field="document_es_id", size=5_000_000) \
    .metric("document_resonance", agg_type="avg", field="document_num_views")
r = std.execute()

resonances = [bucket.document_resonance.value for bucket in r.aggregations.documents.buckets]
resonance_mean = mean(resonances)
resonance_std = pstdev(resonances)
resonance_threshold = resonance_mean + resonance_std

std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
    .filter("range", document_num_views={"gt": 0})[:0]
std.aggs.bucket("topics", agg_type="terms", field="topic_id", size=1000) \
    .bucket("resonance", agg_type="range", field="document_num_views", ranges=
        [
            {"from": 1, "to": resonance_threshold},
            {"from": resonance_threshold},
        ])
r = std.execute()
topic_resonances = dict(
    (bucket.key,
     {
         "low": bucket.resonance.buckets[0].doc_count,
         "high": bucket.resonance.buckets[1].doc_count,
     }) for bucket in r.aggregations.topics
)

total_low_resonance = 0
total_high_resonance = 0
for res in topic_resonances.values():
    total_low_resonance += res['low']
    total_high_resonance += res['high']

for topic in topics:
    if topic.id in topic_resonances:
        topic.low_resonance_score = topic_resonances[topic.id]['low'] / total_low_resonance
        topic.high_resonance_score = topic_resonances[topic.id]['high'] / total_high_resonance
        total_weight = topic.low_resonance_score + topic.high_resonance_score
        topic.low_resonance_score /= total_weight
        topic.high_resonance_score /= total_weight

author = User.objects.filter(is_superuser=True).first()
criterion = get_object_or_None(EvalCriterion, name=criterion_name)
if not criterion:
    criterion = EvalCriterion.objects.create(name=criterion_name)

for topic in topics:
    topic_id_obj = get_object_or_None(TopicID, topic_modelling_name=topic_modelling, topic_id=topic.id)
    if not topic_id_obj:
        topic_id_obj = TopicID.objects.create(topic_modelling_name=topic_modelling, topic_id=topic.id)
    topics_eval = get_object_or_None(TopicsEval,
                                     topics=topic_id_obj,
                                     topicideval__weight=1,
                                     criterion__id=criterion.id,
                                     author=author)
    if hasattr(topic, "high_resonance_score"):
        value = topic.high_resonance_score
    else:
        value = 0
    if topics_eval:
        topics_eval.value = value
        topics_eval.save()
    else:
        topics_eval = TopicsEval.objects.create(criterion_id=criterion.id, value=value, author=author)
        TopicIDEval.objects.create(
            topic_id=topic_id_obj,
            topics_eval=topics_eval,
            weight=1
        )
