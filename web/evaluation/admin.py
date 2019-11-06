from django.contrib import admin
from .models import *


class EvalCorpusAdmin(admin.ModelAdmin):
    list_display = ('name', 'corpus', )
    list_filter = ('corpus', )
    search_fields = ('name', 'corpus__name', )


class EvalCriterionAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )


class DocumentEvalAdmin(admin.ModelAdmin):
    list_display = ('document', 'evaluation_criterion', 'corpus', 'value', )
    list_filter = ('evaluation_criterion', 'corpus', )
    search_fields = ('corpus__name', 'evaluation_criterion__name', 'document__name', )


class TopicsEvalAdmin(admin.ModelAdmin):
    list_display = ('criterion', 'value', 'topics', )
    list_filter = ('criterion', )
    search_fields = ()


class TopicIDEvalAdmin(admin.ModelAdmin):
    list_display = ('topic_id', 'topics_eval', 'weight', )
    list_filter = ('topic_id', 'topics_eval', 'topic_modelling_name', )
    search_fields = ()


admin.site.register(EvalCorpus, EvalCorpusAdmin)
admin.site.register(EvalCriterion, EvalCriterionAdmin)
admin.site.register(DocumentEval, DocumentEvalAdmin)
admin.site.register(TopicsEval, TopicsEvalAdmin)
admin.site.register(TopicIDEval, TopicIDEvalAdmin)
