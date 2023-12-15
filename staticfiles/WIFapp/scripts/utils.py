from django.db.models import Count, Q

from configparser import ConfigParser
import requests
import json

from criterion_titles import criterion_titles
from bechdel_films import yes_bechdel_films, not_bechdel_films

import sys
import os
sys.path.append('/Users/tarakirkland/Documents/code/womeninfilm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WIF.settings')

import django
django.setup()

from WIFapp.models import Film, Person, Genre, Star, Crew

"""
this script starts off with every film in the criterion collection,
exported from https://www.imdb.com/list/ls087831830/?sort=list_order,asc&st_dt=&mode=simple&page=1&ref_=ttls_vw_smp
and imports relevant films
"""


# authentication
cfg = ConfigParser()
cfg.read('config.cfg')
API_KEY = '?api_key=' + cfg['tmdb']['key'].strip('\"')
HEADERS = {"accept": "application/json", "Authorization": cfg['tmdb']['auth']}




def get_film_details(tmdb_id):
    url = f'https://api.themoviedb.org/3/movie/{tmdb_id}{API_KEY}&language=en-US'
    return requests.get(url, headers=HEADERS).json()


# PEOPLE TABLE
def add_to_people(person):
    gender_map = {1: 'female', 2: 'male'}
    person_obj, created = Person.objects.get_or_create(
        id = person['id'],
        defaults = {'name': person['name'], 'gender': gender_map.get(person['gender'], 'other')}
    )
    return person_obj


# STARS TABLE
def get_film_stars(tmdb_id):
    url = f'https://api.themoviedb.org/3/movie/{tmdb_id}/credits{API_KEY}'
    try:
        stars = requests.get(url, headers=HEADERS).json()['cast'][:3]
        film_obj = Film.objects.get(tmdb_id=tmdb_id)

        for star in stars:
            person_obj = add_to_people(star)
            Star.objects.get_or_create(film=film_obj, person=person_obj)
    except json.JSONDecodeError:
        print("Failed to decode JSON from response")


# CREW TABLE
def get_film_crew(tmdb_id):
    url = f'https://api.themoviedb.org/3/movie/{tmdb_id}/credits{API_KEY}'
    crew = requests.get(url, headers=HEADERS).json()['crew'][:50]
    film_obj = Film.objects.get(tmdb_id=tmdb_id)
    
    jobs = ['Director', 'Editor', 'Writer', 'Screenplay', 'Novel']

    for crewmember in crew:
        if crewmember['job'] in jobs:
            person_obj = add_to_people(crewmember)
            Crew.objects.get_or_create(film=film_obj, person=person_obj, job=crewmember['job'])


# GENRES TABLE
def get_genres():
    url = 'https://api.themoviedb.org/3/genre/movie/list{API_KEY}&language=en'.format(API_KEY=API_KEY)
    genres = requests.get(url, headers=HEADERS).json()['genres']
    for genre in genres:
        Genre.objects.update_or_create(
            id=genre['id'],
            defaults={'name': genre['name']}
        )


# FILMS TABLE
def add_film_to_films(film_details, source=None):
    # check if imdb_id exists and isn't empty
    if 'imdb_id' in film_details and film_details['imdb_id'] and film_details['imdb_id'] != 'null' and film_details['vote_average'] != 0.0:
        year = film_details.get('release_date', '')[:4]
        # set value if year is an empty string
        year = int(year) if year.isdigit() else None

        film_obj, created = Film.objects.get_or_create(
            tmdb_id = film_details['id'],
            defaults = {
                'title': film_details['title'],
                'imdb_id': film_details['imdb_id'],
                'year': year,
                'poster_path': film_details['poster_path'],
                'synopsis': film_details['overview'],
                'tmdb_rating': film_details['vote_average'],
            }
        )
        if created:
            genre_ids = [genre['id'] for genre in film_details['genres']]
            genres = Genre.objects.filter(id__in=genre_ids)
            film_obj.genres.set(genres)
            film_obj.source = source
        return True
    return False # if not added to database





def update_woman_directed_status(film):
    film.woman_directed = Crew.objects.filter(film=film, job='Director', person__gender='female').exists()

def update_starring_women_status(film):
    women_stars_count = film.star_set.filter(person__gender='female').count()
    film.starring_women = women_stars_count >= 2

def update_women_written_status(film):
    film.women_written = Crew.objects.filter(
            Q(film=film) & 
            (Q(job='Writer') | Q(job='Screenplay') | Q(job='Novel')) &
            Q(person__gender='female')
        ).exists()

def update_woman_primary_star_status(film):
    primary_star = film.star_set.first()
    if primary_star is not None:
        film.woman_primary_star = primary_star.person.gender.lower() == 'female'

def update_passes_bechdel_status(film):
    if film.imdb_id[2:] in yes_bechdel_films:
        film.passes_bechdel = True
    elif film.imdb_id[2:] in not_bechdel_films:
        film.passes_bechdel = False

# delete movies & related objects that don't have enough women involved
def remove_testosterone():
    Film.objects.filter(starring_women=False, women_written=False, woman_directed=False, woman_primary_star=False).delete()
    Person.objects.annotate(num_stars=Count('star'), num_crew=Count('crew')).filter(num_stars=0, num_crew=0).delete()


# delete movies that really shouldn't be here. only run this if resetting the db from scratch.
# so far this is soft-core porn mostly, that tmdb doesn't consider "adult" but is just garbage.
# also need to delete really short things, like a sade music video
def cleanup():
    delete_films = [7282, 8772, 1095, 7288]
    films_to_delete = Film.objects.filter(pk__in=delete_films)

    if films_to_delete.exists():
        films_to_delete.delete()[0]  # delete() returns a tuple (num_deleted, {model: count})


def add_person_metadata():
    # only include people that don't have a biography, assume they haven't been updated yet.
    persons_without_biography = Person.objects.filter(biography__isnull=True)

    for person in persons_without_biography:
        person_id = person.id
        url = f"https://api.themoviedb.org/3/person/{person_id}{API_KEY}"
        response = requests.get(url, headers=HEADERS).json()
        if response.get('imdb_id'):
            person.biography = response.get('biography', '')
            person.imdb_id = response.get('imdb_id', '')
            if response.get('profile_path'):
                person.photo_path = response['profile_path']
            person.save()