# Generated by Django 2.2.13 on 2020-09-29 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0007_merge_20200929_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialnetworkaccount',
            name='is_valid',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Непроверенный'), (1, 'Верифицированный'), (2, 'Неверифицированный')], default=1, verbose_name='Состояние аккаунта'),
        ),
        migrations.AlterField(
            model_name='socialnetworkaccount',
            name='num_followers',
            field=models.BigIntegerField(blank=True, default=None, null=True, verbose_name='Количество подписчиков'),
        ),
        migrations.AlterField(
            model_name='socialnetworkaccount',
            name='num_follows',
            field=models.BigIntegerField(blank=True, default=None, null=True, verbose_name='Количество подписок'),
        ),
    ]
