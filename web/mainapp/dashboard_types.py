DASHBOARD_TYPE_NUM_PUBLICATIONS_BY_TAG = "NUM_PUBLICATIONS_BY_TAG"
DASHBOARD_TYPE_NUM_PUBLICATIONS_OVERALL = "NUM_PUBLICATIONS_OVERALL"
DASHBOARD_TYPE_NUM_VIEWS_BY_TAG = "NUM_VIEWS_BY_TAG"
DASHBOARD_TYPE_NUM_VIEWS_OVERALL = "NUM_VIEWS_OVERALL"

VALUE_TYPE_COUNT = "VALUE_TYPE_COUNT"
VALUE_TYPE_SUM = "VALUE_TYPE_SUM"

FILTERING_TYPE_BY_TAG = "FILTERING_TYPE_BY_TAG"
FILTERING_TYPE_OVERALL = "FILTERING_TYPE_OVERALL"

DASHBOARD_TYPES = [
    {
        "type": DASHBOARD_TYPE_NUM_PUBLICATIONS_BY_TAG,
        "filtering": FILTERING_TYPE_BY_TAG,
        "value": VALUE_TYPE_COUNT,
        "name": "Количество публикаций по тегам",
    },
    {
        "type": DASHBOARD_TYPE_NUM_VIEWS_BY_TAG,
        "filtering": FILTERING_TYPE_BY_TAG,
        "value": VALUE_TYPE_SUM,
        "field": "num_views",
        "name": "Количество публикаций",
    },
    {
        "type": DASHBOARD_TYPE_NUM_PUBLICATIONS_OVERALL,
        "filtering": FILTERING_TYPE_OVERALL,
        "value": VALUE_TYPE_COUNT,
        "name": "Количество просмотров по тегам",
    },
    {
        "type": DASHBOARD_TYPE_NUM_VIEWS_OVERALL,
        "filtering": FILTERING_TYPE_OVERALL,
        "value": VALUE_TYPE_SUM,
        "field": "num_views",
        "name": "Количество просмотров",
    },
]
