# Generated by Django 2.2.10 on 2020-02-26 06:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0024_remove_document_unique_hash'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='topics',
        ),
    ]
