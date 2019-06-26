from django.db import models
from topicmodelling.models import Topic, DocumentTopic


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

    def __str__(self):
        return self.name


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
        indexes = [
            models.Index(fields=['source']),
        ]
        unique_together = (('source', 'title', 'datetime'), )

    source = models.ForeignKey('Source', on_delete=models.CASCADE, verbose_name="Источник")
    author = models.ForeignKey('Author', null=True, blank=True, on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(max_length=2500, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    html = models.TextField(null=True, blank=True, verbose_name="HTML")
    links = models.TextField(null=True, blank=True, verbose_name="Перечень ссылок")
    url = models.CharField(max_length=1000, null=True, blank=True, verbose_name="URL")

    datetime = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата парсинга")

    num_views = models.IntegerField(null=True, blank=True, verbose_name="Количество просмотров")
    num_shares = models.IntegerField(null=True, blank=True, verbose_name="Количество репостов/шейров")
    num_comments = models.IntegerField(null=True, blank=True, verbose_name="Количество комментариев")
    num_likes = models.IntegerField(null=True, blank=True, verbose_name="Количество лайков")

    tags = models.ManyToManyField('Tag', verbose_name="Теги", blank=True)
    categories = models.ManyToManyField('Category', verbose_name="Категории", blank=True)

    topics = models.ManyToManyField('topicmodelling.Topic', through='topicmodelling.DocumentTopic', verbose_name="Топики", blank=True)

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
        unique_together = (('document', 'datetime', 'text'), )
        indexes = [
            models.Index(fields=['document']),
        ]

    text = models.TextField(verbose_name="Текст")
    document = models.ForeignKey('Document', on_delete=models.CASCADE, verbose_name="Документ")
    datetime = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата парсинга")
    reply_to = models.ForeignKey('Comment', null=True, blank=True, on_delete=models.CASCADE, verbose_name="Ответ на...")

    def __str__(self):
        max_length_to_show = 50
        return self.text[:max_length_to_show] + ("..." if len(self.text) > max_length_to_show else "")
