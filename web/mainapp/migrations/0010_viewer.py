# Generated by Django 2.2.4 on 2019-11-29 10:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('evaluation', '0006_remove_topicideval_topic_modelling_name'),
        ('mainapp', '0009_contentloader_expert'),
    ]

    operations = [
        migrations.CreateModel(
            name='Viewer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic_modelling_names', picklefield.fields.PickledObjectField(editable=False, null=True, verbose_name='Название тематических моделирований')),
                ('criterions', models.ManyToManyField(to='evaluation.EvalCriterion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, unique=True, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователь',
            },
        ),
    ]
