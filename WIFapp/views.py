import random
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.http import HttpResponse, JsonResponse

from .models import Film, Genre, Person, Star, Crew


def index(request):
    genres = Genre.objects.all()
    default_decade = '1980'

    film_data = get_filtered_shuffled_films(default_decade)
    return render(request, "WIFapp/index.html", {'films': film_data, 'genres': genres})



def filter_films(request):
    decade = request.GET.get('decade', '1980')
    genre_ids = request.GET.get('genres', '').split(',')
    bechdel_filter = request.GET.get('passes_bechdel', 'false')
    women_written_filter = request.GET.get('women_written', 'false')
    women_directed_filter = request.GET.get('women_directed', 'false')
    sort_by_rating = request.GET.get('sort_by_rating', 'false') 

    film_data = get_filtered_shuffled_films(decade, genre_ids if genre_ids and genre_ids[0] else None, bechdel_filter == 'true', women_written_filter == 'true', women_directed_filter == 'true', sort_by_rating == 'true')
    return JsonResponse({'films': film_data})



def get_filtered_shuffled_films(decade, genre_ids=None, passes_bechdel=False, women_written=False, women_directed=False, sort_by_rating=False):
    start_year = int(decade)
    end_year = start_year + 10

    films_query = Film.objects.filter(
        year__gte=start_year, year__lt=end_year,
        woman_primary_star=True
    ).prefetch_related('genres', 'star_set__person')

    if genre_ids:
        films_query = films_query.filter(genres__id__in=genre_ids)
    
    if passes_bechdel:
        films_query = films_query.filter(passes_bechdel=True)

    if women_written:
        films_query = films_query.filter(women_written=True)

    if women_directed:
        films_query = films_query.filter(woman_directed=True)

    if sort_by_rating:
        films_query = films_query.order_by('-tmdb_rating')

    films_list = list(films_query.distinct())
    if not sort_by_rating:
        random.shuffle(films_list)

    return [
        {
            'id': film.id,
            'title': film.title,
            'poster_path': film.poster_path,
        }
        for film in films_list
    ]


def about(request):
    return render(request, "WIFapp/about.html")



def actors_view(request):
    female_actors = Person.objects.filter(
        gender='female', 
        star__isnull=False
    ).annotate(
        movie_count=Count('star')
    ).order_by(
        '-movie_count'
    )[:200]

    context = {
        'title': 'Female Actors',
        'people': female_actors
    }
    return render(request, 'WIFapp/person_list.html', context)


def directors_view(request):
    female_directors = Person.objects.filter(
        gender='female',
        crew__job='Director'
    ).annotate(
        movie_count=Count('crew')
    ).order_by(
        '-movie_count'
    )[:100]  # Limit to 100 results

    context = {
        'title': 'Female Directors',
        'people': female_directors
    }
    return render(request, 'WIFapp/person_list.html', context)


def writers_view(request):
    female_writers = Person.objects.filter(
        gender='female',
        crew__job='Writer'
    ).annotate(
        movie_count=Count('crew')
    ).order_by(
        '-movie_count'
    )[:100]  # Limit to 100 results

    context = {
        'title': 'Female Writers',
        'people': female_writers
    }
    return render(request, 'WIFapp/person_list.html', context)



def person_view(request, person_id):
    person = get_object_or_404(Person, pk=person_id)

    starred_films = Star.objects.filter(person=person).select_related('film')
    directed_films = Crew.objects.filter(person=person, job='Director').select_related('film')
    written_films = Crew.objects.filter(person=person, job='Writer').select_related('film')

    context = {
        'person': person,
        'starred_films': [star.film for star in starred_films],
        'directed_films': [crew.film for crew in directed_films],
        'written_films': [crew.film for crew in written_films]
    }
    return render(request, 'WIFapp/person.html', context)



def film_view(request, film_id):
    film = get_object_or_404(Film, pk=film_id)

    context = {
        'film': film,
        'genres': film.get_genres(),
        'stars': film.get_stars(),
        'directors': film.get_directors(),
        'writers': film.get_writers()
    }
    return render(request, 'WIFapp/film.html', context)


def all_women(request):
    films = Film.objects.filter(
        starring_women=True,
        woman_directed=True,
        women_written=True,
        woman_primary_star=True
    ).order_by('-tmdb_rating')
    return render(request, 'WIFapp/all_women.html', {'films': films})