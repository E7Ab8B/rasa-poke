from django import template

register = template.Library()

MAX_BASE_STAT = 255


@register.filter
def stat_percentage(value: int) -> float:
    """Calculates the percentage of a given stat relative to the max stat."""
    if value is not None and value >= 0:
        percentage = (value / MAX_BASE_STAT) * 100
        return round(percentage, 2)
    return 0
