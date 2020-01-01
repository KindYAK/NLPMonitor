from django.contrib import admin
from .models import *


class EvalCriterionAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'is_categorical', 'is_integer', )
    list_filter = ('group', 'is_categorical', 'is_integer', )
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


# Potentially depricated
class DocumentEvalAdmin(admin.ModelAdmin):
    list_display = ('document', 'evaluation_criterion', 'corpus', 'value', )
    list_filter = ('evaluation_criterion', 'corpus', )
    search_fields = ('corpus__name', 'evaluation_criterion__name', 'document__name', )


class EvalCorpusAdmin(admin.ModelAdmin):
    list_display = ('name', 'corpus', )
    list_filter = ('corpus', )
    search_fields = ('name', 'corpus__name', )


admin.site.register(EvalCorpus, EvalCorpusAdmin)
admin.site.register(DocumentEval, DocumentEvalAdmin)
