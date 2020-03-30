from jinja2.loaders import FileSystemLoader
from latex import build_pdf
from latex.jinja2 import make_env

from nlpmonitor.settings import TEMPLATE_LATEX_DIR


def compile_jinja2_latex(template_name, context):
    env = make_env(loader=FileSystemLoader(TEMPLATE_LATEX_DIR))
    tpl = env.get_template(template_name)
    return tpl.render(**context)


def build_latex_pdf(template_name, context):
    latex_code = compile_jinja2_latex(template_name, context)
    pdf = build_pdf(latex_code)
    return pdf
