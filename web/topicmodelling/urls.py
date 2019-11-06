from django.urls import path, include
from .views import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page

app_name = 'topicmodelling'

urlpatterns = [
    path('topics_list/', TopicsListView.as_view(), name="topics_list"),
    path('topic_documents_list/<topic_modelling>/<topic_name>/', TopicDocumentListView.as_view(),
        name="topic_document_list"),
    path('topic_documents_list/<topic_modelling>/', TopicDocumentListView.as_view(),
        name="topics_group_document_list"),
]
