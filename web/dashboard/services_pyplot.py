from mainapp.templatetags.custom_stuff import remove_http


def bar_positive_negative_data_layout(context, criterion):
    if criterion.value_range_from >= 0:
        return None, None
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


def bar_source_data_layout(context, criterion):
    if criterion.value_range_from >= 0:
        data = [
            {
                'x': [remove_http(source['key']) for source in context['source_weight'][criterion.id]],
                'y': [round(source['value'], 2) for source in context['source_weight'][criterion.id]],
                'type': 'bar'
            }
        ]
    else:
        sources = context['source_weight'][criterion.id]
        for source in sources:
            total_source = source['negative'] + source['neutral'] + source['positive']
            source['negative_percent'] = round(source['negative'] / total_source * 100, 2)
            source['neutral_percent'] = round(source['neutral'] / total_source * 100, 2)
            source['positive_percent'] = round(source['positive'] / total_source * 100, 2)
        sources = sorted(sources, key=lambda x: x['negative_percent'], reverse=True)
        keys = []
        negatives_by_source_percents = []
        neutrals_by_source_percents = []
        positives_by_source_percents = []
        for source in sources:
            key = source['key'].replace("https://", "").replace("http://", "")
            if key.endswith("/"):
                key = key[:-1]
            keys.append(key)
            negatives_by_source_percents.append(source['negative_percent'])
            neutrals_by_source_percents.append(source['neutral_percent'])
            positives_by_source_percents.append(source['positive_percent'])
        data = [
            {
                'x': keys,
                'y': negatives_by_source_percents,
                'type': 'bar',
                'name': 'Негативные',
                'marker': {
                    'color': '#d3322b',
                },
            },
            {
                'x': keys,
                'y': neutrals_by_source_percents,
                'type': 'bar',
                'name': 'Нейтральные',
                'marker': {
                    'color': '#fee42c',
                },
            },
            {
                'x': keys,
                'y': positives_by_source_percents,
                'type': 'bar',
                'name': 'Позитивные',
                'marker': {
                    'color': '#23964f',
                }
            }
        ]
    layout = {
        'title': f'{criterion.name}',
        'showlegend': False,
        'bargap': 0.025,
    }
    if criterion.value_range_from < 0:
        layout['barmode'] = 'stack'
    return data, layout
