from django.contrib import admin
from mainapp.models import *


class CorpusAdmin(admin.ModelAdmin):
    pass


class SourceAdmin(admin.ModelAdmin):
    pass


class AuthorAdmin(admin.ModelAdmin):
    pass


class DocumentAdmin(admin.ModelAdmin):
    pass


class TagAdmin(admin.ModelAdmin):
    pass


class CategoryAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Corpus, CorpusAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
