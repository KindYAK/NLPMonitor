from dashboard.widgets import *

TYPES_META_DICT = {
    0: {
        "name": "Overall positive-negative",
        "callable": overall_positive_negative,
        "template_name": "dashboard/widgets/overall_positive_negative.html",
    },
    1: {
        "name": "Dynamic",
        "callable": lambda x, y: {"test": 2},
        "template_name": "dashboard/widgets/test2.html",
    },
    2: {
        "name": "Top news",
        "callable": lambda x, y: {"test": 3},
        "template_name": "dashboard/widgets/test1.html",
    },
    3: {
        "name": "Top topics",
        "callable": lambda x, y: {"test": 4},
        "template_name": "dashboard/widgets/test2.html",
    },
    4: {
        "name": "Source distribution",
        "callable": lambda x, y: {"test": 5},
        "template_name": "dashboard/widgets/test1.html",
    }
}
