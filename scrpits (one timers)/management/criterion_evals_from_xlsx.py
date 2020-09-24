import pandas as pd
from annoying.functions import get_object_or_None
from django.contrib.auth.models import User

from evaluation.models import EvalCriterion, TopicsEval, TopicIDEval
from mainapp.models_user import TopicID

topic_modelling = "bigartm_two_years"
criterion_name = "Социальная значимость (опросы)"

author = User.objects.filter(is_superuser=True).first()
criterion = get_object_or_None(EvalCriterion, name=criterion_name)
if not criterion:
    criterion = EvalCriterion.objects.create(name=criterion_name)

df = pd.read_excel("/social_sign_values.xlsx")

for i, row in df.iterrows():
    topic_id_obj = get_object_or_None(TopicID, topic_modelling_name=topic_modelling, topic_id=row['topic_id'])
    if not topic_id_obj:
        topic_id_obj = TopicID.objects.create(topic_modelling_name=topic_modelling, topic_id=row['topic_id'])
    topics_eval = get_object_or_None(TopicsEval,
                                     topics=topic_id_obj,
                                     topicideval__weight=1,
                                     criterion__id=criterion.id,
                                     author=author)
    value = row['val']
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
