from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
from latex import build_pdf
from latex.jinja2 import ENV_ARGS, LatexMarkup

from mainapp.templatetags.jinja2_styled import remove_http_env, get_item_env, substr_env
from nlpmonitor.settings import TEMPLATE_LATEX_DIR


def compile_jinja2_latex(template_name, context):
    ENV_ARGS['loader'] = FileSystemLoader(TEMPLATE_LATEX_DIR)
    env = Environment(**ENV_ARGS)
    env.filters['e'] = LatexMarkup.escape
    env.filters.update({
        'str': str,
        'get_item': get_item_env,
        'remove_http': remove_http_env,
        'substr': substr_env,
    })
    tpl = env.get_template(template_name)
    return tpl.render(**context)


def build_latex_pdf(template_name, context):
    latex_code = compile_jinja2_latex(template_name, context)
    pdf = build_pdf(latex_code, builder="pdflatex")
    return pdf
