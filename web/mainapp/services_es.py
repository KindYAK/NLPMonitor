from .constants import SEARCH_CUTOFF_CONFIG
from itertools import tee


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return list(zip(a, b))


def get_elscore_cutoff(scores_array, lvl):
    """Given a set of scores"""
    conf = SEARCH_CUTOFF_CONFIG[lvl]
    RC = conf["RIGID_CUTOFF"]
    IDC = conf["IMMEDIATE_DIFFERENTIAL_CUTOFF"]
    GDC = conf["GLOBAL_DIFFERENTIAL_CUTOFF"]
    AMRC = conf["ABS_MAX_RESULTS_CUTOFF"]
    RMRC = conf["REL_MAX_RESULTS_CUTOFF"]

    GLOBAL_DIFFERENTIAL_CUTOFF_ABS = -1
    if scores_array:
        GLOBAL_DIFFERENTIAL_CUTOFF_ABS = max(scores_array) / GDC

    MAX_RESULTS_CUTOFF = int(round(len(scores_array) * RMRC))
    scores_array = scores_array[:min(MAX_RESULTS_CUTOFF, AMRC)]
    len_res = 0
    for i, (_current, _next) in enumerate(pairwise(scores_array)):
        # 1. Cut over _scores
        if _current < RC:
            break
        # 2. Cut over difference between current and next
        if _current / _next > IDC:
            len_res += 1
            break
        # 3. First one would declare his core, and others would filtered
        # according to the score. [100, 70, 50, 49, 20] -> [100, 70, 50]
        if _current < GLOBAL_DIFFERENTIAL_CUTOFF_ABS:
            break
        len_res += 1
        if i == len(scores_array) - 2:  # check if we got all array
            len_res += 1
    return len_res
