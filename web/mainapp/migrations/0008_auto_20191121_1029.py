# Generated by Django 2.2.4 on 2019-11-21 04:29

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0007_topicgroup_topicid'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='topicgroup',
            unique_together={('name', 'owner', 'topic_modelling_name')},
        ),
    ]
