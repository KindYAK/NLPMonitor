from django.contrib import admin
from .models import *


class DashboardPresetAdmin(admin.ModelAdmin):
    list_display = ('name', 'corpus', 'topic_modelling_name', )
    list_filter = ('corpus', 'topic_modelling_name', )
    search_fields = ('name', )


class WidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'criterion', 'index', )
    list_filter = ('type', 'criterion', )
    search_fields = ('title', )


admin.site.register(DashboardPreset, DashboardPresetAdmin)
admin.site.register(Widget, WidgetAdmin)
