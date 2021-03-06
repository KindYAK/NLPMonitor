# Generated by Django 2.2.10 on 2020-02-26 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('evaluation', '0009_auto_20200226_1245'),
        ('mainapp', '0025_remove_document_topics'),
    ]

    operations = [
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SmallIntegerField(default=0)),
                ('title', models.CharField(max_length=50, verbose_name='Заголовок')),
                ('icon_class', models.CharField(max_length=50, verbose_name='Class иконки')),
                ('index', models.SmallIntegerField(default=0, verbose_name='Порядковый номер')),
                ('criterion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluation.EvalCriterion')),
            ],
            options={
                'verbose_name': 'Виджет',
                'verbose_name_plural': 'Виджеты',
            },
        ),
        migrations.CreateModel(
            name='DashboardPreset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название')),
                ('topic_modelling_name', models.CharField(max_length=100, verbose_name='Название ТМ')),
                ('corpus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Corpus', verbose_name='Корпус')),
                ('widgets', models.ManyToManyField(blank=True, to='dashboard.Widget')),
            ],
            options={
                'verbose_name': 'Пресет дашборда',
                'verbose_name_plural': 'Пресеты дашбордов',
            },
        ),
    ]
