from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypedDict

import aiohttp

if TYPE_CHECKING:
    from collections.abc import Sequence

POKEMON_API = 'https://pokeapi.co/api/v2/'
POKEMON_ENDPOINT = f'{POKEMON_API}pokemon/'
ITEM_ENDPOINT = f'{POKEMON_API}item/'
BERRY_ENDPOINT = f'{POKEMON_API}berry/'


class Pokemon(TypedDict):
    """Basic Pokemon information that exists in the Pokemon list endpoint."""

    name: str
    url: str


class PokemonList(TypedDict):
    """List of basic Pokemon information."""

    count: int
    next: str
    previous: str
    results: list[Pokemon]


class Stat(TypedDict):
    """Stat information of a Pokemon."""

    name: int
    url: int


class StatInfo(TypedDict):
    """Detailed information about a Pokemon's stat."""

    base_stat: int
    effort: int
    stat: Stat


class Type(TypedDict):
    """Type information of a Pokemon."""

    name: str
    url: str


class TypeInfo(TypedDict):
    """Detailed information about a Pokemon's type."""

    slot: int
    type: Type


class PokemonInfo(TypedDict):
    """Detailed Pokemon information which is returned on a detail endpoint."""

    id: int
    name: str
    order: int
    sprites: dict
    stats: list[StatInfo]
    types: list[TypeInfo]


class EffectEntry(TypedDict):
    """Entry describing the effect of an item or ability."""

    effect: str
    short_effect: str


class Item(TypedDict):
    """Item information."""

    name: str
    url: str


class ItemInfo(TypedDict):
    """Detailed information about an item."""

    id: int
    name: str
    url: str
    effect_entries: list[EffectEntry]
    sprites: dict[str, str]


class BerryInfo(TypedDict):
    """Information about a berry."""

    id: int
    name: str
    item: Type


class BerryItemInfo(TypedDict):
    """Detailed information about a berry."""

    berry: BerryInfo
    item: ItemInfo


async def retrieve_pokemon_list(limit: int = 20, offset: int = 0) -> PokemonList:
    """Retrieves a list of Pokemon from the Poke API."""
    params = {'limit': limit, 'offset': offset}

    async with aiohttp.ClientSession() as session:
        async with session.get(POKEMON_ENDPOINT, params=params) as resp:
            return await resp.json()


async def retrieve_berries(limit: int = 20, offset: int = 0) -> PokemonList:
    """Retrieves a list of berries from the Poke API."""
    params = {'limit': limit, 'offset': offset}

    async with aiohttp.ClientSession() as session:
        async with session.get(BERRY_ENDPOINT, params=params) as resp:
            return await resp.json()


async def retrieve_pokemon(pokemon: str | int) -> PokemonInfo:
    """Retrieves information about a specific Pokemon from the Poke API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{POKEMON_ENDPOINT}{pokemon}') as resp:
            return await resp.json()


async def _retrieve_pokemon(session: aiohttp.ClientSession, pokemon: str | int) -> PokemonInfo:
    """Retrieves Pokemon information from the Poke API.

    Used for fetching multiple Pokemon concurrently. The session must be provided.
    """
    async with session.get(f'{POKEMON_ENDPOINT}{pokemon}') as resp:
        return await resp.json()


async def _retrieve_berry(session: aiohttp.ClientSession, berry: str | int) -> BerryInfo:
    """Retrieves berry information from the Poke API.

    Used for fetching multiple berries concurrently. The session must be provided.
    """
    async with session.get(f'{BERRY_ENDPOINT}{berry}') as resp:
        return await resp.json()


async def _retrieve_item(session: aiohttp.ClientSession, item: str | int) -> ItemInfo:
    """Retrieves item information from the Poke API.

    Used for fetching multiple items concurrently. The session must be provided.
    """
    async with session.get(f'{ITEM_ENDPOINT}{item}') as resp:
        return await resp.json()


async def _retrieve_berry_item(session: aiohttp.ClientSession, berry: str | int) -> BerryItemInfo:
    """Retrieves detailed berry and associated item info from the Poke API.

    Used for fetching multiple berries concurrently. Session must be provided.
    """
    berry_data = await _retrieve_berry(session=session, berry=berry)
    item_data = await _retrieve_item(session=session, item=berry_data['item']['name'])

    return {
        'berry': berry_data,
        'item': item_data,
    }


async def retrieve_multiple_pokemon(pokemon: Sequence[str | int]) -> list[PokemonInfo]:
    """Retrieves detailed information about multiple Pokemon from the Poke API."""
    assert pokemon, 'The Pokemon list must not empty.'

    async with aiohttp.ClientSession() as session:
        coroutines = [_retrieve_pokemon(session, p) for p in pokemon]
        return await asyncio.gather(*coroutines)


async def retrieve_berry_items(berries: Sequence[str | int]) -> list[BerryItemInfo]:
    """Retrieves detailed info of multiple berries and associated items from the Poke API."""
    assert berries, 'The berries list must not empty.'

    async with aiohttp.ClientSession() as session:
        coroutines = [_retrieve_berry_item(session, p) for p in berries]
        return await asyncio.gather(*coroutines)
