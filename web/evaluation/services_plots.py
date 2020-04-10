import datetime
import os
import plotly

from plotly import graph_objects as go

from dashboard.services_pyplot import *
from nlpmonitor.settings import REPORT_IMAGE_DIR


def get_filename(prefix, user_id):
    return f"{prefix}{user_id}{str(datetime.datetime.now()).replace(' ', '').replace(':', '').replace('-', '').replace('.', '')}.jpg"


def save_plot(filename, data, layout):
    plotly.io.orca.config.server_url = "http://orca:9091"
    plotly.io.orca.config.save()
    fig = go.Figure(data=data, layout=layout)
    if not os.path.exists(os.path.join("/", REPORT_IMAGE_DIR)):
        os.mkdir(os.path.join("/", REPORT_IMAGE_DIR))
    fig.write_image(os.path.join("/", REPORT_IMAGE_DIR, filename), scale=2)
    return os.path.join("/", REPORT_IMAGE_DIR, filename)


def handle_plotting(f_data_layout, context, user_id):
    data, layout = f_data_layout(
        context=context,
        criterion=context['criterion'],
    )
    if not data:
        return None
    filename = get_filename(f_data_layout.__name__, user_id)
    return save_plot(filename, data, layout)


def bar_positive_negative_plot(context, user_id):
    return handle_plotting(
        f_data_layout=bar_positive_negative_data_layout,
        context=context,
        user_id=user_id
    )


def dynamics_plot(context, user_id):
    return {
        "dynamics": handle_plotting(
            f_data_layout=dynamics_data_layout,
            context=context,
            user_id=user_id
        ),
        "dynamics_posneg": handle_plotting(
            f_data_layout=dynamics_posneg_data_layout,
            context=context,
            user_id=user_id
        ),
    }


def bar_source_plot(context, user_id):
    return handle_plotting(
            f_data_layout=bar_source_data_layout,
            context=context,
            user_id=user_id
        )