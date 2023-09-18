from django.urls import path

from .views import berries_view, pokedex_view, pokemon_view

urlpatterns = [
    path('', pokedex_view, name='pokedex'),
    path('pokemon/<int:pokemon_id>/', pokemon_view, name='pokemon'),
    path('berries/', berries_view, name='berries'),
]
