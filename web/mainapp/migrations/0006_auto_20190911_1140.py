# Generated by Django 2.2.4 on 2019-09-11 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_scraprules'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'News'), (1, 'Interview'), (2, 'Article'), (3, 'Blogs/Opinions')], default=0, verbose_name='Тип публикации (в основном для Тенгри)'),
        ),
        migrations.AlterField(
            model_name='scraprules',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'title'), (1, 'text'), (2, 'author'), (3, 'datetime'), (4, 'tags'), (5, 'categories'), (6, 'num_views'), (7, 'num_likes'), (8, 'num_comments'), (9, 'num_shares')], verbose_name='Тип поля'),
        ),
    ]