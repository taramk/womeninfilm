# Generated by Django 4.2.6 on 2023-11-28 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WIFapp', '0009_alter_film_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='imdb_id',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='imdb_id',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
