from django.contrib.auth.models import User
from elasticsearch_dsl import Search

from mainapp.models_user import TopicGroup, TopicID
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_MODELLING

tm_name = "bigartm__scopus_100"
try:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=tm_name).execute()[0]
except:
    tm = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", **{"name.keyword": tm_name}).execute()[
        0]

for topic in tm.topics:
    name = ", ".join([w.word for w in list(sorted(topic.topic_words, key=lambda x: x.weight, reverse=True))[:7]])
    print("!!!", name)
    tg = TopicGroup.objects.create(
        name=f"scopus_100_{name[:100-13]}",
        topic_modelling_name=tm_name,
        owner=User.objects.filter(is_superuser=True).first(),
    )
    t = TopicID.objects.create(
        topic_modelling_name=tm_name,
        topic_id=topic.id
    )
    tg.topics.add(t)
    tg.save()
    t.save()
