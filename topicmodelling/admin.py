from django.contrib import admin
from topicmodelling.models import *


class TopicCorpusAdmin(admin.ModelAdmin):
    pass


class TopicAdmin(admin.ModelAdmin):
    pass


class TopicUnitAdmin(admin.ModelAdmin):
    pass


class DocumentTopicAdmin(admin.ModelAdmin):
    pass


admin.site.register(TopicCorpus, TopicCorpusAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(TopicUnit, TopicUnitAdmin)
admin.site.register(DocumentTopic, DocumentTopicAdmin)
