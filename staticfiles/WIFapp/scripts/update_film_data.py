from django.db.models import Count, Q
from configparser import ConfigParser
import requests
import json

from bechdel_films import not_bechdel_films

import sys
import os
sys.path.append('/Users/tarakirkland/Documents/code/taramk/WIF_container/WIFapp/scripts')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WIF.settings')

import django
django.setup()

from WIFapp.models import Film, Person, Genre, Star, Crew
from django.core.exceptions import ObjectDoesNotExist

# testing (credits, film_details)
# https://api.themoviedb.org/3/movie/1891/credits?api_key=225b0e89130212d174c850b0461d683d
# https://api.themoviedb.org/3/movie/1891?api_key=225b0e89130212d174c850b0461d683d

# profile photo
# https://api.themoviedb.org/3/person/30/images?api_key=225b0e89130212d174c850b0461d683d


# authentication
cfg = ConfigParser()
cfg.read('config.cfg')
API_KEY = '?api_key=' + cfg['tmdb']['key'].strip('\"')
HEADERS = {"accept": "application/json", "Authorization": cfg['tmdb']['auth']}



# imdb id, biography, photo
# def add_person_metadata():
#     for person in Person.objects.all():
#         person_id = person.id
#         url = f"https://api.themoviedb.org/3/person/{person_id}{API_KEY}"
#         response = requests.get(url, headers=HEADERS).json()
#         person.biography = response['biography']
#         person.imdb_id = response['imdb_id']
#         if response['photo_path'] and response['photo_path'] is not '':
#             person.photo_path = response['profile_path']
#         print(person.name)
#         person.save()


def add_to_people(person):
    gender_map = {1: 'female', 2: 'male'}
    person_obj, created = Person.objects.get_or_create(
        id = person['id'],
        defaults = {'name': person['name'], 'gender': gender_map.get(person['gender'], 'other')}
    )
    return person_obj

def get_writers():
    films = Film.objects.all()
    for film in films:
        url = f'https://api.themoviedb.org/3/movie/{film.tmdb_id}/credits{API_KEY}'
        crew = requests.get(url, headers=HEADERS).json()['crew'][:50]
        
        jobs = ['Screenplay', 'Novel']

        for crewmember in crew:
            if crewmember['job'] in jobs:
                person_obj = add_to_people(crewmember)
                print(f"Person Object: {person_obj}, Type: {type(person_obj)}")  # Debugging print
                print(f"Film ID: {film.id}, Type: {type(film)}")  # Debugging print
                Crew.objects.get_or_create(film=film, person=person_obj, job=crewmember['job'])


def add_person_metadata():
    # only include people that don't have a biography, assume they haven't been updated yet.
    persons_without_biography = Person.objects.filter(biography__isnull=True) | Person.objects.filter(biography='')

    for person in persons_without_biography:
        person_id = person.id
        url = f"https://api.themoviedb.org/3/person/{person_id}{API_KEY}"
        response = requests.get(url, headers=HEADERS).json()
        person.biography = response['biography']
        person.imdb_id = response['imdb_id'] if response['imdb_id'] else None
        print(f"imdb id: {person.imdb_id} for {person.name}")
        if 'profile_path' in response and response['profile_path']:
            person.photo_path = response['profile_path']
        print(person.name)
        person.save()


def update_women_written_status():
    films = Film.objects.all()
    for film in films:
        women_writers_exist = Crew.objects.filter(
                Q(film=film) & 
                (Q(job='Writer') | Q(job='Screenplay') | Q(job='Novel')) &
                Q(person__gender='female')
            ).exists()

        film.women_written = women_writers_exist
        print(film.women_written)
        film.save()

# maybe audit this to see if primary_star_status is ever None/null. if so, that means there are no stars.
def update_woman_primary_star_status():
    for film in Film.objects.all():
        primary_star = film.star_set.first()

        if primary_star is not None:
            film.woman_primary_star = primary_star.person.gender.lower() == 'female'

        film.save()
        print(f"Updated film: {film.title}, Woman Primary Star: {film.woman_primary_star}")

def main():
    # get_writers()
    # add_person_metadata()
    # update_women_written_status()
    update_woman_primary_star_status()



if __name__ == '__main__':
    main()