from django import template

register = template.Library()


@register.filter
def remove_http(url):
    if url.endswith("/"):
        url = url[:-1]
    return url.replace("https://", "").replace("http://", "").replace("www.", "")
