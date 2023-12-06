from django.db.models import Count, Q

from configparser import ConfigParser
import requests
import json

from bechdel_films import yes_bechdel_films, not_bechdel_films

import sys
import os
sys.path.append('/Users/tarakirkland/Documents/code/taramk/capstone')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WIF.settings')

import django
django.setup()

from WIFapp.models import Film, Person, Genre, Star, Crew

"""
current tally per year (starting amount, then later filtered down)
1960s - 100
1970s - 100
1980s - 200
1990s - 200
2000s - 240
2010s - 240
2020-22 - 240
"""

# customizable constants
START_YEAR = 2023
END_YEAR = 2023
START_PAGE = 1
END_PAGE = 12 # 20 per page, inclusive

# authentication
cfg = ConfigParser()
cfg.read('config.cfg')
API_KEY = '?api_key=' + cfg['tmdb']['key'].strip('\"')
HEADERS = {"accept": "application/json", "Authorization": cfg['tmdb']['auth']}


def get_film_ids():
    film_ids = []
    for year in range(START_YEAR, END_YEAR+1):
        for page in range(START_PAGE, END_PAGE+1):
            url = f'https://api.themoviedb.org/3/discover/movie/{API_KEY}&sort_by=revenue.desc&primary_release_year={year}&page={page}&with_original_language=en'
            response = requests.get(url, headers=HEADERS)
            film_data = response.json()['results']
            film_ids.extend([film['id'] for film in film_data])
    return film_ids


def get_film_details(film_id):
    url = f'https://api.themoviedb.org/3/movie/{film_id}{API_KEY}&language=en-US'
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
def get_film_stars(film_id):
    url = f'https://api.themoviedb.org/3/movie/{film_id}/credits{API_KEY}'
    try:
        stars = requests.get(url, headers=HEADERS).json()['cast'][:3]
        film_obj = Film.objects.get(tmdb_id=film_id)

        for star in stars:
            person_obj = add_to_people(star)
            Star.objects.get_or_create(film=film_obj, person=person_obj)
    except json.JSONDecodeError:
        print("Failed to decode JSON from response")


# CREW TABLE
def get_film_crew(film_id):
    url = f'https://api.themoviedb.org/3/movie/{film_id}/credits{API_KEY}'
    crew = requests.get(url, headers=HEADERS).json()['crew'][:50]
    film_obj = Film.objects.get(tmdb_id=film_id)
    
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
def add_film_to_films(film_details):
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
                'tmdb_rating': film_details['vote_average']
            }
        )
        if created:
            genre_ids = [genre['id'] for genre in film_details['genres']]
            genres = Genre.objects.filter(id__in=genre_ids)
            film_obj.genres.set(genres)
        return True
    return False # if not added to database


def update_woman_directed_status(film_id):
    film = Film.objects.get(pk=film_id)
    film.woman_directed = Crew.objects.filter(film=film, job='Director', person__gender='female').exists()
    film.save()


def update_starring_women_status(film_id):
    film = Film.objects.get(pk=film_id)
    women_stars_count = film.star_set.filter(person__gender='female').count()
    film.starring_women = women_stars_count >= 2
    film.save()


def update_women_written_status(film_id):
    film = Film.objects.get(pk=film_id)

    women_writers_exist = Crew.objects.filter(
            Q(film=film) & 
            (Q(job='Writer') | Q(job='Screenplay') | Q(job='Novel')) &
            Q(person__gender='female')
        ).exists()

    film.women_written = women_writers_exist
    film.save()


def update_woman_primary_star_status(film_id):
    film = Film.objects.get(pk=film_id)

    primary_star = film.star_set.first()
    if primary_star is not None:
        film.woman_primary_star = primary_star.person.gender.lower() == 'female'
    film.save()


def update_passes_bechdel_status(film_id):
    film = Film.objects.get(pk=film_id)

    if film.imdb_id[2:] in yes_bechdel_films:
        film.passes_bechdel = True
    elif film.imdb_id[2:] in not_bechdel_films:
        film.passes_bechdel = False

    film.save()


# delete movies that don't have enough women involved from the database
def remove_testosterone():
    # Delete films
    Film.objects.filter(starring_women=False, women_written=False, woman_directed=False, woman_primary_star=False).delete()
    # Delete persons with no film links
    Person.objects.annotate(num_stars=Count('star'), num_crew=Count('crew')).filter(num_stars=0, num_crew=0).delete()


# delete movies that really shouldn't be here. only run this if resetting the db from scratch.
def cleanup():
    delete_films = [7282, 8772]
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




def main():
    # get_genres() # only run this if the database is empty
    film_ids = get_film_ids()
    print(f"Total films: {len(film_ids)}")

    # add films to the database
    for film_id in film_ids:
        film_details = get_film_details(film_id)
        if add_film_to_films(film_details):
            get_film_stars(film_id)
            get_film_crew(film_id)
            print(film_details['title'])
        else:
            print(f'Film {film_id} not added')
        
    # add film metadata to database entries
    for film_id in film_ids:
        update_woman_directed_status(film_id)
        update_starring_women_status(film_id)
        update_women_written_status(film_id)
        update_passes_bechdel_status(film_id)
        update_woman_primary_star_status(film_id)

    # checks for criteria across all films
    add_person_metadata()
    remove_testosterone()
    # cleanup() # only run if database has been reset

if __name__ == '__main__':
    main()