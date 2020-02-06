import hashlib

from django.contrib.auth.models import User
from django.db import models
from topicmodelling.models import Topic, DocumentTopic
from .models_user import TopicGroup, TopicID, ContentLoader, Expert, Viewer, UserGroup


class Corpus(models.Model):
    class Meta:
        verbose_name = "Корпус"
        verbose_name_plural = "Корпусы"

    name = models.CharField(max_length=50, unique=True, verbose_name="Название")

    def __str__(self):
        return self.name


class Source(models.Model):
    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"
        unique_together = (('corpus', 'name'), )

    name = models.CharField(max_length=50, verbose_name="Название")
    url = models.CharField(max_length=150, null=True, blank=True, verbose_name="URL")
    corpus = models.ForeignKey('Corpus', on_delete=models.CASCADE, verbose_name="Корпус")
    is_for_content_loaders = models.BooleanField(default=False, verbose_name="Для 'Блогеров'")

    def __str__(self):
        return self.name


class ScrapRules(models.Model):
    class Meta:
        verbose_name = "Правило скрапинга"
        verbose_name_plural = "Правила скрапинга"
        unique_together = (('source', 'type'), )

    TYPES = (
        (0, "title"),
        (1, "text"),
        (2, "author"),
        (3, "datetime"),
        (4, "tags"),
        (5, "categories"),
        (6, "num_views"),
        (7, "num_likes"),
        (8, "num_comments"),
        (9, "num_shares"),
    )

    source = models.ForeignKey('Source', on_delete=models.CASCADE, verbose_name="Источник")
    type = models.SmallIntegerField(choices=TYPES, verbose_name="Тип поля")
    selector = models.CharField(max_length=500, verbose_name="CSS селектор")


class Author(models.Model):
    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        unique_together = (('corpus', 'name'), )

    name = models.CharField(max_length=200,verbose_name="Название")
    corpus = models.ForeignKey('Corpus', on_delete=models.CASCADE, verbose_name="Корпус")

    def __str__(self):
        return self.name


class Document(models.Model):
    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        unique_together = ('source', 'date', 'title', )

    TYPES = (
        (0, "News"),
        (1, "Interview"),
        (2, "Article"),
        (3, "Blogs/Opinions"),
    )

    source = models.ForeignKey('Source', on_delete=models.CASCADE, verbose_name="Источник*")
    author = models.ForeignKey('Author', null=True, blank=True, on_delete=models.CASCADE, verbose_name="Автор (FK)")
    author_txt = models.CharField(max_length=100, null=True, blank=True, verbose_name="Автор")
    title = models.CharField(max_length=500, verbose_name="Заголовок*")
    text = models.TextField(verbose_name="Текст*")
    html = models.TextField(null=True, blank=True, verbose_name="HTML")
    links = models.TextField(null=True, blank=True, verbose_name="Перечень ссылок")
    url = models.CharField(max_length=1000, null=True, blank=True, verbose_name="URL")
    type = models.SmallIntegerField(choices=TYPES, default=0, verbose_name="Тип публикации (в основном для Тенгри)")

    datetime = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")
    date = models.DateField(null=True, blank=True, verbose_name="Дата публикации (dateonly)")
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата парсинга")

    num_views = models.IntegerField(null=True, blank=True, verbose_name="Количество просмотров")
    num_shares = models.IntegerField(null=True, blank=True, verbose_name="Количество репостов/шейров")
    num_comments = models.IntegerField(null=True, blank=True, verbose_name="Количество комментариев")
    num_likes = models.IntegerField(null=True, blank=True, verbose_name="Количество лайков")

    tags = models.ManyToManyField('Tag', verbose_name="Теги", blank=True)
    categories = models.ManyToManyField('Category', verbose_name="Категории", blank=True)

    topics = models.ManyToManyField('topicmodelling.Topic', through='topicmodelling.DocumentTopic', verbose_name="Топики", blank=True)

    author_loader = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Автор (кто загрузил)")
    sentiment_loader = models.FloatField(null=True, blank=True, verbose_name="Тональность*")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.datetime and not self.date:
            self.date = self.datetime.date()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.title


class Tag(models.Model):
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        unique_together = (('corpus', 'name'), )
        indexes = [
            models.Index(fields=['corpus']),
        ]

    corpus = models.ForeignKey('Corpus', on_delete=models.CASCADE, verbose_name="Корпус")
    name = models.CharField(max_length=100, verbose_name="Название")

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        unique_together = (('corpus', 'name'), )
        indexes = [
            models.Index(fields=['corpus']),
        ]

    corpus = models.ForeignKey('Corpus', on_delete=models.CASCADE, verbose_name="Корпус")
    name = models.CharField(max_length=100, verbose_name="Название")

    def __str__(self):
        return self.name


class Comment(models.Model):
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    text = models.TextField(verbose_name="Текст")
    document = models.ForeignKey('Document', on_delete=models.CASCADE, verbose_name="Документ")
    datetime = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата парсинга")
    reply_to = models.ForeignKey('Comment', null=True, blank=True, on_delete=models.CASCADE, verbose_name="Ответ на...")
    unique_hash = models.CharField(max_length=32, null=True, blank=True, unique=True, verbose_name="Уникальность document, datetime, text")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        hash = hashlib.md5()
        hash.update(str(self.document.id).encode())
        hash.update(str(self.datetime).encode())
        hash.update(self.text.encode())
        self.unique_hash = hash.hexdigest()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        max_length_to_show = 50
        return self.text[:max_length_to_show] + ("..." if len(self.text) > max_length_to_show else "")
