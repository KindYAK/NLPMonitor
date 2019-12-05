from django.core.serializers import serialize
from django.template import Library

register = Library()


@register.filter
def json(queryset):
    return serialize('json', queryset)


@register.filter
def round_fl(val, points):
    return round(float(val), points)
