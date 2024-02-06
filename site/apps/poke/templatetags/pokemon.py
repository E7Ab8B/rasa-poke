from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from apps.poke._types import Item, Pokemon

logger = logging.getLogger(__name__)
register = template.Library()

MAX_BASE_STAT = 255


@register.filter
def stat_percentage(value: int) -> float:
    """Calculates the percentage of a given stat relative to the max stat."""
    if value is not None and value >= 0:
        percentage = (value / MAX_BASE_STAT) * 100
        return round(percentage, 2)
    return 0


@register.filter
def pokemon_sprite(pokemon: Pokemon) -> str:
    """Get the URL for the sprite of a Pokemon from `pokemon`."""
    try:
        sprite = pokemon['sprites']['other']['official-artwork']['front_default']
        if not sprite:
            raise TypeError
    except (KeyError, TypeError):
        logger.exception('Missing keys for retrieving pokemon sprite. Pokemon ID: %s', pokemon['id'])
        return ''

    return sprite


@register.filter
def item_sprite(item: Item) -> str:
    """Get the URL for the sprite of an item from `item`."""
    try:
        sprite = item['sprites']['default']
        if not sprite:
            raise TypeError
    except (KeyError, TypeError):
        logger.exception('Missing keys for retrieving item sprite. Item ID: %s', item['id'])
        return ''

    return sprite
