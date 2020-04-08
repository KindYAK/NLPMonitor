def dynamics_data_layout(x, y):
    data = [
        {
            'mode': 'lines',
            'x': x,
            'y': y,
            'name': 'test',
        },
    ]
    layout = {
        'title': 'Динамика',
        'xaxis': {
            'fixedrange': True
        },
        'yaxis': {
            'fixedrange': True,
        },
        'height': 350,
        'margin': {
            'l': 45,
            'r': 15,
            'b': 35,
            't': 45,
            'pad': 5
        }
    }
    return data, layout
