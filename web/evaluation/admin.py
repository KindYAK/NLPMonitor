from django.contrib import admin
from .models import *


class EvalCriterionAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'is_categorical', 'is_integer', 'calc_virt_negative', )
    list_filter = ('group', 'is_categorical', 'is_integer', 'calc_virt_negative', )
    search_fields = ('name', )


class EvalCriterionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ()
    search_fields = ('name', )


class CategoricalCriterionValueAdmin(admin.ModelAdmin):
    list_display = ('criterion', 'int_value', 'char_value', )
    list_filter = ('criterion', )
    search_fields = ('char_value', )


class TopicsEvalAdmin(admin.ModelAdmin):
    list_display = ('criterion', 'value', 'author', )
    list_filter = ('criterion', 'author', )
    search_fields = ()


class TopicIDEvalAdmin(admin.ModelAdmin):
    list_display = ('topic_id', 'topics_eval', 'weight', )
    list_filter = ('topic_id', 'topics_eval', )
    search_fields = ()


admin.site.register(EvalCriterion, EvalCriterionAdmin)
admin.site.register(EvalCriterionGroup, EvalCriterionGroupAdmin)
admin.site.register(CategoricalCriterionValue, CategoricalCriterionValueAdmin)
admin.site.register(TopicsEval, TopicsEvalAdmin)
admin.site.register(TopicIDEval, TopicIDEvalAdmin)
