from jinja2 import environmentfilter
from latex import escape
from markupsafe import Markup

from mainapp.templatetags.custom_stuff import remove_http
from mainapp.templatetags.dictionary_getter import get_item


class LatexMarkup(Markup):
    def unescape(self):
        raise NotImplementedError

    def stripstags(self):
        raise NotImplementedError

    @classmethod
    def escape(cls, s):
        if hasattr(s, '__html__'):
            return s.__html__()

        rv = escape(s).strip()
        if rv.__class__ is not cls:
            return cls(rv)
        return rv


@environmentfilter
def get_item_env(env, dictionary, key):
    return get_item(dictionary, key)


@environmentfilter
def remove_http_env(env, s, _):
    return remove_http(s)


@environmentfilter
def substr_env(env, s, f, t):
    return s[f:t]
