from __future__ import annotations

from typing import TypedDict

from django.http import HttpRequest

from django_htmx.middleware import HtmxDetails


class PokemonBase(TypedDict):
    """Represents basic information about a Pokemon."""

    name: str
    url: str


class PokemonList(TypedDict):
    """List of basic Pokemon information."""

    count: int
    next: str
    previous: str
    results: list[PokemonBase]


class StatBase(TypedDict):
    """Represents the base information of a Pokemon's stat."""

    name: int
    url: int


class Stat(TypedDict):
    """Represents detailed information about a Pokemon's stat."""

    base_stat: int
    effort: int
    stat: StatBase


class TypeBase(TypedDict):
    """Represents the base information of a Pokemon's type."""

    name: str
    url: str


class Type(TypedDict):
    """Represents detailed information about a Pokemon's type."""

    slot: int
    type: TypeBase


class Pokemon(TypedDict):
    """Represents detailed information about a Pokemon."""

    id: int
    name: str
    order: int
    sprites: dict
    stats: list[Stat]
    types: list[Type]


class EffectEntry(TypedDict):
    """Represents an entry describing the effect of an item or ability."""

    effect: str
    short_effect: str


class Item(TypedDict):
    """Represents detailed information about an item."""

    id: int
    name: str
    url: str
    effect_entries: list[EffectEntry]
    sprites: dict[str, str]


class Berry(TypedDict):
    """Represents information about a berry."""

    id: int
    name: str
    item: TypeBase


class BerryItem(TypedDict):
    """Represents detailed information about a berry and its corresponding item."""

    berry: Berry
    item: Item


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails
