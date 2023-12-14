from django.db.models import Count, Q

from configparser import ConfigParser
import requests
import json

import utils
from bechdel_films import yes_bechdel_films, not_bechdel_films
from criterion_titles import criterion_titles


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


# get list of top films by revenue from TMDB
def tmdb_get_film_ids():
    film_ids = []
    for year in range(START_YEAR, END_YEAR+1):
        for page in range(START_PAGE, END_PAGE+1):
            url = f'https://api.themoviedb.org/3/discover/movie/{API_KEY}&sort_by=revenue.desc&primary_release_year={year}&page={page}&with_original_language=en'
            response = requests.get(url, headers=HEADERS)
            film_data = response.json()['results']
            film_ids.extend([film['id'] for film in film_data])
    return film_ids


# take set of IMDB ids and convert it to a list of tmdb ids
tmdb_ids = set()
def convert_imdbids_to_tmdb_ids(imdb_list):
    for id in imdb_list:
        url = f'https://api.themoviedb.org/3/find/{id}{API_KEY}&external_source=imdb_id'
        response = requests.get(url, headers=HEADERS).json()
        try:
            tmdb_ids.add(response['movie_results'][0]['id'])
        except IndexError:
            continue
    return tmdb_ids


def update_films(film_id):
    film = Film.objects.get(pk=film_id)

    utils.update_woman_directed_status(film)
    utils.update_starring_women_status(film)
    utils.update_women_written_status(film)
    utils.update_woman_primary_star_status(film)
    utils.update_passes_bechdel_status(film)

    film.save()



def main():
    # only run this if the database has been reset
    # get_genres()

    # set an input source for the film_ids (choose one, or append to set)
    film_ids = tmdb_get_film_ids()
    film_ids = convert_imdbids_to_tmdb_ids()
    print(f"Total films: {len(film_ids)}")

    # add films to the database
    for film_id in film_ids:
        film_details = utils.get_film_details(film_id)
        if utils.add_film_to_films(film_details):
            utils.get_film_stars(film_id)
            utils.get_film_crew(film_id)
            print(film_details['title'])
        else:
            print(f'Film {film_id} not added')
        
    # add film metadata to database entries
    for film_id in film_ids:
        update_films(film_id)

    # checks for criteria across all films
    utils.add_person_metadata()
    utils.remove_testosterone()

    # only run if database has been reset
    # cleanup() 

if __name__ == '__main__':
    main()