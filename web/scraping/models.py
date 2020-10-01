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
        (5, "Youtube"),
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

    def __str__(self):
        return f"Аккаунт {self.SOCIAL_NETWORKS[self.social_network]} - {self.name}"


# Telegram
class TelegramAuthKey(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    api_id = models.PositiveIntegerField(unique=True, verbose_name="API ID (my.telegram.org)")
    api_hash = models.CharField(max_length=64, unique=True, verbose_name="API Key (my.telegram.org)")
    string_session = models.CharField(max_length=1000, null=True, blank=True, verbose_name="String Session (generated)")

    is_active = models.BooleanField(default=True, verbose_name="Активен")

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменнеия")

    def __str__(self):
        return f"Ключ телеграм - {self.name} ({self.api_id})"


# Instagram
class InstagramLoginPass(models.Model):
    login = models.CharField(max_length=1000, verbose_name='Логин аккаунта')
    password = models.CharField(max_length=1000, verbose_name='Пароль аккаунта')
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    csrftoken = models.CharField(max_length=1000, default='VQZCf2glmiox3V2eBY5GYYVe0Ccaahso', blank=True, null=True, verbose_name='CSRF токен')
    ds_user_id = models.BigIntegerField(default='27655705617', null=True, blank=True, verbose_name='UserID')
    rur = models.CharField(max_length=1000, default='ATN', blank=True, null=True, verbose_name='Некая META')
    sessionid = models.CharField(max_length=1000, default='27655705617%3AhtsX9fZJbhBash%3A17', blank=True, null=True, verbose_name='ID Сессии')
    mid = models.CharField(max_length=1000, default="X3MtfQAEAAEMDbQ5Qaq55lCDlKmn", blank=True, null=True, verbose_name='Некое ID')

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменнеия")

    def __str__(self):
        return f"Логин-пароль Инстаграм - {self.login}"
