TYPES_META_DICT = {
    0: {
        "name": "Overall positive-negative",
        "callable": lambda x: {"test": 1},
        "template_name": "dashboard/widgets/test1.html",
    },
    1: {
        "name": "Dynamic",
        "callable": lambda x: {"test": 2},
        "template_name": "dashboard/widgets/test2.html",
    },
    2: {
        "name": "Top news",
        "callable": lambda x: {"test": 3},
        "template_name": "dashboard/widgets/test1.html",
    },
    3: {
        "name": "Top topics",
        "callable": lambda x: {"test": 4},
        "template_name": "dashboard/widgets/test2.html",
    },
    4: {
        "name": "Source distribution",
        "callable": lambda x: {"test": 5},
        "template_name": "dashboard/widgets/test1.html",
    }
}
