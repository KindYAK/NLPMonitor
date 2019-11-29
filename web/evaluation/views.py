from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.views.generic import TemplateView

from evaluation.models import EvalCriterion
from mainapp.forms import get_topic_weight_threshold_options
from mainapp.models_user import TopicGroup
from mainapp.services import apply_fir_filter
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT_EVAL
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
        s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
            .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)})
        s.aggs.bucket(name="topic_modelling", agg_type="terms", field="topic_modelling.keyword")
        context['topic_modellings'] = [(tm.key, tm.key.replace("bigartm", "tm")) for tm in
                                       s.execute().aggregations.topic_modelling.buckets]

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

    def criterion_eval_update_context(self, context, criterion, document_evals, absolute_value):
        if not 'date_ticks' in context or len(document_evals.aggregations.dynamics.buckets) > len(
                context['date_ticks']):
            context['date_ticks'] = [bucket.key_as_string for bucket in document_evals.aggregations.dynamics.buckets]
        context['absolute_value'][criterion.id] = absolute_value
        if criterion.value_range_from >= 0:
            context['source_weight'][criterion.id] = sorted(document_evals.aggregations.source.buckets,
                                                            key=lambda x: x.source_value.value,
                                                            reverse=True)
        if criterion.value_range_from >= 0:
            context['source_weight'][criterion.id] = sorted(document_evals.aggregations.source.buckets,
                                                            key=lambda x: x.source_value.value,
                                                            reverse=True)
        else:
            sources_criterion_dict = {}
            for i, pn in enumerate(document_evals.aggregations.posneg.buckets):
                for bucket in pn.source.buckets:
                    if bucket.key not in sources_criterion_dict:
                        sources_criterion_dict[bucket.key] = {}
                        sources_criterion_dict[bucket.key]['key'] = bucket.key
                        sources_criterion_dict[bucket.key]['positive'] = 0
                        sources_criterion_dict[bucket.key]['neutral'] = 0
                        sources_criterion_dict[bucket.key]['negative'] = 0
                    tonality = ["positive", "neutral", "negative"][i]
                    sources_criterion_dict[bucket.key][tonality] = bucket.doc_count
            context['source_weight'][criterion.id] = sorted(sources_criterion_dict.values(),
                                                            key=lambda x: x['positive'] + x['negative'] + x['neutral'],
                                                            reverse=True)
        context['y_axis_from'] = min(-1,
                                     context['y_axis_from'] if 'y_axis_from' in context else -1,
                                     min(absolute_value)
                                     )
        context['y_axis_to'] = max(1,
                                   context['y_axis_to'] if 'y_axis_to' in context else 1,
                                   max(absolute_value)
                                   )

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

        # Separate signals
        absolute_value = [bucket.dynamics_weight.value for bucket in document_evals.aggregations.dynamics.buckets]

        # Smooth
        if context['smooth']:
            absolute_value = apply_fir_filter(absolute_value, granularity=context['granularity'], allow_negatives=True)

        # Create context
        self.criterion_eval_update_context(context, criterion, document_evals, absolute_value)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Form creation
        self.form_creation(context)

        # Forms Management
        try:
            max_criterion_value_dict = self.form_management(context)
        except (CacheHit, EmptySearchException):
            return context

        context['absolute_value'] = {}
        context['source_weight'] = {}
        top_news_total = set()
        for criterion in context['criterions']:
            self.get_criterion_evals(context, top_news_total, criterion)

        # Get documents, set weights
        documents_eval_dict = get_documents_with_values(top_news_total, context['criterions'],  context['topic_modelling'], max_criterion_value_dict)
        context['documents'] = documents_eval_dict
        return context
