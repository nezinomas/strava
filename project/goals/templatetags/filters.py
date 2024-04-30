from django import template

register = template.Library()


@register.filter
def convert_seconds(seconds):
    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60

    hours = f"{hours}h" if hours else ""
    minutes = f"{minutes}m" if minutes else "0m"

    return f"{hours} {minutes}" if hours and minutes else minutes


@register.filter
def convert_meters(meters):
    return f"{(meters / 1000):,.1f}km".replace(".", ",")