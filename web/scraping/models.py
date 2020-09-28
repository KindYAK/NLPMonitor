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
        (0, 'Неверифицированный'),
        (1, 'Верифицированный'),
        (2, 'Непроверенный'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    social_network = models.PositiveSmallIntegerField(choices=SOCIAL_NETWORKS, verbose_name="Соц. сеть")
    url = models.CharField(max_length=1000, verbose_name="URL аккаунта (ссылка)")
    account_id = models.CharField(max_length=1000, verbose_name="ID аккаунта")
    is_private = models.BooleanField(default=False, verbose='Конфеденциальность аккаунта')
    is_valid = models.PositiveSmallIntegerField(default=2, max_length=1000, choices=ACCOUNT_STATUSES,
                                                verbose='Состояние аккаунта')

    priority_rate = models.FloatField(default=50, verbose_name="Приоритет парсинга (от 0 до 100")
    is_active = models.BooleanField(default=True, verbose_name="Парсинг активирован")

    datetime_last_parsed = models.DateTimeField(null=True, blank=True, verbose_name="Дата последнего успешного парсинга")


# Telegram
class TelegramAuthKey(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    api_id = models.PositiveIntegerField(unique=True, verbose_name="API ID (my.telegram.org)")
    api_hash = models.CharField(max_length=64, unique=True, verbose_name="API Key (my.telegram.org)")
    string_session = models.CharField(max_length=1000, null=True, blank=True, verbose_name="String Session (generated)")

    is_active = models.BooleanField(default=True, verbose_name="Активен")

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменнеия")
