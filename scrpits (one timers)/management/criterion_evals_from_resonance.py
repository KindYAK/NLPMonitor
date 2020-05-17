from annoying.functions import get_object_or_None
from django.contrib.auth.models import User
from elasticsearch_dsl import Search

from evaluation.models import EvalCriterion, TopicsEval, TopicIDEval
from mainapp.models_user import TopicID
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_MODELLING
from topicmodelling.services import calc_topics_resonance

# topic_modelling = "bigartm_two_years_old_parse"
topic_modelling = "bigartm_test"
criterion_name = "Резонансность"

tm_index = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING).filter("term", name=topic_modelling).execute()[0]
topics = tm_index.topics

calc_topics_resonance(topics, topic_modelling)

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
