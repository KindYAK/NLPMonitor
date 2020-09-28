# Generated by Django 2.2.13 on 2020-09-26 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialNetworkAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_network', models.PositiveSmallIntegerField(choices=[(0, 'Facebook'), (1, 'VK'), (2, 'Twitter'), (3, 'Instagram'), (4, 'Telegram'), (5, 'Youtube')], verbose_name='Соц. сеть')),
                ('url', models.CharField(max_length=1000, verbose_name='URL аккаунта (ссылка)')),
                ('account_id', models.CharField(max_length=1000, verbose_name='ID аккаунта')),
                ('priority_rate', models.FloatField(default=50, verbose_name='Приоритет парсинга (от 0 до 100')),
                ('is_active', models.BooleanField(default=True, verbose_name='Парсинг активирован')),
                ('datatime_last_parsed', models.DateTimeField(blank=True, null=True, verbose_name='Дата последнего успешного парсинга')),
            ],
            options={
                'verbose_name': 'Аккаунт соц. сети',
                'verbose_name_plural': 'Аккаунты соц. сетей',
                'unique_together': {('account_id', 'social_network'), ('url', 'social_network')},
            },
        ),
        migrations.DeleteModel(
            name='SocialAccount',
        ),
        migrations.AddField(
            model_name='telegramauthkey',
            name='datetime_created',
            field=models.DateTimeField(auto_now_add=True, default=None, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='telegramauthkey',
            name='datetime_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата последнего изменнеия'),
        ),
        migrations.AddField(
            model_name='telegramauthkey',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активен'),
        ),
    ]
