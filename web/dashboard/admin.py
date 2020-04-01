from django.contrib import admin

from .models import *


class DashboardPresetAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ()
    search_fields = ('name',)


class WidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'criterion', 'topic_modelling_name', 'index',)
    list_filter = ('type', 'criterion', 'topic_modelling_name',)
    search_fields = ('title',)


class MonitoringObjectAdmin(admin.ModelAdmin):
    list_display = ('name_query', 'ner_query')
    list_filter = ()
    search_fields = ('name_query',)


admin.site.register(DashboardPreset, DashboardPresetAdmin)
admin.site.register(Widget, WidgetAdmin)
admin.site.register(MonitoringObject, MonitoringObjectAdmin)
