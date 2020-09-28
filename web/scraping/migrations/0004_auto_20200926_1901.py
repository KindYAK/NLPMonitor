# Generated by Django 2.2.13 on 2020-09-26 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0003_socialnetworkaccount_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='socialnetworkaccount',
            old_name='datatime_last_parsed',
            new_name='datetime_last_parsed',
        ),
        migrations.AddField(
            model_name='telegramauthkey',
            name='name',
            field=models.CharField(default='', max_length=100, verbose_name='Название'),
            preserve_default=False,
        ),
    ]
