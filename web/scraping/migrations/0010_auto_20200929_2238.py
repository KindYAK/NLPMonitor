# Generated by Django 2.2.13 on 2020-09-29 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0009_auto_20200929_1922'),
    ]

    operations = [
        migrations.RenameField(
            model_name='instagramloginpass',
            old_name='csrf_token',
            new_name='csrftoken',
        ),
    ]
