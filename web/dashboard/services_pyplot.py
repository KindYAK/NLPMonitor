def bar_positive_negative_data_layout(context, criterion):
    data = [
        {
            'x': ["Негатив", "Нейтральные", "Позитив"],
            'y': [bucket.doc_count for bucket in context['posneg_distribution'][criterion.id]['buckets']],
            'marker': {
                'color': ['#d3322b', '#fee42c', '#23964f']
            },
            'type': 'bar'
        }
    ]
    layout = {
        'title': f'{criterion.name}',
        'showlegend': False,
        'bargap': 0.025,
    }
    return data, layout


def dynamics_data_layout(context, criterion):
    x = [tick.key_as_string for tick in context['absolute_value'][criterion.id]]
    y = [round(tick.dynamics_weight.value, 5) for tick in context['absolute_value'][criterion.id]]
    data = [
        {
            'mode': 'lines',
            'x': x,
            'y': y,
            'name': 'test',
        },
    ]
    layout = {
        'title': f'Динамика - {criterion.name}',
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
