# Generated by Django 2.2.2 on 2019-06-20 07:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_auto_20190620_1312'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='source',
            unique_together={('corpus', 'name')},
        ),
    ]
