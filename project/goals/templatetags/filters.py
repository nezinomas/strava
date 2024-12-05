from django import template

from ..lib import utils

register = template.Library()


@register.filter
def convert_seconds(seconds):
    hours, minutes, _ = utils.convert_seconds(seconds)

    hours = f"{hours}h" if hours else ""
    minutes = f"{minutes}m" if minutes else "0m"

    return f"{hours} {minutes}" if hours and minutes else minutes


@register.filter
def convert_meters(meters):
    tmp_placeholder = "#"
    return (
        f"{(meters / 1000):,.1f}km".replace(".", tmp_placeholder)
        .replace(",", ".")
        .replace(tmp_placeholder, ",")
    )


@register.filter
def cut_name(name: str):
    name, _ = name.rsplit(" ", 1)
    return f"{name} {_[:2]}."


@register.filter
def intcomma(number):
    return str(number).replace(",", ".")


# @register.simple_tag
@register.filter()
def get_object(arr, index):
    try:
        return arr[index]
    except IndexError:
        return ""
