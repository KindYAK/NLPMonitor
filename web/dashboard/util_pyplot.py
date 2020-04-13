def get_title_layout_update(title, font=30):
    return {
        'title': {
            'text': f'{title}',
            'font': {
                'size': font
            },
            'xanchor': 'center',
            'x': 0.5,
        }
    }


def get_axis_title_layout_update(xtitle=None, ytitle=None, font=24):
    res = {}
    if xtitle:
        res['xaxis'] = {
            'title': {
                'text': f'{xtitle}',
                'font': {
                    'size': font
                }
            }
        }
    if ytitle:
        res['yaxis'] = {
            'title': {
                'text': f'{ytitle}',
                'font': {
                    'size': font
                }
            }
        }
    return res
