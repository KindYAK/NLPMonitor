SETTINGS_BODY = {
    "settings": {
        "number_of_shards": None,
        "number_of_replicas": 1,
        "max_result_window": 5000000
    },
    "mappings": None
}


def shards_mapping(doc_count: int) -> int:
    if isinstance(doc_count, str):
        doc_count = int(doc_count)

    if doc_count > 10_000_000:
        return 5
    elif doc_count > 1_000_000:
        return 3
    elif doc_count > 100_000:
        return 2
    else:
        return 1


def get_mapping(index_name: str) -> dict:
    if index_name.startswith('topic_document_sharded'):
        return {
            "properties": {
                "datetime": {
                    "type": "date"
                },
                "document_es_id": {
                    "type": "keyword",
                },
                "document_source": {
                    "type": "keyword",
                },
                "topic_id": {
                    "type": "keyword",
                },
                "topic_weight": {
                    "type": "float"
                }
            }
        }
    elif index_name.startswith('document_eval'):
        return {
            "properties": {
                "document_datetime": {
                    "type": "date"
                },
                "document_es_id": {
                    "type": "keyword"
                },
                "document_source": {
                    "type": "keyword"
                },
                "value": {
                    "type": "float"
                },
                "topic_ids_top": {
                    "type": "keyword"
                },
                "topic_ids_bottom": {
                    "type": "keyword"
                },
            }
        }
    return {}
