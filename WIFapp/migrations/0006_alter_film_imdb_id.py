# Generated by Django 4.2.6 on 2023-11-22 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WIFapp', '0005_person_photo_path_alter_film_tmdb_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='imdb_id',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]