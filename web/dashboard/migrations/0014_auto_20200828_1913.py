# Generated by Django 2.2.13 on 2020-08-28 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_auto_20200515_1718'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monitoringobject',
            options={'verbose_name': 'Объект мониторинга', 'verbose_name_plural': 'Объекты мониторинга'},
        ),
        migrations.CreateModel(
            name='MonitoringObjectsGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Название')),
                ('monitoring_objects', models.ManyToManyField(to='dashboard.MonitoringObject')),
            ],
            options={
                'verbose_name': 'Группа объектов мониторинга',
                'verbose_name_plural': 'Группы объектов мониторинга',
            },
        ),
    ]