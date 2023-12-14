from django.db import models
from django.db.models import Q



class Person(models.Model):
    name = models.CharField(max_length=255, null=False)
    gender = models.CharField(max_length=255, null=True, blank=True)
    photo_path = models.CharField(max_length=255, null=True)
    imdb_id = models.CharField(max_length=50, null=True, blank=False, unique=True)
    biography = models.TextField(blank=True, null=True, default=None)


class Film(models.Model):
    SOURCES = (
        ('criterion', 'Criterion Collection'),
        ('letterboxd_250', 'Letterboxd Top 250 Narrative Films'),
        ('natl_registry', 'National Film Registry'),
        ('tmdb_by_revenue', 'TMDB Top Film by Revenue')
    )

    title = models.CharField(max_length=255, null=False)
    tmdb_id = models.IntegerField(null=True, blank=True, unique=True)
    imdb_id = models.CharField(max_length=50, null=True, blank=False, unique=True)
    year = models.IntegerField(null=True, db_index=True)
    starring_women = models.BooleanField(null=True, default=None, db_index=True)
    woman_directed = models.BooleanField(null=True, default=None, db_index=True)
    passes_bechdel = models.BooleanField(null=True, default=None, db_index=True)
    women_written = models.BooleanField(null=True, default=None, db_index=True)
    woman_primary_star = models.BooleanField(null=True, default=None, db_index=True)
    genres = models.ManyToManyField('Genre', blank=True, db_index=True)
    poster_path = models.CharField(max_length=255, null=True)
    tmdb_rating = models.DecimalField(null=True, blank=True, max_digits=3, decimal_places=1)
    synopsis = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True, choices=SOURCES)

    def get_directors(self):
        directors = Crew.objects.filter(film=self, job='Director').select_related('person')
        return [(director.person.name, director.person.id) for director in directors]
    
    def get_writers(self):
        writers = Crew.objects.filter(
            Q(film=self) & 
            (Q(job='Writer') | Q(job='Screenplay') | Q(job='Novel'))
        ).select_related('person')

        writers_dict = {writer.person.id: (writer.person.name, writer.person.id) for writer in writers}
        return list(writers_dict.values())
    
    def get_stars(self):
        return [(star.person.name, star.person.id) for star in self.star_set.all()]

    def get_genres(self):
        return [genre.name for genre in self.genres.all()]




class Genre(models.Model):
    name = models.CharField(max_length=255, null=False)


class Star(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)


class Crew(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    job = models.CharField(max_length=255, null=False)