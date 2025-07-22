from django import template

register = template.Library()

@register.filter
def pluck(values, key):
    return [v.get(key) for v in values]
