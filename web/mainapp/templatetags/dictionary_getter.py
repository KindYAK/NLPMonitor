from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    if not type(dictionary) == list:
        if not dictionary or key not in dictionary:
            return ""
    else:
        if not (key >= 0 and key < len(dictionary)):
            return ""
    return dictionary[key]


@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name)


@register.simple_tag(takes_context=True)
def get_by_name(context, name):
    return context[name]
