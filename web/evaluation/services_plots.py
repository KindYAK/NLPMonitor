import datetime
import os

from plotly import graph_objects as go

from dashboard.services_pyplot import *
from nlpmonitor.settings import REPORT_IMAGE_DIR


def get_filename(prefix, user_id):
    return f"{prefix}{user_id}{str(datetime.datetime.now()).replace(' ', '').replace(':', '').replace('-', '').replace('.', '')}.jpg"


def save_plot(filename, data, layout):
    fig = go.Figure(data=data, layout=layout)
    if not os.path.exists(os.path.join("/", REPORT_IMAGE_DIR)):
        os.mkdir(os.path.join("/", REPORT_IMAGE_DIR))
    print("! start", datetime.datetime.now())
    fig.write_image(os.path.join("/", REPORT_IMAGE_DIR, filename))
    print("! end", datetime.datetime.now())


def bar_positive_negative_plot(context, user_id):
    data, layout = bar_positive_negative_data_layout(
        context=context,
        criterion=context['criterion'],
    )
    filename = get_filename("baroverall", user_id)
    save_plot(filename, data, layout)
    return os.path.join(REPORT_IMAGE_DIR, filename)


def dynamics_plot(context, user_id):
    data, layout = dynamics_data_layout(
        context=context,
        criterion=context['criterion'],
    )
    filename = get_filename("dynamics", user_id)
    save_plot(filename, data, layout)
    return os.path.join(REPORT_IMAGE_DIR, filename)
