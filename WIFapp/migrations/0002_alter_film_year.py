# Generated by Django 4.2.6 on 2023-11-18 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WIFapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='year',
            field=models.IntegerField(null=True),
        ),
    ]
