from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dict(dictionary).get(key)
