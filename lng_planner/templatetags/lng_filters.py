# lng_planner/templatetags/lng_filters.py
from django import template

register = template.Library()

@register.filter
def get_key(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def abs_value(value):
    """Return absolute value of a number"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0