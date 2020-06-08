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
        "critetion_id+postfix": criterion_id + (("_" + postfix) if postfix else ""),
        "topic_modelling": topic_modelling,
        "ignore": ignore
    }
