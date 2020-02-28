from django.conf.urls import include, url
from rest_framework import routers

from restapp.views import *

router = routers.DefaultRouter()
router.register("topic_group", TopicGroupViewSet, basename="topic_group")
router.register("criterion_eval", CriterionEvalViewSet, basename="criterion_eval")
router.register("range_documents", RangeDocumentsViewSet, basename="range_documents")
router.register("criterion_eval_util", CriterionEvalUtilViewSet, basename="criterion_eval_util")
router.register("dynamic_tm", DynamicTMViewSet, basename="dynamic_tm")

app_name = 'restapp'

urlpatterns = [
    url('', include(router.urls)),
]
