import datetime
from copy import deepcopy

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from evaluation.models import EvalCriterionGroup, EvalCriterion
from evaluation.services import get_documents_with_values, divide_posneg_source_buckets, normalize_buckets_main_topics, \
    get_low_volume_positive_topics, get_current_document_evals, smooth_buckets, get_topic_dict, \
    get_total_group_dynamics, normalize_documents_eval_dynamics, normalize_documents_eval_dynamics_with_virt_negative, \
    get_documents_ids_filter, get_criterions_values_for_normalization
from evaluation.utils import parse_eval_index_name
from mainapp.forms import get_topic_weight_threshold_options
from mainapp.models import Source
from mainapp.models_user import TopicGroup
from mainapp.services import get_user_group, unique_ize
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT_EVAL


class CacheHit(Exception):
    pass


class EmptySearchException(Exception):
    pass


class Forbidden(Exception):
    pass


def form_creation(request, context):
    group = get_user_group(request.user)
    eval_indices = ES_CLIENT.indices.get_alias(f"{ES_INDEX_DOCUMENT_EVAL}_*").keys()
    if request.user.is_superuser:
        context['criterions_list'] = EvalCriterion.objects.all()
    else:
        if not group:
            raise Forbidden("403")
        context['criterions_list'] = EvalCriterion.objects.filter(usergroup=group)
        eval_indices = filter(lambda x: parse_eval_index_name(x)['topic_modelling'] in group.topic_modelling_names.split(","), eval_indices)
    context['public_groups'] = TopicGroup.objects.filter(is_public=True)
    context['my_groups'] = TopicGroup.objects.filter(owner=request.user)
    context['topic_modellings'] = list(sorted(list(set(
        [(parse_eval_index_name(tm)['topic_modelling'], parse_eval_index_name(tm)['topic_modelling'].replace("bigartm", "tm")) for tm in eval_indices if not parse_eval_index_name(tm)['ignore']]
    ))))
    if not context['topic_modellings']:
        raise Forbidden("403")
    context['sources_list'] = Source.objects.filter(document__isnull=False).distinct()
    context['top_news_num'] = 1000


def form_management(request, context, skip_cache=False):
    context['granularity'] = request.GET['granularity'] if 'granularity' in request.GET else "1w"
    context['smooth'] = True if 'smooth' in request.GET else (True if 'granularity' not in request.GET else False)

    context['topic_modelling'] = request.GET['topic_modelling'] if 'topic_modelling' in request.GET else context['topic_modellings'][0][0]
    context['public_groups'] = context['public_groups'].filter(topic_modelling_name=context['topic_modelling'])
    context['my_groups'] = context['my_groups'].filter(topic_modelling_name=context['topic_modelling'])

    eval_indices = ES_CLIENT.indices.get_alias(f"{ES_INDEX_DOCUMENT_EVAL}_{context['topic_modelling']}_*").keys()

    criterions = context['criterions_list'].filter(id__in=[parse_eval_index_name(index)['criterion_id'] for index in eval_indices]).distinct()
    criterions_dict = dict(
        (c.id, c) for c in criterions
    )
    context['criterions_list'] = []
    for index in eval_indices:
        index = parse_eval_index_name(index)
        if index['ignore']:
            continue
        criterion = deepcopy(criterions_dict[index['criterion_id']])
        criterion.id_postfix = index['criterion.id_postfix']
        if index['postfix']:
            criterion.name = criterion.name + ("_" + index['postfix'] if index['postfix'] else "")
        context['criterions_list'].append(criterion)
    criterions_list_dict = dict(
        (c.id_postfix, c) for c in context['criterions_list']
    )

    context['criterions'] = [criterions_list_dict[c] for c in request.GET.getlist('criterions')] \
        if 'criterions' in request.GET else \
        [context['criterions_list'][0]]
    context['sources'] = Source.objects.filter(id__in=request.GET.getlist('sources')) \
        if 'sources' in request.GET else None
    context['keyword'] = request.GET['keyword'] if 'keyword' in request.GET else ""
    context['group'] = TopicGroup.objects.get(id=request.GET['group']) \
        if 'group' in request.GET and request.GET['group'] not in ["-1", "-2", "", None] \
        else None
    context['criterion_q'] = request.GET['criterion_q'] if 'criterion_q' in request.GET else "-1"
    context['action_q'] = request.GET['action_q'] if 'action_q' in request.GET else "gte"
    try:
        context['value_q'] = float(request.GET['value_q'].replace(",", ".")) if 'value_q' in request.GET else ""
    except ValueError:
        context['value_q'] = ""
    analytical_query = []
    if context['criterion_q'] != "-1" and context['action_q'] != "" and context['value_q'] != "":
        analytical_query = [
            {
                "criterion_id": context['criterion_q'],
                "action": context['action_q'],
                "value": context['value_q'],
            }
        ]
    context['topic_weight_threshold_options'] = get_topic_weight_threshold_options(request.user.is_superuser)
    context['topic_weight_threshold'] = float(request.GET['topic_weight_threshold']) \
        if 'topic_weight_threshold' in request.GET else \
        0.05

    key = make_template_fragment_key('criterion_analysis', [context['topic_modelling'],
                                                            context['topic_weight_threshold'], context['criterions'],
                                                            context['sources'], context['keyword'],
                                                            context['group'], context['granularity'],
                                                            context['smooth'], context['action_q'],
                                                            context['value_q'], context['criterion_q'],
                                                            ])
    if cache.get(key) and not skip_cache:
        raise CacheHit()

    topics_to_filter = None
    if context['group']:
        topics_to_filter = [topic.topic_id for topic in context['group'].topics.all()]

    is_empty_search, documents_ids_to_filter = get_documents_ids_filter(topics_to_filter, context['keyword'],
                                                                        context['group'].topic_modelling_name if context['group'] else None,
                                                                        context['topic_weight_threshold'])
    if is_empty_search:
        raise EmptySearchException()

    max_criterion_value_dict, total_criterion_date_value_dict = \
        get_criterions_values_for_normalization(context['criterions'], context['topic_modelling'],
                                                granularity=context['granularity'] if ((context['keyword'] or context['group'])) else None,
                                                analytical_query=analytical_query)
    documents_ids_to_filter = documents_ids_to_filter
    total_criterion_date_value_dict = total_criterion_date_value_dict
    analytical_query = analytical_query
    return documents_ids_to_filter, total_criterion_date_value_dict, analytical_query, max_criterion_value_dict


