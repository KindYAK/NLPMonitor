# Generated by Django 2.2.13 on 2020-09-26 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramAuthKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_id', models.PositiveIntegerField(unique=True, verbose_name='API ID (my.telegram.org)')),
                ('api_hash', models.CharField(max_length=64, unique=True, verbose_name='API Key (my.telegram.org)')),
                ('string_session', models.CharField(blank=True, max_length=1000, null=True, verbose_name='String Session (generated)')),
            ],
        ),
        migrations.CreateModel(
            name='SocialAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_network', models.PositiveSmallIntegerField(choices=[(0, 'Facebook'), (1, 'VK'), (2, 'Twitter'), (3, 'Instagram'), (4, 'Telegram'), (5, 'Youtube')], verbose_name='Соц. сеть')),
                ('url', models.CharField(max_length=1000, verbose_name='URL аккаунта (ссылка)')),
                ('account_id', models.CharField(max_length=1000, verbose_name='ID аккаунта')),
            ],
            options={
                'verbose_name': 'Аккаунт соц. сети',
                'verbose_name_plural': 'Аккаунты соц. сетей',
                'unique_together': {('account_id', 'social_network'), ('url', 'social_network')},
            },
        ),
    ]
