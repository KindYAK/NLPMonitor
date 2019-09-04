# Generated by Django 2.2.4 on 2019-09-04 05:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_auto_20190826_1729'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScrapRules',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SmallIntegerField(choices=[(0, 'title'), (1, 'text'), (2, 'author'), (3, 'date'), (4, 'tags'), (5, 'categories'), (6, 'num_views'), (7, 'num_likes'), (8, 'num_comments'), (8, 'num_shares')], verbose_name='Тип поля')),
                ('selector', models.CharField(max_length=500, verbose_name='CSS селектор')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Source', verbose_name='Источник')),
            ],
            options={
                'verbose_name': 'Правило скрапинга',
                'verbose_name_plural': 'Правила скрапинга',
                'unique_together': {('source', 'type')},
            },
        ),
    ]