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
            'name': f'{criterion.name}',
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


def dynamics_posneg_data_layout(context, criterion):
    if criterion.value_range_from >= 0:
        return None, None
    x_pos = [tick.key_as_string for tick in context['positive'][criterion.id]]
    y_pos = [round(tick.doc_count, 0) for tick in context['positive'][criterion.id]]
    x_neg = [tick.key_as_string for tick in context['negative'][criterion.id]]
    y_neg = [round(tick.doc_count, 0) for tick in context['negative'][criterion.id]]
    data = [
        {
            'mode': 'lines',
            'x': x_pos,
            'y': y_pos,
            'name': f'{criterion.name} - позитив',
            'line': {
                'color': '#23964f',
            }
        },
        {
            'mode': 'lines',
            'x': x_neg,
            'y': y_neg,
            'name': f'{criterion.name} - негатив',
            'line': {
                'color': '#d3322b',
            }
        },
    ]
    layout = {
        'title': f'Динамика - {criterion.name}',
        'legend': {'orientation': 'h'},
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
