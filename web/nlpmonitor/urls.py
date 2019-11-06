"""nlpmonitor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from nlpmonitor.settings import STATIC_URL, STATIC_ROOT

urlpatterns = [
    path('', include('mainapp.urls', namespace='mainapp')),
    path('topicmodelling/', include('topicmodelling.urls', namespace='topicmodelling')),
    path('jet/', include('jet.urls', namespace='jet')),
    path('api/', include('restapp.urls', namespace='api')),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls, name="admin"),
] + static(STATIC_URL, document_root=STATIC_ROOT)
