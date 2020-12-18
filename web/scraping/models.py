from django.db import models


# Common
class SocialNetworkAccount(models.Model):
    class Meta:
        verbose_name = "Аккаунт соц. сети"
        verbose_name_plural = "Аккаунты соц. сетей"
        unique_together = (('url', 'social_network'), ('account_id', 'social_network'))

    # social networks choices
    SOCIAL_NETWORKS = (
        (0, "Facebook"),
        (1, "VK"),
        (2, "Twitter"),
        (3, "Instagram"),
        (4, "Telegram"),
        (5, "YouTube"),
    )

    # account status choices
    ACCOUNT_STATUSES = (
        (0, 'Непроверенный'),
        (1, 'Верифицированный'),
        (2, 'Неверифицированный'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")  # Мухтар Шлюхтар Залупкин
    nickname = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Никнэйм аккаунта")  # @muha_reptar
    social_network = models.PositiveSmallIntegerField(choices=SOCIAL_NETWORKS, verbose_name="Соц. сеть")
    url = models.CharField(max_length=1000, verbose_name="URL аккаунта (ссылка)")  # https://telegram.org/muha_reptar
    account_id = models.CharField(max_length=1000, verbose_name="ID аккаунта")  # 66614881337

    priority_rate = models.FloatField(default=50, verbose_name="Приоритет парсинга (от 0 до 100")
    is_active = models.BooleanField(default=True, verbose_name="Парсинг активирован")
    is_private = models.BooleanField(default=False, verbose_name='Конфеденциальность аккаунта')
    is_valid = models.PositiveSmallIntegerField(default=1, choices=ACCOUNT_STATUSES, verbose_name='Состояние аккаунта')

    num_followers = models.BigIntegerField(default=None, null=True, blank=True, verbose_name='Количество подписчиков')
    num_follows = models.BigIntegerField(default=None, null=True, blank=True, verbose_name='Количество подписок')

    datetime_last_parsed = models.DateTimeField(null=True, blank=True,
                                                verbose_name="Дата последнего успешного парсинга")

    # Meta from YouTube channels
    keywords = models.CharField(max_length=1000, default=None, null=True, blank=True, verbose_name="Ключевые слова канала")
    description = models.CharField(max_length=1500, default=None, null=True, blank=True, verbose_name="Описание канала")
    topic_ids = models.CharField(max_length=1500, default=None, null=True, blank=True, verbose_name='Темы, относящиеся к каналу, разделенные знаком "|"')
    view_count = models.BigIntegerField(default=None, null=True, blank=True, verbose_name='Количество просмотров профиля/канала')
    posts_count = models.BigIntegerField(default=None, null=True, blank=True, verbose_name='Количество постов/видео')

    def __str__(self):
        return f"Аккаунт {self.SOCIAL_NETWORKS[self.social_network][1]} - {self.name}"


class MonitoringQuery(models.Model):
    class Meta:
        verbose_name = "Запрос для мониторинга"
        verbose_name_plural = "Запрос для мониторинга"
        unique_together = (('query', 'social_network'), )

    name = models.CharField(max_length=100, verbose_name="Название")
    social_network = models.PositiveSmallIntegerField(choices=SocialNetworkAccount.SOCIAL_NETWORKS, verbose_name="Соц. сеть")
    query = models.CharField(max_length=1000, verbose_name="Запрос")

    priority_rate = models.FloatField(default=50, verbose_name="Приоритет парсинга (от 0 до 100")
    max_requests_per_session = models.PositiveSmallIntegerField(default=100, verbose_name="Количество запросов за сессию")
    is_active = models.BooleanField(default=True, verbose_name="Парсинг активирован")

    datetime_last_parsed = models.DateTimeField(null=True, blank=True,
                                                verbose_name="Дата последнего успешного парсинга")

    def __str__(self):
        return f"Запрос {SocialNetworkAccount.SOCIAL_NETWORKS[self.social_network]} - {self.name}"


# Telegram
class TelegramAuthKey(models.Model):
    class Meta:
        verbose_name = "Telegram - ключ"
        verbose_name_plural = "Telegram - ключи"

    name = models.CharField(max_length=100, verbose_name="Название")
    api_id = models.PositiveIntegerField(unique=True, verbose_name="API ID (my.telegram.org)")
    api_hash = models.CharField(max_length=64, unique=True, verbose_name="API Key (my.telegram.org)")
    string_session = models.CharField(max_length=1000, null=True, blank=True, verbose_name="String Session (generated)")

    is_active = models.BooleanField(default=True, verbose_name="Активен")

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменнеия")

    def __str__(self):
        return f"Telegram - доступ - {self.name} ({self.api_id})"


# Instagram
class InstagramLoginPass(models.Model):
    class Meta:
        verbose_name = "Instagram - доступ"
        verbose_name_plural = "Instagram - доступ"

    login = models.CharField(max_length=1000, verbose_name='Логин аккаунта')
    password = models.CharField(max_length=1000, verbose_name='Пароль аккаунта')

    csrftoken = models.CharField(max_length=1000, default='VQZCf2glmiox3V2eBY5GYYVe0Ccaahso', blank=True, null=True, verbose_name='CSRF токен')
    ds_user_id = models.BigIntegerField(default='27655705617', null=True, blank=True, verbose_name='UserID')
    rur = models.CharField(max_length=1000, default='ATN', blank=True, null=True, verbose_name='Некая META')
    sessionid = models.CharField(max_length=1000, default='27655705617%3AhtsX9fZJbhBash%3A17', blank=True, null=True, verbose_name='ID Сессии')
    mid = models.CharField(max_length=1000, default="X3MtfQAEAAEMDbQ5Qaq55lCDlKmn", blank=True, null=True, verbose_name='Некое ID')

    is_active = models.BooleanField(default=True, verbose_name="Активен")

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменнеия")

    def __str__(self):
        return f"Логин-пароль Инстаграм - {self.login}"


# VK
class VKLoginPass(models.Model):
    class Meta:
        verbose_name = "VK - доступ"
        verbose_name_plural = "VK - доступ"

    NEWS_FEED_LIMIT = 1000
    WALL_GET = 5000

    NEWS_FEED_MAX_COUNT = 200
    WALL_GET_MAX_COUNT = 100

    API_V = 5.92

    app_id = models.CharField(max_length=100, verbose_name='APP ID приложения')
    login = models.CharField(max_length=100, verbose_name='Логин аккаунта')
    password = models.CharField(max_length=100, verbose_name='Пароль аккаунта')

    is_active = models.BooleanField(default=True, verbose_name="Активен")

    news_feed_limit_used = models.PositiveSmallIntegerField(default=0, verbose_name="News Feed запросов использовано")
    wall_get_limit_used = models.PositiveSmallIntegerField(default=0, verbose_name="Wall Get запросов использовано")

    datetime_news_feed_limit_reached = models.DateTimeField(default=None, null=True, blank=True, verbose_name="Дата, когда достигнут лимит по News Feed")
    datetime_wall_get_limit_reached = models.DateTimeField(default=None, null=True, blank=True, verbose_name="Дата, когда достигнут лимит по Wall Get")

    datetime_news_feed_updated = models.DateTimeField(default=None, null=True, blank=True, verbose_name="Дата, когда обновлено количество запросов по News Feed")
    datetime_wall_get_updated = models.DateTimeField(default=None, null=True, blank=True, verbose_name="Дата, когда обновлено количество запросов по Wall Get")

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменнеия")

    def __str__(self):
        return f"Логин-пароль VK - {self.login}"


# YouTube
class YouTubeAuthToken(models.Model):
    class Meta:
        verbose_name = "YouTube - доступ"
        verbose_name_plural = "YouTube - доступ"

    API_V = 3
    SERVICE_NAME = "youtube"

    token_id = models.CharField(null=True, blank=True, max_length=100, verbose_name='TOKEN ID')

    is_active = models.BooleanField(default=True, verbose_name="Активен")

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменнеия")

    videos_limit_used = models.PositiveSmallIntegerField(default=0, verbose_name="Get video запросов использовано")
    datetime_videos_limit_reached = models.DateTimeField(default=None, null=True, blank=True, verbose_name="Дата, когда достигнут лимит по get video")
    datetime_videos_updated = models.DateTimeField(default=None, null=True, blank=True, verbose_name="Дата, когда обновлено количество запросов по get video")

    def __str__(self):
        return f"YouTube token id - {self.token_id}"
