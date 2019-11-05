from django.urls import path, include
from .views import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page

app_name = 'mainapp'

urlpatterns = [
    path('', TemplateView.as_view(template_name="mainapp/index.html"), name="index"),
    path('accounts/login/', cache_page(60*60*8)(auth_views.LoginView.as_view(template_name="mainapp/login.html")), name='login'),
    path('accounts/logout/', cache_page(60*60*8)(auth_views.LogoutView.as_view(next_page="/")), name='logout'),

    path('search/', SearchView.as_view(), name='search'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('kibana_dashboard/', KibanaDashboardView.as_view(), name="kibana_dashboard"),

    path('document_view/<document_id>/', DocumentDetailView.as_view(), name='document_view'),

    path('topics_list/', TopicsListView.as_view(), name="topics_list"),
    path('topic_documents_list/<topic_modelling>/<topic_name>/', TopicDocumentListView.as_view(),
        name="topic_document_list"),
    path('topic_documents_list/<topic_modelling>/', TopicDocumentListView.as_view(),
        name="topics_group_document_list"),
]
