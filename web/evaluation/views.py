from elasticsearch_dsl.response.aggs import FieldBucket
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.views.generic import TemplateView

from evaluation.models import EvalCriterion
from mainapp.forms import get_topic_weight_threshold_options
from mainapp.models_user import TopicGroup
from mainapp.services import apply_fir_filter
from .services import *


class CacheHit(Exception):
    pass


class EmptySearchException(Exception):
    pass


class CriterionEvalAnalysisView(TemplateView):
    template_name = "evaluation/criterion_analysis.html"

    def form_creation(self, context):
        context['criterions_list'] = EvalCriterion.objects.all()
        context['public_groups'] = TopicGroup.objects.filter(is_public=True)
        context['my_groups'] = TopicGroup.objects.filter(owner=self.request.user)
        indices = ES_CLIENT.indices.get_alias(f"{ES_INDEX_DOCUMENT_EVAL}_*").keys()
        context['topic_modellings'] = list(set([("_".join(tm.split("_")[2:-1]), "_".join(tm.split("_")[2:-1]).replace("bigartm", "tm")) for tm in indices]))

    def form_management(self, context):
        context['granularity'] = self.request.GET['granularity'] if 'granularity' in self.request.GET else "1w"
        context['smooth'] = True if 'smooth' in self.request.GET else (True if 'granularity' not in self.request.GET else False)
        context['topic_modelling'] = self.request.GET['topic_modelling'] if 'topic_modelling' in self.request.GET else context['topic_modellings'][0][0]
        context['public_groups'] = context['public_groups'].filter(topic_modelling_name=context['topic_modelling'])
        context['my_groups'] = context['my_groups'].filter(topic_modelling_name=context['topic_modelling'])
        context['criterions'] = EvalCriterion.objects.filter(id__in=self.request.GET.getlist('criterions')) \
            if 'criterions' in self.request.GET else \
            [context['criterions_list'].first()]
        context['keyword'] = self.request.GET['keyword'] if 'keyword' in self.request.GET else ""
        context['group'] = TopicGroup.objects.get(id=self.request.GET['group']) \
            if 'group' in self.request.GET and self.request.GET['group'] not in ["-1", "-2", "", None] \
            else None
        context['criterion_q'] = self.request.GET['criterion_q'] if 'criterion_q' in self.request.GET else "-1"
        context['action_q'] = self.request.GET['action_q'] if 'action_q' in self.request.GET else "gte"
        try:
            context['value_q'] = float(self.request.GET['value_q'].replace(",", ".")) if 'value_q' in self.request.GET else ""
        except ValueError:
            context['value_q'] = ""
        analytical_query = []
        if context['criterion_q'] != "-1" and context['action_q'] and context['value_q']:
            analytical_query = [
                {
                    "criterion_id": context['criterion_q'],
                    "action": context['action_q'],
                    "value": context['value_q'],
                }
            ]
        context['topic_weight_threshold_options'] = get_topic_weight_threshold_options(self.request.user.is_superuser)
        context['topic_weight_threshold'] = float(self.request.GET['topic_weight_threshold']) \
            if 'topic_weight_threshold' in self.request.GET else \
            0.05

        key = make_template_fragment_key('criterion_analysis', [self.request.GET])
        if cache.get(key):
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
        self.documents_ids_to_filter = documents_ids_to_filter
        self.total_criterion_date_value_dict = total_criterion_date_value_dict
        self.analytical_query = analytical_query
        return max_criterion_value_dict

    def criterion_eval_update_context(self, context, criterion, document_evals, absolute_value, positive, negative):
        context['absolute_value'][criterion.id] = absolute_value
        context['positive'][criterion.id] = positive
        context['negative'][criterion.id] = negative
        if criterion.value_range_from >= 0:
            context['source_weight'][criterion.id] = sorted(document_evals.aggregations.source.buckets,
                                                            key=lambda x: x.source_value.value,
                                                            reverse=True)
        else:
            context['source_weight'][criterion.id] = divide_posneg_source_buckets(document_evals.aggregations.posneg.buckets)

        context['y_axis_from'] = min(-1,
                                     context['y_axis_from'] if 'y_axis_from' in context else -1,
                                     min([bucket.dynamics_weight.value for bucket in absolute_value])
                                     )
        context['y_axis_to'] = max(1,
                                   context['y_axis_to'] if 'y_axis_to' in context else 1,
                                   max([bucket.dynamics_weight.value for bucket in absolute_value])
                                   )
        if criterion.value_range_from < 0:
            context['posneg_distribution'][criterion.id] = document_evals.aggregations.posneg

        context['posneg_top_topics'][criterion.id] = \
            normalize_buckets_main_topics(document_evals.aggregations.posneg.buckets[-1].top_topics.buckets, self.topics_dict)
        context['posneg_bottom_topics'][criterion.id] = \
            normalize_buckets_main_topics(document_evals.aggregations.posneg[0].bottom_topics.buckets, self.topics_dict)

    def get_criterion_evals(self, context, top_news_total, criterion):
        # Current topic metrics
        document_evals, top_news = get_current_document_evals(context['topic_modelling'], criterion,
                                                              context['granularity'],
                                                              self.documents_ids_to_filter,
                                                              analytical_query=self.analytical_query)
        if not top_news:
            return
        top_news_total.update(top_news)

        # Normalize
        normalize_documents_eval_dynamics(document_evals, self.total_criterion_date_value_dict[criterion.id])

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

        # Smooth
        def smooth_buckets(buckets, is_posneg):
            if is_posneg:
                smoothed = apply_fir_filter([bucket.doc_count for bucket in buckets], granularity=context['granularity'], allow_negatives=True)
            else:
                smoothed = apply_fir_filter([bucket.dynamics_weight.value for bucket in buckets], granularity=context['granularity'], allow_negatives=True)
            for bucket, val in zip(buckets, smoothed):
                if is_posneg:
                    bucket.doc_count = val
                else:
                    bucket.dynamics_weight.value = val

        if context['smooth']:
            smooth_buckets(absolute_value, False)
            smooth_buckets(positive, True)
            smooth_buckets(negative, True)

        # Get topic dict
        self.topics_dict = get_topic_dict(context['topic_modelling'])

        # Create context
        self.criterion_eval_update_context(context, criterion, document_evals, absolute_value, positive, negative)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Form creation
        self.form_creation(context)

        # Forms Management
        try:
            max_criterion_value_dict = self.form_management(context)
        except (CacheHit, EmptySearchException):
            return context

        dicts_to_init = ['absolute_value', 'positive', 'negative', 'source_weight',
                         'posneg_distribution', 'posneg_top_topics', 'posneg_bottom_topics']
        for key in dicts_to_init:
            context[key] = {}
        top_news_total = set()
        for criterion in context['criterions']:
            self.get_criterion_evals(context, top_news_total, criterion)

        # Get documents, set weights
        documents_eval_dict = get_documents_with_values(top_news_total, context['criterions'],  context['topic_modelling'], max_criterion_value_dict)
        context['documents'] = documents_eval_dict
        return context
