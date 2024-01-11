from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import aiohttp
from asgiref.sync import async_to_sync

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic import ListView, TemplateView

from apps.poke.cache import cache_page_without_q_param
from apps.poke.utils.requests import (
    retrieve_berries,
    retrieve_berry_items,
    retrieve_multiple_pokemon,
    retrieve_pokemon,
    retrieve_pokemon_list,
)

if TYPE_CHECKING:
    from apps.poke._types import BerryItem, HtmxHttpRequest, Pokemon

logger = logging.getLogger(__name__)


@method_decorator(cache_page_without_q_param(60 * 5), name='dispatch')
@method_decorator(vary_on_headers('HX-Request'), name='dispatch')
class PokedexView(ListView):
    """View class for displaying the Pokédex.

    This view class utilizes HTMX for paginating(infinite-scroll) and caching
    for improved performance.
    """

    paginate_by = 40
    context_object_name = 'pokemon_list'
    request: HtmxHttpRequest  # pyright: ignore[reportIncompatibleVariableOverride]

    def get_template_names(self) -> list[str]:
        """Returns the appropriate template name based on the request.

        If the request is an HTMX request, returns the partial template for
        paginating(infinite-scroll).  Otherwise, returns the full template for
        regular requests.
        """
        if self.request.htmx:
            return ['pokedex.html#pokemon-list']
        return ['pokedex.html']

    def get_queryset(self) -> list[Pokemon]:
        """Returns list of Pokémon for displaying the Pokémon.

        If the list is not present in the cache, retrieves it and caches the
        result.
        """
        pokemon_info_list = cache.get('pokemon_info_list')

        if pokemon_info_list is None:
            pokemon_info_list = async_to_sync(self.retrieve_pokemon_info_list)()
            cache.set('pokemon_info_list', pokemon_info_list, timeout=60 * 60)

        query = self.request.GET.get("q")
        if query:
            pokemon_info_list = self.filter_pokemon_by_name(pokemon_info_list, query)

        return pokemon_info_list

    def filter_pokemon_by_name(self, pokemon_info_list: list[Pokemon], query: str) -> list[Pokemon]:
        query = query.lower()
        return [pokemon_info for pokemon_info in pokemon_info_list if query in pokemon_info['name'].lower()]

    async def retrieve_pokemon_info_list(self) -> list[Pokemon]:
        """Asynchronously retrieves the list of Pokémon information.

        Uses the :func:`retrieve_pokemon_list` function to get the list of
        Pokémon names, then fetches details for multiple Pokémon concurrently.
        """
        pokemon_list = await retrieve_pokemon_list()
        return await retrieve_multiple_pokemon([pokemon['name'] for pokemon in pokemon_list['results']])


class PokemonView(TemplateView):
    """View class for displaying information about a specific Pokémon.

    Note:
        Caching individual Pokémon views may not be worthwhile due to the
        likelihood of frequent updates. Pokémon information is subject to
        change more frequently, and these views typically contain less data,
        making it faster to generate response.

        It is more suitable to manage caching strategies at the list level,
        especially when dealing with more extensive datasets like a Pokédex.
    """

    template_name = 'pokemon.html'
    request: HtmxHttpRequest  # pyright: ignore[reportIncompatibleVariableOverride]

    # The warnings are intentionally ignored for compatibility with Django >= 4.2 (async) and to handle URL parameters
    async def get(  # pyright: ignore pylint: disable=arguments-differ,invalid-overridden-method
        self,
        request: HtmxHttpRequest,
        pokemon_id: int,
        *args,
        **kwargs,
    ) -> HttpResponse:
        context = self.get_context_data(**kwargs)

        try:
            context['pokemon'] = await retrieve_pokemon(pokemon_id)
        except aiohttp.ContentTypeError:
            return HttpResponseNotFound()

        return self.render_to_response(context)


@method_decorator(cache_page(60 * 5), name='dispatch')
class BerriesView(TemplateView):
    """View class for displaying Berries.

    Note:
        Pagination is unnecessary as the list of berries is short.
    """

    template_name = 'berries.html'
    request: HtmxHttpRequest  # pyright: ignore[reportIncompatibleVariableOverride]

    def get(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        request: HtmxHttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        context = self.get_context_data(**kwargs)

        berry_items_info: list[BerryItem] | None = cache.get('berry_items_info')

        if berry_items_info is None:
            berry_items_info = async_to_sync(self.retrieve_berry_items_info)()
            cache.set('berry_items_info', berry_items_info, timeout=60 * 60)

        context['berry_items_info'] = berry_items_info

        return self.render_to_response(context)

    async def retrieve_berry_items_info(self) -> list[BerryItem]:
        """Asynchronously retrieves the list of Berries information.

        Uses the :func:`retrieve_berries` function to get the list of
        Berry names, then fetches details for multiple Berries concurrently.
        """
        berries = await retrieve_berries()
        return await retrieve_berry_items([berry['name'] for berry in berries['results']])


pokedex_view = PokedexView.as_view()
pokemon_view = PokemonView.as_view()
berries_view = BerriesView.as_view()
