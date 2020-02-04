from django import template

register = template.Library()

@register.filter
def remove_http(url):
    return url.replace("https://", "").replace("http://", "")
