from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import aiohttp
from asgiref.sync import async_to_sync

from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic import ListView, TemplateView

from apps.poke.utils.requests import (
    retrieve_berries,
    retrieve_berry_items,
    retrieve_multiple_pokemon,
    retrieve_pokemon,
    retrieve_pokemon_list,
)

if TYPE_CHECKING:
    from apps.poke._types import HtmxHttpRequest, PokemonInfo

logger = logging.getLogger(__name__)


class PokePaginationMixin:
    """Mixin class for handling pagination in the Pokédex and Berries views."""

    POKE_OFFSET = 20
    POKE_LIMIT = 20

    def get_page_number(self, request: HtmxHttpRequest) -> int:
        """Returns expected page number, which should be passed as `page` param."""
        try:
            page_number = int(request.GET['page'])  # pyright: ignore[reportGeneralTypeIssues]
        except (ValueError, KeyError):
            return 1

        return max(page_number, 1)


@method_decorator(cache_page(60 * 5), name='dispatch')
@method_decorator(vary_on_headers('HX-Request'), name='dispatch')
class PokedexView(ListView):
    """View class for displaying the Pokédex.

    This view class utilizes HTMX for paginating(infinite-scroll) and caching
    for improved performance.
    """

    paginate_by = 40
    context_object_name = 'pokemon_list'
    request: HtmxHttpRequest  # type: ignore[reportGeneralTypeIssues]

    def get_template_names(self) -> list[str]:
        """Returns the appropriate template name based on the request.

        If the request is an HTMX request, returns the partial template for
        paginating(infinite-scroll).  Otherwise, returns the full template for
        regular requests.
        """
        if self.request.htmx:
            return ['pokedex.html#partial-pokemon']
        return ['pokedex.html']

    def get_queryset(self) -> list[PokemonInfo]:
        """Returns list of Pokémon for displaying the Pokémon list.

        If the list is not present in the cache, retrieves it and caches the
        result.
        """
        pokemon_info_list = cache.get('pokemon_info_list')

        if pokemon_info_list is None:
            pokemon_info_list = async_to_sync(self.retrieve_pokemon_info_list)()
            cache.set('pokemon_info_list', pokemon_info_list, timeout=60 * 60)

        return pokemon_info_list

    async def retrieve_pokemon_info_list(self) -> list[PokemonInfo]:
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

    request: HtmxHttpRequest  # type: ignore[reportGeneralTypeIssues]

    def get_template_names(self) -> list[str]:
        """Returns the appropriate template name based on the request.

        If the request is an HTMX request, returns the partial template.
        Otherwise, returns the full template for regular requests.
        """
        if self.request.htmx:
            return ['pokemon.html#pokemon-info']
        return ['pokemon.html']

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

        response = self.render_to_response(context)
        if self.request.htmx:
            response['HX-Push-Url'] = reverse('pokemon', kwargs={'pokemon_id': pokemon_id})

        return response


class BerriesView(PokePaginationMixin, View):
    """View class for displaying the Berries."""

    async def get(self, request: HtmxHttpRequest, *args, **kwargs) -> HttpResponse:
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
