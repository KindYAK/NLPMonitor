from django.contrib import admin
from mainapp.models import *


class CorpusAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ()
    search_fields = ('name', )


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'corpus', )
    list_filter = ('corpus', )
    search_fields = ('name', 'url', )


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'corpus', )
    list_filter = ('corpus', )
    search_fields = ('name', 'corpus__name', )


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'datetime', 'source', 'url', )
    list_filter = ('source', )
    search_fields = ('title', 'author__name', 'source__name', 'url', )


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'corpus', )
    list_filter = ('corpus', )
    search_fields = ('name', 'corpus__name', )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'corpus', )
    list_filter = ('corpus', )
    search_fields = ('name', 'corpus__name', )


class CommentAdmin(admin.ModelAdmin):
    list_display = ('document', 'datetime', 'text', )
    list_filter = ()
    search_fields = ('text', 'document__title', )


class ScrapRulesAdmin(admin.ModelAdmin):
    list_display = ('source', 'type', 'selector')
    list_filter = ('source', 'type', )
    search_fields = ('selector', )


admin.site.register(Corpus, CorpusAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ScrapRules, ScrapRulesAdmin)


class TopicGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic_modelling_name', 'owner', 'is_public')
    list_filter = ('owner', 'is_public', 'topic_modelling_name', )
    search_fields = ('name', 'topic_modelling_name', )


class TopicIDAdmin(admin.ModelAdmin):
    list_display = ('topic_modelling_name', 'topic_id', )
    list_filter = ('topic_modelling_name', )
    search_fields = ('topic_modelling_name', )


admin.site.register(TopicGroup, TopicGroupAdmin)
admin.site.register(TopicID, TopicIDAdmin)


class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', )
    list_filter = ('corpuses', 'criterions', )
    search_fields = ('name', 'topic_modelling_names', )


class ContentLoaderAdmin(admin.ModelAdmin):
    list_display = ('user', 'supervisor', )
    list_filter = ('supervisor', )
    search_fields = ('user__username', )


class ExpertAdmin(admin.ModelAdmin):
    list_display = ('user', )
    list_filter = ()
    search_fields = ('user__username', )


class ViewerAdmin(admin.ModelAdmin):
    list_display = ('user', )
    list_filter = ()
    search_fields = ('user__username', )


admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(ContentLoader, ContentLoaderAdmin)
admin.site.register(Expert, ExpertAdmin)
admin.site.register(Viewer, ViewerAdmin)
