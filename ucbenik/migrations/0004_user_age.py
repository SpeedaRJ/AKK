# Generated by Django 3.0.7 on 2020-06-20 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ucbenik', '0003_auto_20200620_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='age',
            field=models.IntegerField(default=99),
        ),
    ]