# Generated by Django 2.2.13 on 2020-10-06 10:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0013_auto_20201006_1315'),
    ]

    operations = [
        migrations.CreateModel(
            name='VKLoginPass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_id', models.CharField(max_length=100, verbose_name='APP ID приложения')),
                ('login', models.CharField(max_length=100, verbose_name='Логин аккаунта')),
                ('password', models.CharField(max_length=100, verbose_name='Пароль аккаунта')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('news_feed_limit_used', models.PositiveSmallIntegerField(default=0, verbose_name='News Feed запросов использовано')),
                ('wall_get_limit_used', models.PositiveSmallIntegerField(default=0, verbose_name='Wall Get запросов использовано')),
                ('datetime_news_feed_limit_reached', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата когда достигнут лимит по News Feed')),
                ('datetime_wall_get_limit_reached', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата когда достигнут лимит по Wall Get')),
                ('datetime_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('datetime_modified', models.DateTimeField(auto_now=True, verbose_name='Дата последнего изменнеия')),
            ],
            options={
                'verbose_name': 'VK - доступ',
                'verbose_name_plural': 'VK - доступ',
            },
        ),
    ]
