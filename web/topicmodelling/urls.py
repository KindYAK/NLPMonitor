from django.urls import path

from .views import *

app_name = 'topicmodelling'

urlpatterns = [
    path('topics_list/', TopicsListView.as_view(), name="topics_list"),
    path('topic_documents_list/<topic_modelling>/<topic_name>/', TopicDocumentListView.as_view(), name="topic_document_list"),
    path('topic_documents_list/<topic_modelling>/', TopicDocumentListView.as_view(), name="topics_group_document_list"),

    path('monitoring_object_documents_list/<widget_id>/<object_id>/', MonitoringObjectDocumentListView.as_view(), name="monitoring_object_document_list"),

    path('topics_combo_list/', TopicsComboListView.as_view(), name="topics_combo_list"),

    path('dynamic_tm/', DynamicTMView.as_view(), name="dynamic_tm")
]
