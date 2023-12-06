from django.contrib import admin
from .models import Film

class FilmAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'year', 'tmdb_rating')  # Fields to display in the list view
    search_fields = ('title', 'year')  # Fields to be searched
    list_filter = ('year', 'genres')  # Filters you can use on the side

admin.site.register(Film, FilmAdmin)