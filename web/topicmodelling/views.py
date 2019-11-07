import json

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.views.generic import TemplateView
from elasticsearch_dsl import Search

from mainapp.forms import TopicChooseForm
from mainapp.services import apply_fir_filter
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_MODELLING


class TopicDocumentListView(TemplateView):
    template_name = "topicmodelling/topic_document_list.html"

    def get_total_metrics(self, granularity):
        std_total = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
            .filter("term", topic_modelling=self.topic_modelling) \
            .filter("range", topic_weight={"gte": 0.001})
        std_total.aggs.bucket(name="dynamics",
                              agg_type="date_histogram",
                              field="datetime",
                              calendar_interval=granularity) \
                      .metric("dynamics_weight", agg_type="sum", field="topic_weight")
        topic_documents_total = std_total.execute()
        total_metrics_dict = dict(
            (
                t.key_as_string,
                {
                    "size": t.doc_count,
                    "weight": t.dynamics_weight.value
                }
            ) for t in topic_documents_total.aggregations.dynamics.buckets
        )
        return total_metrics_dict

    def get_current_topics_metrics(self, topics, granularity):
        if type(topics) != list:
            topics = [topics]
        std = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
                  .filter("term", topic_modelling=self.topic_modelling) \
                  .filter("terms", topic_id=topics).sort("-topic_weight") \
                  .filter("range", topic_weight={"gte": 0.001}) \
                  .source(['document_es_id', 'topic_weight'])[:100]
        std.aggs.bucket(name="dynamics",
                        agg_type="date_histogram",
                        field="datetime",
                        calendar_interval=granularity) \
            .metric("dynamics_weight", agg_type="sum", field="topic_weight")
        std.aggs.bucket(name="source", agg_type="terms", field="document_source.keyword") \
            .metric("source_weight", agg_type="sum", field="topic_weight")
        topic_documents = std.execute()
        return topic_documents

    def get_documents_with_weights(self, topic_documents):
        sd = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT) \
                 .filter('terms', _id=[d.document_es_id for d in topic_documents]) \
                 .source(('id', 'title', 'source', 'datetime',))[:100]
        documents = sd.execute()
        weight_dict = {}
        for td in topic_documents:
            if td.document_es_id not in weight_dict:
                weight_dict[td.document_es_id] = td.topic_weight
            else:
                weight_dict[td.document_es_id] += td.topic_weight
        for document in documents:
            document.weight = weight_dict[document.meta.id]
        documents = sorted(documents, key=lambda x: x.weight, reverse=True)
        return documents

    def normalize_topic_documnets(self, topic_documents, total_metrics_dict):
        for bucket in topic_documents.aggregations.dynamics.buckets:
            total_weight = total_metrics_dict[bucket.key_as_string]['weight']
            total_size = total_metrics_dict[bucket.key_as_string]['size']
            if total_weight != 0:
                bucket.dynamics_weight.value /= total_weight
            if total_size != 0:
                bucket.doc_count_normal = bucket.doc_count / total_size
            else:
                bucket.doc_count_normal = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = make_template_fragment_key('topic_detail', [kwargs, self.request.GET])
        if cache.get(key):
            return context

        self.topic_modelling = kwargs['topic_modelling']
        if 'topic_name' in kwargs:
            topics = kwargs['topic_name']
        else:
            topics = json.loads(self.request.GET['topics'])
            is_too_many_groups = len(topics) > 50

        # Forms Management
        context['granularity'] = self.request.GET['granularity'] if 'granularity' in self.request.GET else "1w"
        context['smooth'] = True if 'smooth' in self.request.GET else (True if 'granularity' not in self.request.GET else False)

        # Total metrics
        total_metrics_dict = self.get_total_metrics(context['granularity'])

        # Current topic metrics
        topic_documents = self.get_current_topics_metrics(topics, context['granularity'])

        # Get documents, set weights
        documents = self.get_documents_with_weights(topic_documents)

        # Normalize
        self.normalize_topic_documnets(topic_documents, total_metrics_dict)

        # Separate signals
        absolute_power = [bucket.doc_count for bucket in topic_documents.aggregations.dynamics.buckets]
        relative_power = [bucket.doc_count_normal for bucket in topic_documents.aggregations.dynamics.buckets]
        relative_weight = [bucket.dynamics_weight.value for bucket in topic_documents.aggregations.dynamics.buckets]

        # Smooth
        if context['smooth']:
            absolute_power = apply_fir_filter(absolute_power, granularity=context['granularity'])
            relative_power = apply_fir_filter(relative_power, granularity=context['granularity'])
            relative_weight = apply_fir_filter(relative_weight, granularity=context['granularity'])

        # Create context
        context['documents'] = documents
        context['date_ticks'] = [bucket.key_as_string for bucket in topic_documents.aggregations.dynamics.buckets]
        context['absolute_power'] = absolute_power
        context['relative_power'] = relative_power
        context['relative_weight'] = relative_weight
        context['source_weight'] = topic_documents.aggregations.source.buckets
        return context


class TopicsListView(TemplateView):
    template_name = "topicmodelling/topics_list.html"
    form_class = TopicChooseForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = make_template_fragment_key('topics_list', [self.request.GET])
        if cache.get(key):
            return context
        form = self.form_class(data=self.request.GET)
        if form.is_valid():
            context['topic_modelling'] = form.cleaned_data['topic_modelling']

        else:
            context['topic_modelling'] = form.fields['topic_modelling'].choices[0][0]
        form.fields['topic_modelling'].initial = context['topic_modelling']

        # Get topics aggregation
        s = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
            .filter("term", topic_modelling=context['topic_modelling']) \
            .filter("range", topic_weight={"gte": 0.001})
        s.aggs.bucket(name='topics', agg_type="terms", field='topic_id.keyword', size=10000)\
            .metric("topic_weight", agg_type="sum", field="topic_weight")
        result = s.execute()
        topic_info_dict = dict(
            (bucket.key, {
                "count": bucket.doc_count,
                "weight_sum": bucket.topic_weight.value
            }) for bucket in result.aggregations.topics.buckets
        )

        # Get actual topics
        topics = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_MODELLING) \
            .filter("term", **{"name": context['topic_modelling']}) \
            .filter("term", **{"is_ready": True}).execute()[0]['topics']
        # Fill topic objects with meta data
        for topic in topics:
            if topic.id in topic_info_dict:
                topic.size = topic_info_dict[topic.id]['count']
                topic.weight = topic_info_dict[topic.id]['weight_sum']
            else:
                topic.size, topic.weight = 0, 0
            if not topic.topic_words:
                continue
            max_word_weight = max((word.weight for word in topic.topic_words))
            for topic_word in topic.topic_words:
                topic_word.weight /= max_word_weight

        # Normalize topic weights by max
        max_topic_weight = max((topic.weight for topic in topics))
        if max_topic_weight != 0:
            for topic in topics:
                topic.weight /= max_topic_weight

        # Create context
        context['topics'] = sorted([t for t in topics if len(t.topic_words) >= 5],
                                   key=lambda x: x.weight, reverse=True)
        context['rest_weight'] = sum([t.weight for t in topics[10:]])
        context['form'] = form
        return context
