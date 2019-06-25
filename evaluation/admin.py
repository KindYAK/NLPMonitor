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


admin.site.register(EvalCorpus, EvalCorpusAdmin)
admin.site.register(EvalCriterion, EvalCriterionAdmin)
admin.site.register(DocumentEval, DocumentEvalAdmin)