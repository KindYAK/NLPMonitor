from copy import deepcopy

from nlpmonitor.settings import ES_INDEX_DOCUMENT_EVAL

POSTFIXES_TO_IGNORE = ["neg", ]
POSTFIXES_ALLOWED = ["m4a", "m4a_class", ] # Order matters - if one postfixes is a part of another, the bigger one should be on the right


def parse_eval_index_name(index_name):
    postfix = ""
    ignore = False
    for p in POSTFIXES_TO_IGNORE:
        if index_name.endswith(p):
            index_name = index_name.replace("_" + p, "")
            postfix = ""
            ignore = True
            break
    for p in POSTFIXES_ALLOWED:
        if index_name.endswith(p):
            index_name = index_name.replace("_" + p, "")
            postfix = p
            break
    criterion_id = index_name.split("_")[-1]
    topic_modelling = index_name.replace(ES_INDEX_DOCUMENT_EVAL + "_", "").replace("_" + criterion_id, "")
    return {
        "criterion_id": int(criterion_id),
        "postfix": postfix,
        "criterion.id_postfix": criterion_id + (("_" + postfix) if postfix else ""),
        "topic_modelling": topic_modelling,
        "ignore": ignore
    }


def add_id_postfix_to_dicts(criterions, eval_indices):
    criterions_dict = dict(
        (c['id'], c) for c in criterions
    )
    criterions_result = []
    for index in eval_indices:
        index = parse_eval_index_name(index)
        if index['ignore']:
            continue
        criterion = deepcopy(criterions_dict[index['criterion_id']])
        criterion['id'] = index['criterion.id_postfix']
        criterion['id_postfix'] = index['criterion.id_postfix']
        if index['postfix']:
            criterion['name'] = criterion['name'] + ("_" + index['postfix'] if index['postfix'] else "")
        criterions_result.append(criterion)
    return criterions_result


def add_id_postfix_to_qs(criterions, eval_indices):
    criterions_dict = dict(
        (c.id, c) for c in criterions
    )
    criterions_result = []
    for index in eval_indices:
        index = parse_eval_index_name(index)
        if index['ignore']:
            continue
        criterion = deepcopy(criterions_dict[index['criterion_id']])
        criterion.id_postfix = index['criterion.id_postfix']
        if index['postfix']:
            criterion.name = criterion.name + ("_" + index['postfix'] if index['postfix'] else "")
        criterions_result.append(criterion)
    return criterions_result
