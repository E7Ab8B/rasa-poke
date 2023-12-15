from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import aiohttp

from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render, reverse
from django.views import View

from .utils.requests import (
    retrieve_berries,
    retrieve_berry_items,
    retrieve_multiple_pokemon,
    retrieve_pokemon,
    retrieve_pokemon_list,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)


class PokePaginationMixin:
    """Mixin class for handling pagination in the Pokédex and Berries views."""

    POKE_OFFSET = 20
    POKE_LIMIT = 20

    def get_page_number(self, request: HttpRequest) -> int:
        """Returns expected page number, which should be passed as `page` param."""
        try:
            page_number = int(request.GET['page'])  # pyright: ignore[reportGeneralTypeIssues]
        except (ValueError, KeyError):
            return 1

        return max(page_number, 1)


class PokedexView(PokePaginationMixin, View):
    """View class for displaying the Pokédex."""

    async def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        page_number = self.get_page_number(request)

        try:
            pokemon_list = await retrieve_pokemon_list(
                limit=self.POKE_LIMIT,
                offset=self.POKE_OFFSET * (page_number - 1),
            )
            last_page = pokemon_list['count'] // self.POKE_OFFSET
        except aiohttp.ClientResponseError:
            logger.exception('Failed to retrieve pokemon.')
            return render(
                request=request,
                template_name='poke_api_error.html',
            )

        # If wrong offset number was provided and empty results were returned,
        # redirects to the last page
        if not pokemon_list['results']:
            base_url = reverse('pokedex')
            return redirect(f'{base_url}?page={last_page}')

        try:
            pokemon_info_list = await retrieve_multiple_pokemon(
                [pokemon['name'] for pokemon in pokemon_list['results']]
            )
        except (aiohttp.ClientResponseError, KeyError):
            logger.exception('Failed to retrieve pokemon.')
            return render(
                request=request,
                template_name='poke_api_error.html',
            )

        context = {
            'paginator': Paginator(pokemon_info_list, self.POKE_LIMIT),
            'page_number': page_number,
            'previous_page_number': page_number - 1,
            'next_page_number': page_number + 1 if pokemon_list['next'] else None,
            'last_page': last_page,
        }

        return render(
            request=request,
            template_name='pokedex.html',
            context=context,
        )


class PokemonView(View):
    """View class for displaying information about a specific Pokémon."""

    async def get(self, request: HttpRequest, pokemon_id: int, *args, **kwargs) -> HttpResponse:
        try:
            pokemon = await retrieve_pokemon(pokemon_id)
        except aiohttp.ContentTypeError:
            return HttpResponseNotFound()

        return render(
            request=request,
            template_name='pokemon.html',
            context={'pokemon': pokemon},
        )


class BerriesView(PokePaginationMixin, View):
    """View class for displaying the Berries."""

    async def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        page_number = self.get_page_number(request)

        try:
            berries = await retrieve_berries(
                limit=self.POKE_LIMIT,
                offset=self.POKE_OFFSET * (page_number - 1),
            )
            last_page = berries['count'] // self.POKE_OFFSET
        except (aiohttp.ClientResponseError, KeyError):
            logger.exception('Failed to retrieve berries.')
            return render(
                request=request,
                template_name='poke_api_error.html',
            )

        # If wrong offset number was provided and empty results were returned,
        # redirects to the last page
        if not berries['results']:
            base_url = reverse('berries')
            return redirect(f'{base_url}?page={last_page}')

        try:
            berry_items = await retrieve_berry_items(
                [berry['name'] for berry in berries['results']],
            )
        except aiohttp.ClientResponseError:
            logger.exception('Failed to retrieve berries.')
            return render(
                request=request,
                template_name='poke_api_error.html',
            )

        context = {
            'paginator': Paginator(berry_items, self.POKE_LIMIT),
            'page_number': page_number,
            'previous_page_number': page_number - 1,
            'next_page_number': page_number + 1 if berries['next'] else None,
            'last_page': last_page,
        }

        return render(
            request=request,
            template_name='berries.html',
            context=context,
        )


pokedex_view = PokedexView.as_view()
pokemon_view = PokemonView.as_view()
berries_view = BerriesView.as_view()
