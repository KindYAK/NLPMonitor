import os
import sys
import glob

from contextlib import contextmanager
from tempfile import mkdtemp

from airflow.plugins_manager import AirflowPlugin
from airflow.operators.python_operator import PythonVirtualenvOperator


@contextmanager
def ReusableTemporaryDirectory(prefix):
    try:
        existing = glob.glob('/tmp/' + prefix + '*')
        if len(existing):
            name = existing[0]
        else:
            name = mkdtemp(prefix=prefix)
        yield name
    finally:
        # simply don't delete the tmp dir
        pass


class PythonVirtualenvCachedOperator(PythonVirtualenvOperator):
    def execute_callable(self, *args, **kwargs):
        with ReusableTemporaryDirectory(prefix='venv') as tmp_dir:
            if self.templates_dict:
                self.op_kwargs['templates_dict'] = self.templates_dict
            # generate filenames
            input_filename = os.path.join(tmp_dir, 'script.in')
            output_filename = os.path.join(tmp_dir, 'script.out')
            string_args_filename = os.path.join(tmp_dir, 'string_args.txt')
            script_filename = os.path.join(tmp_dir, 'script.py')

            # set up virtualenv
            self._execute_in_subprocess(self._generate_virtualenv_cmd(tmp_dir))
            cmd = self._generate_pip_install_cmd(tmp_dir)
            if cmd:
                self._execute_in_subprocess(cmd)

            self._write_args(input_filename)
            self._write_script(script_filename)
            self._write_string_args(string_args_filename)

            # execute command in virtualenv
            self._execute_in_subprocess(
                self._generate_python_cmd(tmp_dir,
                                          script_filename,
                                          input_filename,
                                          output_filename,
                                          string_args_filename))
            return self._read_result(output_filename)


class PythonVirtualenvCachedPlugin(AirflowPlugin):
    name = "python_virtualenv_cached"
    operators = [PythonVirtualenvCachedOperator]
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
