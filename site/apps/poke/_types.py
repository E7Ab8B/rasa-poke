from __future__ import annotations

from typing import TypedDict

from django.http import HttpRequest

from django_htmx.middleware import HtmxDetails


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


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails
