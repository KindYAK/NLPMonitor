from django.db import models
from topicmodelling.models import Topic, DocumentTopic


class Corpus(models.Model):
    class Meta:
        verbose_name = "Корпус"
        verbose_name_plural = "Корпусы"

    name = models.CharField(max_length=50, unique=True)


class Source(models.Model):
    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"
        unique_together = (('corpus', 'name'))

    name = models.CharField(max_length=50)
    url = models.CharField(max_length=150, null=True, blank=True)
    corpus = models.ForeignKey('Corpus', on_delete=models.CASCADE)


class Author(models.Model):
    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        unique_together = (('corpus', 'name'))

    name = models.CharField(max_length=200)
    corpus = models.ForeignKey('Corpus', on_delete=models.CASCADE)


class Document(models.Model):
    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        unique_together = (('source', 'title', 'datetime'))

    source = models.ForeignKey('Source', on_delete=models.CASCADE)
    author = models.ForeignKey('Author', null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=2500)
    text = models.TextField()
    html = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=1000, null=True, blank=True)

    datetime = models.DateTimeField(null=True, blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True)

    num_views = models.IntegerField(null=True, blank=True)
    num_shares = models.IntegerField(null=True, blank=True)
    num_comments = models.IntegerField(null=True, blank=True)
    num_likes = models.IntegerField(null=True, blank=True)

    tags = models.ManyToManyField('Tag')
    categories = models.ManyToManyField('Category')

    topics = models.ManyToManyField('topicmodelling.Topic', through='topicmodelling.DocumentTopic')


class Tag(models.Model):
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        unique_together = (('corpus', 'name'))

    corpus = models.ForeignKey('Corpus', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class Category(models.Model):
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        unique_together = (('corpus', 'name'))

    corpus = models.ForeignKey('Corpus', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class Comment(models.Model):
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        unique_together = (('document', 'datetime', 'text'))

    text = models.TextField()
    document = models.ForeignKey('Document', null=True, blank=True, on_delete=models.CASCADE)
    datetime = models.DateTimeField(null=True, blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('Comment', null=True, blank=True, on_delete=models.CASCADE)
