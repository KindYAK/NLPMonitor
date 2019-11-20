from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    if not dictionary or key not in dictionary:
        return ""
    return dictionary[key]


@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name)
