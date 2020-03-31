from jinja2 import environmentfilter

from mainapp.templatetags.custom_stuff import remove_http
from mainapp.templatetags.dictionary_getter import get_item


@environmentfilter
def get_item_env(env, dictionary, key):
    return get_item(dictionary, key)


@environmentfilter
def remove_http_env(env, s, _):
    return remove_http(s)


@environmentfilter
def substr_env(env, s, f, t):
    return s[f:t]
