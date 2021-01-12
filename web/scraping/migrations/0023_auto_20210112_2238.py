# Generated by Django 2.2.13 on 2021-01-12 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0022_auto_20201014_0024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monitoringquery',
            name='social_network',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Facebook'), (1, 'VK'), (2, 'Twitter'), (3, 'Instagram'), (4, 'Telegram'), (5, 'YouTube')], verbose_name='Соц. сеть'),
        ),
        migrations.AlterField(
            model_name='socialnetworkaccount',
            name='social_network',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Facebook'), (1, 'VK'), (2, 'Twitter'), (3, 'Instagram'), (4, 'Telegram'), (5, 'YouTube')], verbose_name='Соц. сеть'),
        ),
    ]