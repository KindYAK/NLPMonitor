import datetime
import os

from plotly import graph_objects as go

from dashboard.services_pyplot import *
from nlpmonitor.settings import REPORT_IMAGE_DIR, DEBUG


def get_filename(prefix, user_id):
    return f"{prefix}{user_id}{str(datetime.datetime.now()).replace(' ', '').replace(':', '').replace('-', '').replace('.', '')}.jpg"


def save_plot(filename, data, layout):
    fig = go.Figure(data=data, layout=layout)
    if not os.path.exists(os.path.join("/", REPORT_IMAGE_DIR)):
        os.mkdir(os.path.join("/", REPORT_IMAGE_DIR))
    if DEBUG:
        print("! start", datetime.datetime.now())
    fig.write_image(os.path.join("/", REPORT_IMAGE_DIR, filename), scale=2)
    if DEBUG:
        print("! end", datetime.datetime.now())


def handle_plotting(f_data_layout, context, user_id):
    data, layout = f_data_layout(
        context=context,
        criterion=context['criterion'],
    )
    if not data:
        return None
    if DEBUG:
        print("!!!", f_data_layout.__name__)
    filename = get_filename(f_data_layout.__name__, user_id)
    save_plot(filename, data, layout)
    return os.path.join(REPORT_IMAGE_DIR, filename)


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
