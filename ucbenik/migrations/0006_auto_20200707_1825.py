# Generated by Django 3.0.7 on 2020-07-07 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ucbenik', '0005_characterdatamen_characterdatawomen'),
    ]

    operations = [
        migrations.AddField(
            model_name='characterdatamen',
            name='hair_type',
            field=models.CharField(default='short_hair', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='characterdatawomen',
            name='hair_type',
            field=models.CharField(default='bun', max_length=30),
            preserve_default=False,
        ),
    ]
