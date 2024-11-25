from django import template

register = template.Library()

@register.filter(is_safe=True)
def ms_to_minutes_and_seconds(value):
    return f'{round(value / (1000 * 60))}m {round(value / 1000) % 60}s'