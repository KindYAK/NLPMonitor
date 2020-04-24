def default_parser(widget_ner_query, datetime_from, datetime_to, parent_search):
    """
    name_query_example = 'Пандемия Короновируса в Казахстане'
    ner_query_example = '1(|) AND 2(1(|||) $ 3(||||||) $ 4(|||||) $ 3(||||||||||||)) AND 2(||)'
    :param widget_ner_query:
    :param datetime_from:
    :param datetime_to:
    :param parent_search:
    :return:
    """

    from elasticsearch_dsl import Search
    from nlpmonitor.settings import ES_INDEX_DOCUMENT, ES_CLIENT

    documents = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter('range', datetime={'gte': datetime_from}). \
        filter('range', datetime={'lte': datetime_to}). \
        source(['_id'])

    done_queries_list = list()
    for query in widget_ner_query.split(' AND '):
        done_queries_list.append(parse_query(query=query))

    q = parse_list_of_queries(q_list=done_queries_list, num=len(done_queries_list))

    s = apply_query(q=q,
                    parent_search=parent_search,
                    search_lvl="SEARCH_LVL_HARD",
                    documents=documents,
                    cutoff='ABS_MAX_RESULTS_CUTOFF')

    return s


def apply_query(q, parent_search, search_lvl, documents, cutoff):
    from mainapp.constants import SEARCH_CUTOFF_CONFIG

    docs_with_applied_query = documents.query(q)
    new_query = docs_with_applied_query[:SEARCH_CUTOFF_CONFIG[search_lvl][cutoff]]
    executed_query = new_query.execute()
    search_ids = [d.meta.id for d in executed_query]
    new_search = parent_search.filter('terms', document_es_id=search_ids)

    return new_search


def create_elementary_query(words, num):
    from elasticsearch_dsl import Q
    number = isinstance_validator(num)
    return Q(
            'bool',
            should=[Q("match_phrase", text_lemmatized=k.strip()) for k in words.split("|")] +
                   [Q("match_phrase", text=k.strip()) for k in words.split("|")] +
                   [Q("match_phrase", title=k.strip()) for k in words.split("|")],
            minimum_should_match=int(number)
            )


def parse_list_of_queries(q_list, num):
    from elasticsearch_dsl import Q
    number = isinstance_validator(num)
    return Q(
            'bool',
            should=q_list,
            minimum_should_match=int(number)
            )


def parse_query(query):
    import re
    nums = re.findall('\d(?![^(]*\))', query)
    depth = True if re.findall('\D', query)[:2].count('(') - 1 else False
    if len(nums) > 1:

        if depth:
            start_id = query.find('(') + 1  # скипаем начало строки где 2 скобки (re не обрабатывает такую скобку)
            parsed_text = re.findall('(?<=\().+?(?=\))', query[start_id:-1])  # получаем строку
            minimum_should_match_first = nums[0]  # вытаскиваем первое число для query_list парсера
            del nums[0]  # больше не нужно
        else:
            parsed_text = re.findall('(?<=\().+?(?=\))', query)  # получаем строку
            minimum_should_match_first = len(nums)

        list_of_subqueries = list()
        assert len(nums) == len(parsed_text)
        for sub_text, num in zip(parsed_text, nums):
            list_of_subqueries.append(create_elementary_query(words=sub_text, num=num))

        return parse_list_of_queries(q_list=list_of_subqueries, num=minimum_should_match_first)

    parsed_text = isinstance_validator(re.findall('(?<=\().+?(?=\))', query))
    return create_elementary_query(words=parsed_text, num=nums)


def isinstance_validator(array):
    if isinstance(array, list):
        return array[0]
    else:
        return array


def location_buckets_parser(buckets):
    from geo.models import Locality

    magnitude = list()
    for bucket in buckets:
        if bucket.criterion_value_sum.value is not None:
            magnitude.append(int(bucket.criterion_value_sum.value * 100 + 100))
        else:
            magnitude.append(0)
    mag_max, mag_min = max(magnitude), min(magnitude)
    scaled_data = [abs(int((m - mag_min) * 10 / (mag_max - mag_min) - 10)) for m in magnitude]
    coord_and_z = dict()
    loc_long_lat = {elem['name']: [elem['longitude'], elem['latitude']] for elem in Locality.objects.values()}
    for i, bucket in enumerate(buckets):
        coord_and_z[bucket.key] = loc_long_lat[bucket.key] + [scaled_data[i]]
    coord_and_z = list(coord_and_z.values())

    return coord_and_z
