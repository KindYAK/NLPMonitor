from django.conf.urls import include, url
from rest_framework import routers
from restapp.views import *

router = routers.DefaultRouter()
router.register("test", TestViewSet, basename="Test")

app_name = 'restapp'

urlpatterns = [
    url('', include(router.urls)),
]
