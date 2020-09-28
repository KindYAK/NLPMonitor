from django.urls import path, include
from .views import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page

app_name = 'mainapp'

urlpatterns = [
    path('index/', TemplateView.as_view(template_name="mainapp/index.html"), name="index"),
    path('', login_redirect, name="login_redirect"),
    path('login_redirect/', login_redirect, name="login_redirect"),
    path('accounts/login/', cache_page(60*60*8)(auth_views.LoginView.as_view(template_name="mainapp/login.html")), name='login'),
    path('accounts/logout/', cache_page(60*60*8)(auth_views.LogoutView.as_view(next_page="/")), name='logout'),

    path('search/', SearchView.as_view(), name='search'),

    path('document_view/<document_id>/', DocumentDetailView.as_view(), name='document_view'),
    path('document_create/', DocumentCreateView.as_view(), name='document_create'),
    path('document_create_success/', TemplateView.as_view(template_name="mainapp/document_create_success.html"), name='document_create_success'),
    path('document_list/', DocumentListView.as_view(), name='document_list'),
    path('document_delete/<pk>/', DocumentDeleteView.as_view(), name='document_delete'),
]
