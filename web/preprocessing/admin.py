from django.contrib import admin
from preprocessing.models import *


class ProcessedCorpusAdmin(admin.ModelAdmin):
    list_display = ('name', 'corpus', 'description', )
    list_filter = ('corpus', )
    search_fields = ('name', 'corpus__name', 'description', )


class ProcessedDocumentAdmin(admin.ModelAdmin):
    list_display = ('processed_corpus', 'original_document', )
    list_filter = ('processed_corpus', )
    search_fields = ('processed_corpus__name', 'processed_corpus__description', 'original_document__title')


class AnalysisUnitAdmin(admin.ModelAdmin):
    list_display = ('value', 'processed_document', 'type', 'index', )
    list_filter = ('type', )
    search_fields = ('value', 'processed_document__original_document__title', )


admin.site.register(ProcessedCorpus, ProcessedCorpusAdmin)
admin.site.register(ProcessedDocument, ProcessedDocumentAdmin)
admin.site.register(AnalysisUnit, AnalysisUnitAdmin)
