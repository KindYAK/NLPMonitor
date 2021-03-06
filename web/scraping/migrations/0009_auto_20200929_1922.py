# Generated by Django 2.2.13 on 2020-09-29 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0008_auto_20200929_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='instagramloginpass',
            name='csrf_token',
            field=models.CharField(blank=True, default='VQZCf2glmiox3V2eBY5GYYVe0Ccaahso', max_length=1000, null=True, verbose_name='CSRF токен'),
        ),
        migrations.AddField(
            model_name='instagramloginpass',
            name='ds_user_id',
            field=models.BigIntegerField(blank=True, default='27655705617', null=True, verbose_name='UserID'),
        ),
        migrations.AddField(
            model_name='instagramloginpass',
            name='mid',
            field=models.CharField(blank=True, default='X3MtfQAEAAEMDbQ5Qaq55lCDlKmn', max_length=1000, null=True, verbose_name='Некое ID'),
        ),
        migrations.AddField(
            model_name='instagramloginpass',
            name='rur',
            field=models.CharField(blank=True, default='ATN', max_length=1000, null=True, verbose_name='Некая META'),
        ),
        migrations.AddField(
            model_name='instagramloginpass',
            name='sessionid',
            field=models.CharField(blank=True, default='27655705617%3AhtsX9fZJbhBash%3A17', max_length=1000, null=True, verbose_name='ID Сессии'),
        ),
    ]
