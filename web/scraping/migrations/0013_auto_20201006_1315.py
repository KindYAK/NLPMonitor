# Generated by Django 2.2.13 on 2020-10-06 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0012_auto_20201001_1234'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instagramloginpass',
            options={'verbose_name': 'Instagram - доступ', 'verbose_name_plural': 'Instagram - доступ'},
        ),
        migrations.AlterModelOptions(
            name='telegramauthkey',
            options={'verbose_name': 'Telegram - ключ', 'verbose_name_plural': 'Telegram - ключи'},
        ),
    ]
