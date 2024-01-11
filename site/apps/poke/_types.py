from __future__ import annotations

from typing import TypedDict

from django.http import HttpRequest

from django_htmx.middleware import HtmxDetails


class Pokemon(TypedDict):
    """Represents basic information about a Pokemon."""

    name: str
    url: str


class PokemonList(TypedDict):
    """List of basic Pokemon information."""

    count: int
    next: str
    previous: str
    results: list[Pokemon]


class Stat(TypedDict):
    """Represents the base information of a Pokemon's stat."""

    name: int
    url: int


class StatInfo(TypedDict):
    """Represents detailed information about a Pokemon's stat."""

    base_stat: int
    effort: int
    stat: Stat


class Type(TypedDict):
    """Represents the base information of a Pokemon's type."""

    name: str
    url: str


class TypeInfo(TypedDict):
    """Represents detailed information about a Pokemon's type."""

    slot: int
    type: Type


class PokemonInfo(TypedDict):
    """Represents detailed information about a Pokemon."""

    id: int
    name: str
    order: int
    sprites: dict
    stats: list[StatInfo]
    types: list[TypeInfo]


class EffectEntry(TypedDict):
    """Represents an entry describing the effect of an item or ability."""

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
    """Represents information about a berry."""

    id: int
    name: str
    item: Type


class BerryItemInfo(TypedDict):
    """Represents detailed information about a berry and its corresponding item."""

    berry: BerryInfo
    item: ItemInfo


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails
