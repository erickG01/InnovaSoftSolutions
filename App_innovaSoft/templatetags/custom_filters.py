# custom_filters.py
from django import template

register = template.Library()

@register.filter(name='absolute')
def absolute(value):
    return abs(value)  # Aquí usamos la función `abs` de Python sin conflicto

