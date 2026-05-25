from django import template

from ..lib import utils

register = template.Library()


from django.utils.safestring import mark_safe

@register.filter
def convert_seconds(seconds):
    hours, minutes, _ = utils.convert_seconds(seconds)

    hours_str = f'<span class="time-hours">{hours}</span><span class="time-unit">h</span>' if hours else ""
    minutes_str = f'<span class="time-minutes">{minutes}</span><span class="time-unit">m</span>'

    if hours:
        return mark_safe(f"{hours_str} {minutes_str}")
    else:
        return mark_safe(minutes_str)


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
