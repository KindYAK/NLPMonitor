class CacheHit(Exception):
    pass


class EmptySearchException(Exception):
    pass


class Forbidden(Exception):
    pass


def get_topic_weight_threshold_options(is_superuser):
    if is_superuser:
        return [(i, str(i)) for i in
                [0.0001, 0.001] + [j / 100 for j in range(1, 10)] + [0.1, 0.125, 0.15, 0.175, 0.2, 0.25]]
    else:
        return [
            (0.01, "Очень мягкий (0.01)"),
            (0.05, "Мягкий (0.05)"),
            (0.1, "Средний (0.1)"),
            (0.15, "Жёсткий (0.15)"),
            (0.2, "Очень жёсткий (0.2)"),
        ]