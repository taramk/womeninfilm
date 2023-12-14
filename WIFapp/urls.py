from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about", views.about, name="about"),
    path('filter_films/', views.filter_films, name='filter_films'),
    path('actors/', views.actors_view, name='actors'),
    path('directors/', views.directors_view, name='directors'),
    path('writers/', views.writers_view, name='writers'),
    path('person/<int:person_id>', views.person_view, name="person"),
    path('film/<int:film_id>', views.film_view, name="film"),
    path('all_women', views.all_women, name='all_women')
]