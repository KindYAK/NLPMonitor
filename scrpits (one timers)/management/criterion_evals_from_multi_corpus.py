from annoying.functions import get_object_or_None
from django.contrib.auth.models import User

from evaluation.models import EvalCriterion, TopicsEval, TopicIDEval
from mainapp.models_user import TopicID
from topicmodelling.services import get_topics_with_meta


def get_corpus_weight(topic):
    try:
        return topic.corpus_weights[target_corpus].weight_sum if target_corpus in topic.corpus_weights else 0
    except:
        return 0


topic_modelling = "bigartm_two_years_1000_rus_and_rus_propaganda"
target_corpus = "rus_propaganda"
criterion_name = "Пропаганда (RU)"

topics = get_topics_with_meta(topic_modelling=topic_modelling,
                              topic_weight_threshold=0.005,
                              is_multi_corpus=True)

author = User.objects.filter(is_superuser=True).first()
criterion = get_object_or_None(EvalCriterion, name=criterion_name)
if not criterion:
    criterion = EvalCriterion.objects.create(name=criterion_name)

max_value = max((get_corpus_weight(topic) for topic in topics))

for topic in topics:
    topic_id_obj = get_object_or_None(TopicID, topic_modelling_name=topic_modelling, topic_id=topic.id)
    if not topic_id_obj:
        topic_id_obj = TopicID.objects.create(topic_modelling_name=topic_modelling, topic_id=topic.id)
    topics_eval = get_object_or_None(TopicsEval,
                                     topics=topic_id_obj,
                                     topicideval__weight=1,
                                     criterion__id=criterion.id,
                                     author=author)
    value = get_corpus_weight(topic) / max_value
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
