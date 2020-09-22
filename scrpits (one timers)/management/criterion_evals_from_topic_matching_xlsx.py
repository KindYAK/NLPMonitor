from collections import defaultdict

import pandas as pd
from annoying.functions import get_object_or_None
from django.contrib.auth.models import User
from elasticsearch_dsl import Search

from evaluation.models import EvalCriterion, TopicsEval, TopicIDEval
from mainapp.models import Document
from mainapp.models_user import TopicID
from nlpmonitor.settings import ES_INDEX_DOCUMENT, ES_CLIENT, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_TOPIC_MODELLING


def custom_multiply(value, weight):
    return (value - 0.5) * weight + 0.5 + 2 ** -20


def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union


topic_modelling = "bigartm_two_years_main_and_gos2"
criterion_name = "Социальная значимость (опросы)"

author = User.objects.filter(is_superuser=True).first()
criterion = get_object_or_None(EvalCriterion, name=criterion_name)
if not criterion:
    criterion = EvalCriterion.objects.create(name=criterion_name)

df = pd.read_excel("/social_sign_values.xlsx")

s = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING)
s = s.filter("term", name=topic_modelling)
r = s.execute()

topics = r[0].topics
topics_evals = defaultdict(int)

for topic in topics:
    words = [w['word'].strip().lower() for w in topic.topic_words[:30]]
    for i, row in df.iterrows():
        similarity = jaccard_similarity(words, [w.strip().lower() for w in row.words.split(",")[:30]])
        topics_evals[topic.id] += custom_multiply(row.val, similarity)
    topics_evals[topic.id] /= len(df)


min_v = min(topics_evals.values())
max_v = max(topics_evals.values())

for key in topics_evals.keys():
    topics_evals[key] = (topics_evals[key] - min_v) / (max_v - min_v)

for topic_id, value in topics_evals.items():
    topic_id_obj = get_object_or_None(TopicID, topic_modelling_name=topic_modelling, topic_id=topic_id)
    if not topic_id_obj:
        topic_id_obj = TopicID.objects.create(topic_modelling_name=topic_modelling, topic_id=topic_id)
    topics_eval = get_object_or_None(TopicsEval,
                                     topics=topic_id_obj,
                                     topicideval__weight=1,
                                     criterion__id=criterion.id,
                                     author=author)
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
