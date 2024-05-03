from django import template
from ..lib import utils
register = template.Library()


@register.filter
def convert_seconds(seconds):
    hours, minutes = utils.convert_seconds_to_hours_and_minutes(seconds)

    hours = f"{hours}h" if hours else ""
    minutes = f"{minutes}m" if minutes else "0m"

    return f"{hours} {minutes}" if hours and minutes else minutes


@register.filter
def convert_meters(meters):
    return f"{(meters / 1000):,.1f}km".replace(".", ",")