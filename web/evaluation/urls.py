from django.urls import path, include
from .views import *

app_name = 'evaluation'

urlpatterns = [
    path('criterion_eval_analysis/', CriterionEvalAnalysisView.as_view(), name="criterion_eval_analysis"),
]
