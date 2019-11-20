import datetime

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.views.generic import TemplateView
from elasticsearch_dsl import Search, Q

from evaluation.models import EvalCriterion
from mainapp.forms import TopicChooseForm
from mainapp.services import apply_fir_filter
from mainapp.services_es import filter_by_elscore
from mainapp.models_user import TopicGroup
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_DOCUMENT, ES_INDEX_DOCUMENT_EVAL


class CriterionEvalAnalysisView(TemplateView):
    template_name = "evaluation/criterion_analysis.html"

    def get_total_metrics(self, topic_modelling, criterion, granularity, documents_ids_to_filter):
        std_total = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
            .filter("term", topic_modelling=topic_modelling) \
            .filter("term", criterion_id=criterion.id) \
            .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)})
        if documents_ids_to_filter:
            std_total = std_total.filter("terms", **{'document_es_id.keyword': documents_ids_to_filter})
        std_total.aggs.bucket(name="dynamics",
                              agg_type="date_histogram",
                              field="document_datetime",
                              calendar_interval=granularity)
        topic_documents_total = std_total.execute()
        total_metrics_dict = dict(
            (
                t.key_as_string, t.doc_count,
            ) for t in topic_documents_total.aggregations.dynamics.buckets
        )
        return total_metrics_dict

    def get_current_document_evals(self, topic_modelling, criterion, granularity, documents_ids_to_filter):
        std = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
                  .filter("term", **{'topic_modelling.keyword': topic_modelling}) \
                  .filter("term", criterion_id=criterion.id).sort('-value') \
                  .source(['document_es_id'])
        if documents_ids_to_filter:
            std = std.filter("terms", **{'document_es_id.keyword': documents_ids_to_filter})
        std = std[:100]
        std.aggs.bucket(name="dynamics",
                        agg_type="date_histogram",
                        field="document_datetime",
                        calendar_interval=granularity) \
                .metric("dynamics_weight", agg_type="avg", field="value")
        std.aggs.bucket(name="source", agg_type="terms", field="document_source.keyword") \
            .metric("source_value", agg_type="avg", field="value")
        document_evals = std.execute()

        # Top_news ids
        top_news = set()
        top_news.update((d.document_es_id for d in document_evals))
        std_min = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
                  .filter("term", **{'topic_modelling.keyword': topic_modelling}) \
                  .filter("term", criterion_id=criterion.id).sort('value') \
                  .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}) \
                  .source(['document_es_id'])
        if documents_ids_to_filter:
            std = std.filter("terms", **{'document_es_id.keyword': documents_ids_to_filter})
        std = std[:100]
        document_evals_min = std_min.execute()
        top_news.update((d.document_es_id for d in document_evals_min))
        return document_evals, top_news

    def get_documents_with_values(self, top_news_total, criterions, topic_modelling):
        sd = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
                 .filter('terms', _id=list(top_news_total)) \
                 .source(('id', 'title', 'source', 'datetime',))[:1000]
        documents = sd.scan()
        documents_dict = dict((d.meta.id, d) for d in documents)

        std = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL) \
                .filter("terms", **{'document_es_id.keyword': list(top_news_total)}) \
                .filter("term", **{'topic_modelling.keyword': topic_modelling}) \
                .filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)}) \
                .source(['document_es_id', 'value', 'criterion_id'])[:1000]
        document_evals = std.execute()

        documents_eval_dict = {}
        for td in document_evals:
            if td.document_es_id not in documents_eval_dict:
                documents_eval_dict[td.document_es_id] = {}
                documents_eval_dict[td.document_es_id]['document'] = documents_dict[td.document_es_id]
            documents_eval_dict[td.document_es_id][td.criterion_id] = td.value
        return documents_eval_dict

    def normalize_topic_documnets(self, topic_documents, total_metrics_dict):
        for bucket in topic_documents.aggregations.dynamics.buckets:
            total_size = total_metrics_dict[bucket.key_as_string]
            if total_size != 0:
                bucket.doc_count_normal = bucket.doc_count / total_size
            else:
                bucket.doc_count_normal = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        key = make_template_fragment_key('criterion_analysis', [self.request.GET])
        if cache.get(key):
            return context

        # Form creation
        context['criterions_list'] = EvalCriterion.objects.all()
        context['public_groups'] = TopicGroup.objects.filter(is_public=True)
        context['my_groups'] = TopicGroup.objects.filter(owner=self.request.user)
        s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT_EVAL).filter("range", document_datetime={"gte": datetime.date(2000, 1, 1)})
        s.aggs.bucket(name="topic_modelling", agg_type="terms", field="topic_modelling.keyword")
        context['topic_modellings'] = [tm.key for tm in s.execute().aggregations.topic_modelling.buckets]

        # Forms Management
        context['granularity'] = self.request.GET['granularity'] if 'granularity' in self.request.GET else "1w"
        context['smooth'] = True if 'smooth' in self.request.GET else (
            True if 'granularity' not in self.request.GET else False)
        context['topic_modelling'] = self.request.GET['topic_modelling'] \
                                        if 'topic_modelling' in self.request.GET else \
                                        context['topic_modellings'][0]
        context['criterions'] = EvalCriterion.objects.filter(id__in=self.request.GET.getlist('criterions')) \
                                    if 'criterions' in self.request.GET else \
                                    [context['criterions_list'].first()]
        context['keyword'] = self.request.GET['keyword'] if 'keyword' in self.request.GET else ""
        context['group'] = TopicGroup.objects.get(id=self.request.GET['group']) \
                                    if 'group' in self.request.GET and self.request.GET['group'] not in ["-1", "-2", "", None] \
                                    else None
        topics_to_filter = None
        if context['group']:
            topics_to_filter = [topic.topic_id for topic in context['group'].topics.all()]

        is_empty_search = False
        documents_ids_to_filter = []
        if topics_to_filter:
            s = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
                        .filter("terms", **{"topic_id.keyword": topics_to_filter}) \
                        .filter("term", **{"topic_modelling.keyword": context['group'].topic_modelling_name}) \
                        .filter("range", topic_weight={"gte": 0.1}) \
                        .source(("document_es_id", ))[:10000000]
            documents_ids_to_filter = list(set([d.document_es_id for d in s.scan()]))
            if not documents_ids_to_filter:
                is_empty_search = True

        if context['keyword']:
            s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT)
            q = Q('multi_match',
                  query=context['keyword'],
                  fields=['title^10',
                          'tags^3',
                          'categories^3',
                          'text^2'])
            s = s.query(q)
            s = s.source(tuple())
            s = s[:500000]
            r = s.execute()
            cutoff = filter_by_elscore([d.meta.score for d in r], "SEARCH_LVL_HARD")
            keyword_ids_to_filter = [d.meta.id for d in r[:cutoff]]
            if topics_to_filter:
                documents_ids_to_filter = list(set(documents_ids_to_filter).intersection(set(keyword_ids_to_filter)))
            else:
                documents_ids_to_filter = keyword_ids_to_filter
            if not documents_ids_to_filter:
                is_empty_search = True
        if is_empty_search:
            return context

        context['absolute_value'] = {}
        context['source_weight'] = {}
        top_news_total = set()
        for criterion in context['criterions']:
            # Total metrics
            total_metrics_dict = self.get_total_metrics(context['topic_modelling'], criterion, context['granularity'], documents_ids_to_filter)

            # Current topic metrics
            document_evals, top_news = self.get_current_document_evals(context['topic_modelling'], criterion, context['granularity'], documents_ids_to_filter)
            top_news_total.update(top_news)

            # Normalize
            self.normalize_topic_documnets(document_evals, total_metrics_dict)

            # Separate signals
            absolute_value = [(bucket.dynamics_weight.value if bucket.dynamics_weight.value else 0) for bucket in document_evals.aggregations.dynamics.buckets]

            # Smooth
            if context['smooth']:
                absolute_value = apply_fir_filter(absolute_value, granularity=context['granularity'])

            # Create context
            if not 'date_ticks' in context or len(document_evals.aggregations.dynamics.buckets) > len(context['date_ticks']):
                context['date_ticks'] = [bucket.key_as_string for bucket in document_evals.aggregations.dynamics.buckets]
            context['absolute_value'][criterion.id] = absolute_value
            context['source_weight'][criterion.id] = sorted(document_evals.aggregations.source.buckets,
                                                            key=lambda x: x.source_value.value,
                                                            reverse=True)

        # Get documents, set weights
        documents_eval_dict = self.get_documents_with_values(top_news_total, context['criterions'], context['topic_modelling'])
        context['documents'] = documents_eval_dict
        return context
