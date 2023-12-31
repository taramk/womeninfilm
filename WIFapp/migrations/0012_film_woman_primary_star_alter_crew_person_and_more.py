# Generated by Django 4.2.6 on 2023-12-03 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WIFapp', '0011_alter_film_genres_alter_film_passes_bechdel_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='woman_primary_star',
            field=models.BooleanField(db_index=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='crew',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='WIFapp.person'),
        ),
        migrations.AlterField(
            model_name='star',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='WIFapp.person'),
        ),
    ]
