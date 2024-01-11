from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    from collections.abc import Sequence

    from apps.poke._types import Berry, BerryItem, Item, Pokemon, PokemonList

POKEMON_API = 'https://pokeapi.co/api/v2/'
POKEMON_ENDPOINT = f'{POKEMON_API}pokemon/'
ITEM_ENDPOINT = f'{POKEMON_API}item/'
BERRY_ENDPOINT = f'{POKEMON_API}berry/'


async def retrieve_pokemon_list(*, limit: int = -1, offset: int = 0) -> PokemonList:
    """Retrieves a list of Pokemon from the Poke API.

    Args:
        limit: The maximum number of results to retrieve.  Use ``-1`` to
            retrieve all results.
        offset: The offset for paginated results.
    """
    params = {'limit': limit, 'offset': offset}

    async with aiohttp.ClientSession() as session:
        async with session.get(POKEMON_ENDPOINT, params=params) as resp:
            return await resp.json()


async def retrieve_berries(*, limit: int = -1, offset: int = 0) -> PokemonList:
    """Retrieves a list of berries from the Poke API.

    Args:
        limit: The maximum number of results to retrieve.  Use ``-1`` to
            retrieve all results.
        offset: The offset for paginated results.
    """
    params = {'limit': limit, 'offset': offset}

    async with aiohttp.ClientSession() as session:
        async with session.get(BERRY_ENDPOINT, params=params) as resp:
            return await resp.json()


async def retrieve_pokemon(pokemon: str | int) -> Pokemon:
    """Retrieves information about a specific Pokemon from the Poke API."""
    async with aiohttp.ClientSession() as session:
        return await _retrieve_pokemon(session, pokemon)


async def _retrieve_pokemon(session: aiohttp.ClientSession, pokemon: str | int) -> Pokemon:
    """Retrieves Pokemon information from the Poke API.

    Used for fetching multiple Pokemon concurrently.
    """
    async with session.get(f'{POKEMON_ENDPOINT}{pokemon}') as resp:
        return await resp.json()


async def _retrieve_berry(session: aiohttp.ClientSession, berry: str | int) -> Berry:
    """Retrieves berry information from the Poke API.

    Used for fetching multiple berries concurrently.
    """
    async with session.get(f'{BERRY_ENDPOINT}{berry}') as resp:
        return await resp.json()


async def _retrieve_item(session: aiohttp.ClientSession, item: str | int) -> Item:
    """Retrieves item information from the Poke API.

    Used for fetching multiple items concurrently.
    """
    async with session.get(f'{ITEM_ENDPOINT}{item}') as resp:
        return await resp.json()


async def _retrieve_berry_item(session: aiohttp.ClientSession, berry: str | int) -> BerryItem:
    """Retrieves detailed berry and associated item info from the Poke API.

    Used for fetching multiple berries concurrently. Session must be provided.
    """
    berry_data = await _retrieve_berry(session=session, berry=berry)
    item_data = await _retrieve_item(session=session, item=berry_data['item']['name'])

    return {
        'berry': berry_data,
        'item': item_data,
    }


async def retrieve_multiple_pokemon(pokemon: Sequence[str | int]) -> list[Pokemon]:
    """Retrieves detailed information about multiple Pokemon from the Poke API."""
    assert pokemon, 'The Pokemon list must not empty.'

    async with aiohttp.ClientSession() as session:
        coroutines = [_retrieve_pokemon(session, p) for p in pokemon]
        return await asyncio.gather(*coroutines)


async def retrieve_berry_items(berries: Sequence[str | int]) -> list[BerryItem]:
    """Retrieves detailed info of multiple berries and associated items from the Poke API."""
    assert berries, 'The berries list must not empty.'

    async with aiohttp.ClientSession() as session:
        coroutines = [_retrieve_berry_item(session, p) for p in berries]
        return await asyncio.gather(*coroutines)
