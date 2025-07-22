# templatetags/dashboard_extras.py
from django import template
register = template.Library()

@register.filter
def pluck(data, key):
    try:
        return [item.get(key) for item in data]
    except Exception:
        return []
