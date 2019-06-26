from django.contrib import admin
from topicmodelling.models import *


class TopicCorpusAdmin(admin.ModelAdmin):
    list_display = ('name', 'corpus', )
    list_filter = ('corpus', )
    search_fields = ('name', 'corpus__name', 'description', )


class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic_corpus', 'topic_parent', )
    list_filter = ('topic_corpus', )
    search_fields = ('name', 'topic_corpus__name', 'topic_corpus__description', )


class TopicUnitAdmin(admin.ModelAdmin):
    list_display = ('text', 'topic', 'weight', )
    list_filter = ('topic', )
    search_fields = ('text', 'topic__name', )


class DocumentTopicAdmin(admin.ModelAdmin):
    list_display = ('topic', 'document', 'weight', )
    list_filter = ('topic', )
    search_fields = ('topic__name', 'document__title', )


admin.site.register(TopicCorpus, TopicCorpusAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(TopicUnit, TopicUnitAdmin)
admin.site.register(DocumentTopic, DocumentTopicAdmin)
