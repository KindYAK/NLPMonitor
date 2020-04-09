import datetime
import os

from plotly import graph_objects as go

from dashboard.services_pyplot import dynamics_data_layout
from nlpmonitor.settings import REPORT_IMAGE_DIR


def get_filename(prefix, user_id):
    return f"{prefix}{user_id}{str(datetime.datetime.now()).replace(' ', '').replace(':', '').replace('-', '').replace('.', '')}.jpg"


def save_plot(filename, data, layout):
    fig = go.Figure(data=data, layout=layout)
    if not os.path.exists(os.path.join("/", REPORT_IMAGE_DIR)):
        os.mkdir(os.path.join("/", REPORT_IMAGE_DIR))
    fig.write_image(os.path.join("/", REPORT_IMAGE_DIR, filename))


def dynamics_plot(context, user_id):
    data, layout = dynamics_data_layout(
        x=[tick.key_as_string for tick in context['absolute_value'][context['criterions'][0].id]],
        y=[round(tick.dynamics_weight.value, 5) for tick in context['absolute_value'][context['criterions'][0].id]]
    )
    filename = get_filename("dynamics", user_id)
    save_plot(filename, data, layout)
    return os.path.join(REPORT_IMAGE_DIR, filename)
