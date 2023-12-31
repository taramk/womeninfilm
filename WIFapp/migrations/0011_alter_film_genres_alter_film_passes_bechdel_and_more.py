# Generated by Django 4.2.6 on 2023-11-29 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WIFapp', '0010_alter_film_imdb_id_alter_person_imdb_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='genres',
            field=models.ManyToManyField(blank=True, db_index=True, to='WIFapp.genre'),
        ),
        migrations.AlterField(
            model_name='film',
            name='passes_bechdel',
            field=models.BooleanField(db_index=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='film',
            name='starring_women',
            field=models.BooleanField(db_index=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='film',
            name='woman_directed',
            field=models.BooleanField(db_index=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='film',
            name='women_written',
            field=models.BooleanField(db_index=True, default=None, null=True),
        ),
    ]
