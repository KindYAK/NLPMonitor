from django.contrib import admin
from preprocessing.models import *


class ProcessedCorpusAdmin(admin.ModelAdmin):
    pass


class ProcessedDocumentAdmin(admin.ModelAdmin):
    pass


class AnalysisUnitAdmin(admin.ModelAdmin):
    pass


admin.site.register(ProcessedCorpus, ProcessedCorpusAdmin)
admin.site.register(ProcessedDocument, ProcessedDocumentAdmin)
admin.site.register(AnalysisUnit, AnalysisUnitAdmin)
