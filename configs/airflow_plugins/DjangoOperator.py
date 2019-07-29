import os
import sys

from airflow.plugins_manager import AirflowPlugin
from airflow.operators.python_operator import PythonOperator


def setup_django_for_airflow():
    sys.path.append('/django/')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nlpmonitor.settings")

    import django
    django.setup()


class DjangoOperator(PythonOperator):
    def pre_execute(self, *args, **kwargs):
        setup_django_for_airflow()


class AirflowTestPlugin(AirflowPlugin):
    name = "django"
    operators = [DjangoOperator]
    # A list of class(es) derived from BaseHook
    hooks = []
    # A list of class(es) derived from BaseExecutor
    executors = []
    # A list of references to inject into the macros namespace
    macros = []
    # A list of objects created from a class derived
    # from flask_admin.BaseView
    admin_views = []
    # A list of Blueprint object created from flask.Blueprint
    flask_blueprints = []
    # A list of menu links (flask_admin.base.MenuLink)
    menu_links = []
