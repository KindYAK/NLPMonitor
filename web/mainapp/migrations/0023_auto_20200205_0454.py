# Generated by Django 2.2.8 on 2020-02-04 22:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0022_auto_20200204_1942'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='document',
            unique_together={('source', 'date', 'title')},
        ),
    ]