def get_analytics_context(request, context, skip_cache=False):
    # Form creation
    try:
        form_creation(request, context)
    except Forbidden:
        context['error'] = "FORBIDDEN 403"
        return context
    # Forms Management
    try:
        documents_ids_to_filter, total_criterion_date_value_dict, analytical_query, max_criterion_value_dict = form_management(request, context, skip_cache=skip_cache)
    except (CacheHit, EmptySearchException):
        return context

    dicts_to_init = ['absolute_value', 'positive', 'negative', 'source_weight',
                     'posneg_distribution', 'posneg_top_topics', 'posneg_bottom_topics',
                     'group_total_dynamics', 'low_volume_positive_topics']
    for key in dicts_to_init:
        context[key] = {}

    # Info by criterion
    top_news_total = set()
    for criterion in context['criterions']:
        get_criterion_evals(context, top_news_total, criterion, documents_ids_to_filter, analytical_query, total_criterion_date_value_dict)

    # Info by group
    context['groups'] = [
        {
            "id": group.id,
            "name": group.name,
            "criterions": group.criterions.all(),
        }
        for group in EvalCriterionGroup.objects.filter(criterions__in=context['criterions']).distinct()]
    for group in context['groups']:
        get_group_evals(context, group)

    # Get documents, set weights
    documents_eval_dict = get_documents_with_values(top_news_total,
                                                    context['criterions'],
                                                    context['topic_modelling'],
                                                    max_criterion_value_dict,
                                                    top_news_num=context['top_news_num'])
    context['documents'] = unique_ize(documents_eval_dict.values(),
                                      key=lambda x: x['document'].id)[:context['top_news_num']]
    return context


