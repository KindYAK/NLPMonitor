from django import template

register = template.Library()


@register.filter
def remove_http(url):
    if url.endswith("/"):
        url = url[:-1]
    return url.replace("https://", "").replace("http://", "").replace("www.", "")


@register.filter
def multiply_by_50(value):
    return int(value) * 40 + 80
