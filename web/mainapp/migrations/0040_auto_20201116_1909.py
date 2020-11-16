# Generated by Django 2.2.13 on 2020-11-16 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0039_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='subscription_type',
            field=models.SmallIntegerField(choices=[(-1, 'Негатив'), (0, 'Последние новости'), (1, 'Позитив')], verbose_name='Тип подписки'),
        ),
    ]