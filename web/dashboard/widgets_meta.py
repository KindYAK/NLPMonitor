from dashboard.widgets import *

TYPES_META_DICT = {
    0: {
        "name": "Overall positive-negative",
        "callable": overall_positive_negative,
        "template_name": "dashboard/widgets/overall_positive_negative.html",
    },
    1: {
        "name": "Dynamic",
        "callable": dynamics,
        "template_name": "dashboard/widgets/dynamics.html",
    },
    2: {
        "name": "Top news",
        "callable": top_news,
        "template_name": "dashboard/widgets/top_news.html",
    },
    3: {
        "name": "Top topics",
        "callable": lambda x, y: {"test": 4},
        "template_name": "dashboard/widgets/test1.html",
    },
    4: {
        "name": "Source distribution",
        "callable": source_distribution,
        "template_name": "dashboard/widgets/source_distribution.html",
    }
}
