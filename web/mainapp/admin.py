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
    fields = ('title', 'text', 'tags', 'categories', )
    raw_id_fields = ('tags', 'categories', )


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


admin.site.register(Corpus, CorpusAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
