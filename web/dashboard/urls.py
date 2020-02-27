from django.urls import path, include
from .views import *

app_name = 'dashboard'

urlpatterns = [
    path('<dashboard_id>/', DashboardView.as_view(), name="dashboard"),
]
