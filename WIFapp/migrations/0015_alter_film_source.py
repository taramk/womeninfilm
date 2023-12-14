# Generated by Django 4.2.6 on 2023-12-14 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WIFapp', '0014_film_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='source',
            field=models.CharField(blank=True, choices=[('criterion', 'Criterion Collection'), ('letterboxd_250', 'Letterboxd Top 250 Narrative Films'), ('natl_registry', 'National Film Registry'), ('tmdb_by_revenue', 'TMDB Top Film by Revenue')], max_length=100, null=True),
        ),
    ]
