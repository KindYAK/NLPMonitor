import pandas as pd
from annoying.functions import get_object_or_None
from django.contrib.auth.models import User
from elasticsearch_dsl import Search

from evaluation.models import TopicsEval, TopicIDEval, EvalCriterion
from mainapp.models_user import TopicID
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_MODELLING

tm_name = "bigartm_two_years"
criterion = EvalCriterion.objects.get(name="Социальная значимость (разметка экспертов)")
try:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=tm_name).execute()[0]
except:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", **{"name.keyword": tm_name}).execute()[0]

name_topic_id_dict = {}
for topic in tm.topics:
    name = ", ".join([w.word for w in list(sorted(topic.topic_words, key=lambda x: x.weight, reverse=True))[:10]])
    name_topic_id_dict[name] = topic.id


topic_evals = pd.read_excel("/topic_evals.xlsx")

to_create = []
for row in topic_evals.iterrows():
    if row[1]['name'] in name_topic_id_dict:
        to_create.append(
            {
                "id": name_topic_id_dict[row[1]['name']],
                "eval": row[1]['eval']
            }
        )
        print(row[1]['name'])


for obj in to_create:
    topic_id_obj = get_object_or_None(TopicID, topic_modelling_name=tm_name, topic_id=obj['id'])
    if not topic_id_obj:
        topic_id_obj = TopicID.objects.create(topic_modelling_name=tm_name, topic_id=obj['id'])
    topics_eval = get_object_or_None(TopicsEval,
                                     topics=topic_id_obj,
                                     topicideval__weight=1,
                                     criterion__id=criterion.id,
                                     author=User.objects.filter(is_superuser=True).first())
    value = obj['eval']
    if topics_eval:
        topics_eval.value = value
        topics_eval.save()
    else:
        topics_eval = TopicsEval.objects.create(criterion_id=criterion.id, value=value, author=User.objects.filter(is_superuser=True).first())
        TopicIDEval.objects.create(
            topic_id=topic_id_obj,
            topics_eval=topics_eval,
            weight=1
        )
