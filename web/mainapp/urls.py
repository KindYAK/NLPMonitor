from django.urls import path, include
from .views import *
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

app_name = 'mainapp'

urlpatterns = [
    path('', TemplateView.as_view(template_name="mainapp/index.html"), name="index"),
    path('search/', SearchView.as_view(template_name="mainapp/search.html"), name='search'),
    path('dashboard/', DashboardView.as_view(template_name="mainapp/dashboard.html"), name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name="mainapp/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page="/"), name='logout'),
    path('kibana_dashboard/', KibanaDashboardView.as_view(template_name="mainapp/kibana_dashboard.html"), name="kibana_dashboard")
]