def criterion_eval_update_context(context, criterion, document_evals, absolute_value, positive, negative, topics_dict, tm_dict):
    # Dynamics
    context['absolute_value'][criterion.id] = absolute_value
    context['positive'][criterion.id] = positive
    context['negative'][criterion.id] = negative
    if criterion.value_range_from >= 0:
        context['source_weight'][criterion.id] = sorted(document_evals.aggregations.source.buckets,
                                                        key=lambda x: x.value,
                                                        reverse=True)
    else:
        context['source_weight'][criterion.id] = divide_posneg_source_buckets(document_evals.aggregations.posneg.buckets)

    context['y_axis_from'] = min(
                                     criterion.value_range_from,
                                     context['y_axis_from'] if 'y_axis_from' in context else criterion.value_range_from,
                                     min([bucket.dynamics_weight.value for bucket in absolute_value])
                                 )
    max_value = max([bucket.dynamics_weight.value for bucket in absolute_value])
    context['y_axis_to'] = max(
                                   context['y_axis_to'] if 'y_axis_to' in context else max_value,
                                   max_value,
                               )

    # Posneg distribution
    if criterion.value_range_from < 0:
        context['posneg_distribution'][criterion.id] = document_evals.aggregations.posneg

    # Top and bottom topics
    last_date = datetime.datetime.strptime(absolute_value[-1].key_as_string[:10], "%Y-%m-%d").date()
    context['posneg_top_topics'][criterion.id] = \
        normalize_buckets_main_topics(document_evals.aggregations.posneg.buckets[-1].top_topics.buckets,
                                      topics_dict, tm_dict, context['topic_weight_threshold'], last_date)
    context['posneg_bottom_topics'][criterion.id] = \
        normalize_buckets_main_topics(document_evals.aggregations.posneg[0].bottom_topics.buckets,
                                      topics_dict, tm_dict, context['topic_weight_threshold'], last_date)

    # Get non-highlighted topics
    context['low_volume_positive_topics'][criterion.id] = get_low_volume_positive_topics(tm_dict,
                                                                                         topics_dict,
                                                                                         criterion,
                                                                                         context['topic_weight_threshold'])


def get_criterion_evals(context, top_news_total, criterion, documents_ids_to_filter, analytical_query, total_criterion_date_value_dict):
    # Current topic metrics
    document_evals, top_news = get_current_document_evals(context['topic_modelling'], criterion,
                                                          context['granularity'],
                                                          context['sources'],
                                                          documents_ids_to_filter,
                                                          analytical_query=analytical_query,
                                                          top_news_num=context['top_news_num'])
    if not top_news:
        return
    top_news_total.update(top_news)

    # Normalize
    if not criterion.calc_virt_negative:
        normalize_documents_eval_dynamics(document_evals, total_criterion_date_value_dict[criterion.id])
    else:
        normalize_documents_eval_dynamics_with_virt_negative(document_evals,
                                                             context['topic_modelling'],
                                                             context['granularity'],
                                                             criterion)

    absolute_value = document_evals.aggregations.dynamics.buckets
    positive = []
    negative = []
    if criterion.value_range_from < 0:
        negative = list(document_evals.aggregations.posneg.buckets[0].dynamics.buckets)
        positive = list(document_evals.aggregations.posneg.buckets[-1].dynamics.buckets)
        # Equalize periods
        positive_ticks = set([bucket.key_as_string for bucket in positive])
        negative_ticks = set([bucket.key_as_string for bucket in negative])
        class Bucket(object):
            pass
        for tick in positive_ticks - negative_ticks:
            bucket = Bucket()
            setattr(bucket, "key_as_string", tick)
            setattr(bucket, "doc_count", 0)
            negative.append(bucket)
        for tick in negative_ticks - positive_ticks:
            bucket = Bucket()
            setattr(bucket, "key_as_string", tick)
            setattr(bucket, "doc_count", 0)
            positive.append(bucket)
        positive = sorted(positive, key=lambda x: x.key_as_string)
        negative = sorted(negative, key=lambda x: x.key_as_string)

    if context['smooth']:
        smooth_buckets(absolute_value,
                       is_posneg=False,
                       granularity=context['granularity'])
        smooth_buckets(positive,
                       is_posneg=True,
                       granularity=context['granularity'])
        smooth_buckets(negative,
                       is_posneg=True,
                       granularity=context['granularity'])

    # Get topic dict
    topics_dict, tm_dict = get_topic_dict(context['topic_modelling'])

    # Create context
    criterion_eval_update_context(context, criterion, document_evals, absolute_value, positive, negative, topics_dict, tm_dict)
    return topics_dict, tm_dict


def get_group_evals(context, group):
    context['group_total_dynamics'][group['id']] = get_total_group_dynamics(
                                                        context['absolute_value'],
                                                        group['criterions'],
                                                        context['granularity'],
                                                        context['smooth'],
                                                    )
