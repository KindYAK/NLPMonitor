# Generated by Django 2.2.8 on 2020-04-01 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_auto_20200328_0020'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonitoringObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_query', models.CharField(blank=True, max_length=100, null=True, verbose_name='Предмет запроса')),
                ('ner_query', models.CharField(blank=True, max_length=500, null=True, verbose_name='Список сущностей')),
            ],
            options={
                'verbose_name': 'Объекты мониторинга',
                'verbose_name_plural': 'Объекты мониторинга',
            },
        ),
        migrations.RemoveField(
            model_name='widget',
            name='name_query',
        ),
        migrations.RemoveField(
            model_name='widget',
            name='ner_query',
        ),
        migrations.AddField(
            model_name='widget',
            name='monitoring_object',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.MonitoringObject'),
        ),
    ]
