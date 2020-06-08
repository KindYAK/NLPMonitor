import json
from copy import deepcopy

from annoying.functions import get_object_or_None
from django.db.utils import IntegrityError
from rest_framework import viewsets
from rest_framework.response import Response

from evaluation.models import EvalCriterion, TopicIDEval
from evaluation.services import *
from evaluation.utils import parse_eval_index_name
from mainapp.services import get_user_group
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_DOCUMENT, ES_INDEX_DOCUMENT_EVAL
from .serializers import *


class TopicGroupViewSet(viewsets.ViewSet):
    def list(self, request):
        if not 'topic_modelling' in request.GET:
            return Response(
                {
                    "status": 500,
                    "error": "You need to specify topic_modelling GET parameter"
                }
            )
        topic_modelling_name = request.GET['topic_modelling']
        topic_groups = TopicGroup.objects.filter(topic_modelling_name=topic_modelling_name).order_by('name')
        topic_groups_my = topic_groups.filter(owner=request.user).prefetch_related('topics')
        topic_groups_public = topic_groups.filter(is_public=True).prefetch_related('topics')

        return Response(
            {
                "my_groups": TopicGroupSerializer(topic_groups_my, many=True).data,
                "public_groups": TopicGroupSerializer(topic_groups_public, many=True).data,
                "status": 200,
            }
        )

    def partial_update(self, request, pk=None):
        if 'topic_id' not in request.POST or 'is_checked' not in request.POST:
            return Response(
                {
                    "status": 500,
                    "error": "You need to specify topic_id and is_checked POST parameters"
                }
            )
        topic_group = TopicGroup.objects.get(id=pk)
        topic_id = request.POST['topic_id']
        is_checked = request.POST['is_checked'] == "true"

        if is_checked:
            topic_id_obj = get_object_or_None(TopicID,
                                          topic_id=topic_id,
                                          topic_modelling_name=topic_group.topic_modelling_name)
            if not topic_id_obj:
                topic_id_obj = TopicID.objects.create(topic_id=topic_id,
                                       topic_modelling_name=topic_group.topic_modelling_name)
            topic_group.topics.add(topic_id_obj)
            return Response(
                {
                    "status": 200,
                    "result": "added",
                    "topic_id": topic_id,
                    "group_id": topic_group.id,
                }
            )
        else:
            topic_to_delete = topic_group.topics.filter(topic_id=topic_id,
                                                        topic_modelling_name=topic_group.topic_modelling_name)
            if not topic_to_delete.exists():
                return Response(
                    {
                        "status": 500,
                        "error": "Something went wrong while trying to delete"
                    }
                )
            topic_group.topics.remove(*topic_to_delete)
            return Response(
                {
                    "status": 200,
                    "result": "removed",
                    "topic_id": topic_id,
                    "group_id": topic_group.id,
                }
            )

    def create(self, request):
        if 'name' not in request.POST or 'topic_modelling' not in request.POST:
            return Response(
                {
                    "status": 500,
                    "error": "You need to specify topic_id and is_checked POST parameters"
                }
            )
        try:
            group = TopicGroup.objects.create(name=request.POST['name'],
                                              topic_modelling_name=request.POST['topic_modelling'],
                                              owner=request.user,
                                              is_public=bool(request.user.is_superuser or request.user.expert)
                                             )
        except IntegrityError:
            return Response(
                {
                    "status": 500,
                    "error": "Группа с таким названием уже существует",
                }
            )
        return Response(
            {
                "status": 200,
                "id": group.id,
                "name": group.name,
                "is_public": group.is_public,
            }
        )

    def destroy(self, request, pk=None):
        TopicGroup.objects.get(id=pk).delete()
        return Response(
            {
                "status": 200,
                "group_id": int(pk),
            }
        )


class CriterionEvalViewSet(viewsets.ViewSet):
    def list(self, request):
        if not 'topic_modelling' in request.GET:
            return Response(
                {
                    "status": 500,
                    "error": "You need to specify topic_modelling GET parameter"
                }
            )

        topic_modelling = request.GET['topic_modelling']
        topic_id_evals = TopicIDEval.objects.filter(weight=1, topic_id__topic_modelling_name=topic_modelling).distinct()
        topics_evals = TopicsEval.objects.filter(topicideval__in=topic_id_evals, author=request.user).distinct()
        criterions = EvalCriterion.objects.filter(topicseval__in=topics_evals).distinct()

        criterions_dict = {}
        for criterion in criterions:
            for topics_eval in topics_evals:
                if topics_eval.criterion != criterion:
                    continue
                if criterion.id not in criterions_dict:
                    criterions_dict[criterion.id] = {}
                criterions_dict[criterion.id][topics_eval.topics.first().topic_id] = topics_eval.value
        return Response(
            {
                "status": 200,
                "criterions": criterions_dict,
            }
        )

    def create(self, request):
        if 'topic_modelling' not in request.POST or \
                    'topic_id' not in request.POST or \
                    'criterion_id' not in request.POST or \
                    'value' not in request.POST:
            return Response(
                {
                    "status": 500,
                    "error": "You need to specify topic_modelling, topic_id, criterion_id and value POST parameters"
                }
            )

        topic_modelling = request.POST['topic_modelling']
        topic_id = request.POST['topic_id']
        criterion_id = request.POST['criterion_id']
        value = float(request.POST['value'])

        topic_id_obj = get_object_or_None(TopicID, topic_modelling_name=topic_modelling, topic_id=topic_id)
        if not topic_id_obj:
            topic_id_obj = TopicID.objects.create(topic_modelling_name=topic_modelling, topic_id=topic_id)
        topics_eval = get_object_or_None(TopicsEval, topics=topic_id_obj, topicideval__weight=1, criterion__id=criterion_id, author=request.user)
        if topics_eval:
            topics_eval.value = value
            topics_eval.save()
        else:
            topics_eval = TopicsEval.objects.create(criterion_id=criterion_id, value=value, author=request.user)
            TopicIDEval.objects.create(
                topic_id=topic_id_obj,
                topics_eval=topics_eval,
                weight=1
            )
        return Response(
            {
                "status": 200,
                "value": value,
                "criterion_id": criterion_id,
                "topic_id": topic_id,
            }
        )


class RangeDocumentsViewSet(viewsets.ViewSet):
    def topics_search(self):
        topic_modelling = self.request.GET['topic_modelling']
        topic_weight_threshold = float(self.request.GET['topic_weight_threshold'])
        topics = json.loads(self.request.GET['topics'])
        date_from = datetime.datetime.strptime(self.request.GET['date_from'][:10], "%Y-%m-%d").date()
        date_to = datetime.datetime.strptime(self.request.GET['date_to'][:10], "%Y-%m-%d").date()

        std = Search(using=ES_CLIENT, index=f"{ES_INDEX_TOPIC_DOCUMENT}_{topic_modelling}") \
                  .filter("terms", topic_id=topics).sort("-topic_weight") \
                  .filter("range", topic_weight={"gte": topic_weight_threshold}) \
                  .filter("range", datetime={"gte": date_from}) \
                  .filter("range", datetime={"lte": date_to}) \
                  .source(['document_es_id', 'topic_weight'])[:100]
        std.aggs.bucket(name="source", agg_type="terms", field="document_source") \
            .metric("source_weight", agg_type="sum", field="topic_weight")
        topic_documents = std.execute()

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
        return documents, topic_documents.aggregations.source.buckets

    def search_search(self):
        date_from = datetime.datetime.strptime(self.request.GET['datetime_from'][:10], "%Y-%m-%d").date()
        date_to = datetime.datetime.strptime(self.request.GET['datetime_to'][:10], "%Y-%m-%d").date()
        s = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).source(('id', 'datetime', 'title', 'source', ))
        s = s.filter('range', datetime={"gte": date_from})
        s = s.filter('range', datetime={"lte": date_to})
        if self.request.GET['corpuses'] and self.request.GET['corpuses'] != "None":
            corpus_ids = json.loads(self.request.GET['corpuses'].replace("'", '"'))
            cs = Corpus.objects.filter(id__in=corpus_ids)
            s = s.filter('terms', **{"corpus": [c.name for c in cs]})
        if self.request.GET['sources'] and self.request.GET['sources'] != "None":
            sources_ids = json.loads(self.request.GET['sources'].replace("'", '"'))
            ss = Source.objects.filter(id__in=sources_ids)
            s = s.filter('terms', **{"source.keyword": [s.name for s in ss]})
        if self.request.GET['authors'] and self.request.GET['authors'] != "None":
            author_ids = json.loads(self.request.GET['authors'].replace("'", '"'))
            aus = Author.objects.filter(id__in=author_ids)
            s = s.filter('terms', **{"author.keyword": [a.name for a in aus]})
        if self.request.GET['title']:
            s = s.filter('match', title=self.request.GET['title'])
        if self.request.GET['text']:
            q = Q('multi_match',
                  query=self.request.GET['text'],
                  fields=['title^10',
                          'tags^3',
                          'categories^3',
                          'text^2'])
            s = s.query(q)
        s = s[:100]
        s.aggs.bucket(name="source", agg_type="terms", field="source.keyword") \
            .metric("source_weight", agg_type="sum", field="topic_weight")
        documents = s.execute()
        return documents, documents.aggregations.source.buckets

    def search_criterions(self):
        date_from = datetime.datetime.strptime(self.request.GET['date_from'][:10], "%Y-%m-%d").date()
        date_to = datetime.datetime.strptime(self.request.GET['date_to'][:10], "%Y-%m-%d").date()
        topic_modelling = self.request.GET['topic_modelling']
        criterions = EvalCriterion.objects.filter(id__in=self.request.GET.getlist('criterions'))
        sources = Source.objects.filter(id__in=self.request.GET.getlist('sources'))
        keyword = self.request.GET['keyword'] if 'keyword' in self.request.GET else ""
        group = TopicGroup.objects.get(id=self.request.GET['group']) \
            if 'group' in self.request.GET and self.request.GET['group'] not in ["-1", "-2", "", "None", None] \
            else None
        topics_to_filter = None
        if group:
            topics_to_filter = [topic.topic_id for topic in group.topics.all()]
        topic_weight_threshold = float(self.request.GET['topic_weight_threshold']) if 'topic_weight_threshold' in self.request.GET else 0.05
        criterion_q = self.request.GET['criterion_q'] if 'criterion_q' in self.request.GET else "-1"
        action_q = self.request.GET['action_q'] if 'action_q' in self.request.GET else ""
        try:
            value_q = float(self.request.GET['value_q'].replace(",", ".")) if 'value_q' in self.request.GET else ""
        except ValueError:
            value_q = ""
        analytical_query = []
        if criterion_q != "-1" and action_q and value_q:
            analytical_query = [
                {
                    "criterion_id": criterion_q,
                    "action": action_q,
                    "value": value_q,
                }
            ]
        is_empty_search, documents_ids_to_filter = get_documents_ids_filter(topics_to_filter, keyword,
                                                                            group.topic_modelling_name if group else None,
                                                                            topic_weight_threshold)
        if is_empty_search:
            return [], []

        max_criterion_value_dict, _ = get_criterions_values_for_normalization(criterions, topic_modelling,
                                                                              analytical_query=analytical_query)
        source_weight = {}
        posneg_distribution = {}
        posneg_top_topics = {}
        posneg_bottom_topics = {}
        low_volume_positive_topics = {}
        top_news_total = set()
        for criterion in criterions:
            # Current topic metrics
            document_evals, top_news = get_current_document_evals(topic_modelling, criterion, None,
                                                                  sources,
                                                                  documents_ids_to_filter,
                                                                  date_from, date_to,
                                                                  analytical_query=analytical_query)
            top_news_total.update(top_news)
            if criterion.value_range_from < 0:
                source_weight[criterion.id] = divide_posneg_source_buckets(document_evals.aggregations.posneg.buckets)
                posneg_distribution[criterion.id] = document_evals.aggregations.posneg.buckets
            else:
                source_weight[criterion.id] = sorted(document_evals.aggregations.source.buckets,
                                                     key=lambda x: x.value,
                                                     reverse=True)

            # Main topics
            topics_dict, tm_dict = get_topic_dict(topic_modelling)
            posneg_top_topics[criterion.id] = \
                normalize_buckets_main_topics(document_evals.aggregations.posneg.buckets[-1].top_topics.buckets,
                                            topics_dict, tm_dict, topic_weight_threshold, date_to)
            posneg_bottom_topics[criterion.id] = \
                normalize_buckets_main_topics(document_evals.aggregations.posneg.buckets[0].bottom_topics.buckets,
                                              topics_dict, tm_dict, topic_weight_threshold, date_to)

            # Get non-highlighted topics
            low_volume_positive_topics[criterion.id] = get_low_volume_positive_topics(tm_dict,
                                                                                      topics_dict,
                                                                                      criterion,
                                                                                      topic_weight_threshold,
                                                                                      date_from,
                                                                                      date_to)

        # Get documents, set weights
        documents_eval_dict = get_documents_with_values(top_news_total, criterions, topic_modelling, max_criterion_value_dict,
                                                        date_from, date_to).values()

        return documents_eval_dict, source_weight, posneg_distribution, posneg_top_topics, posneg_bottom_topics, low_volume_positive_topics

    def list(self, request):
        filter_type = request.GET['type']
        posneg_distribution = {}
        posneg_top_topics = {}
        posneg_bottom_topics = {}
        low_volume_positive_topics = {}
        if filter_type == "topics":
            documents, source_buckets = self.topics_search()
        elif filter_type == "search":
            documents, source_buckets = self.search_search()
        elif filter_type == "criterions":
            documents, source_buckets, posneg_distribution, \
                posneg_top_topics, posneg_bottom_topics, \
                low_volume_positive_topics = self.search_criterions()
        else:
            return Response(
                {
                    "status": 400,
                    "error": "Search type not implemented",
                }
            )

        def get_value_or_weight(document):
            if hasattr(document, "weight") and document.weight:
                return round(document.weight, 3)
            if hasattr(document, "value") and document.value:
                return round(document.value, 3)
            if document.meta.score:
                return round(document.meta.score, 3) if document.meta.score != 0 else 1.000
            return 1

        if filter_type in ["topics", "search"]:
            source_weights = [
                        {
                            "source": bucket.key,
                            "weight": bucket.source_weight.value,
                        } for bucket in sorted(source_buckets, key=lambda x: x.source_weight.value, reverse=True)
                    ]
            documents = [
                {
                    "id": document.id,
                    "weight": get_value_or_weight(document),
                    "title": document.title,
                    "source": document.source,
                    "datetime": document.datetime,
                } for document in documents
            ]
        elif filter_type in ["criterions"]:
            posneg_distribution = dict(
                (key, [b.doc_count for b in bucket])
                for key, bucket in posneg_distribution.items()
            )
            posneg_top_topics = dict(
                (criterion_id, [bucket.to_dict() for bucket in buckets])
                    for criterion_id, buckets in posneg_top_topics.items()
            )
            posneg_bottom_topics = dict(
                (criterion_id, [bucket.to_dict() for bucket in buckets])
                    for criterion_id, buckets in posneg_bottom_topics.items()
            )
            source_weights = dict(
                ((criterion_id,
                    [
                        {
                            "source": bucket.key,
                            "weight": bucket.value,
                        } for bucket in sorted(buckets, key=lambda x: x.value, reverse=True)
                    ]
                ) if buckets and hasattr(buckets[0], "doc_count") else (criterion_id, buckets)) for criterion_id, buckets in source_buckets.items()
            )
            for document in documents:
                document["document"] = {
                    "id": document["document"].id,
                    "title": document["document"].title,
                    "source": document["document"].source,
                    "datetime": document["document"].datetime,
                }
        else:
            return Response(
                {
                    "status": 400,
                    "error": "Search type not implemented",
                }
            )

        return Response(
            {
                "status": 200,
                "documents": documents,
                "source_weights": source_weights,
                "posneg_distribution": posneg_distribution,
                "posneg_top_topics": posneg_top_topics,
                "posneg_bottom_topics": posneg_bottom_topics,
                "low_volume_positive_topics": low_volume_positive_topics
            }
        )


class CriterionEvalUtilViewSet(viewsets.ViewSet):
    def list(self, request):
        if not 'topic_modelling' in request.GET:
            return Response(
                {
                    "status": 500,
                    "error": "You need to specify topic_modelling GET parameter"
                }
            )

        topic_modelling = request.GET['topic_modelling']
        public_groups = TopicGroup.objects.filter(is_public=True, topic_modelling_name=topic_modelling).values('id', 'name')
        my_groups = TopicGroup.objects.filter(owner=self.request.user, topic_modelling_name=topic_modelling).values('id', 'name')

        eval_indices = ES_CLIENT.indices.get_alias(f"{ES_INDEX_DOCUMENT_EVAL}_{topic_modelling}_*").keys()
        criterion_id_labels = [parse_eval_index_name(index)['criterion_id'] for index in eval_indices if not index.endswith("_neg")]
        criterions = EvalCriterion.objects.filter(id__in=criterion_id_labels).distinct().values('id', 'name')
        if not request.user.is_superuser:
            group = get_user_group(request.user)
            if topic_modelling not in group.topic_modelling_names.split(","):
                return Response(
                    {"status": 403}
                )
            criterions = criterions.filter(usergroup=group)
        criterions_dict = dict(
            (c['id'], c) for c in criterions
        )
        criterions_result = []
        for index in eval_indices:
            index = parse_eval_index_name(index)
            if index['ignore']:
                continue
            criterion = deepcopy(criterions_dict[index['criterion_id']])
            criterion['id'] = index['critetion_id+postfix']
            if index['postfix']:
                criterion['name'] = criterion['name'] + ("_" + index['postfix'] if index['postfix'] else "")
            criterions_result.append(criterion)

        return Response(
            {
                "status": 200,
                "criterions": sorted(criterions_result, key=lambda x: x['id']),
                "my_groups": sorted(my_groups, key=lambda x: x['id']),
                "public_groups": sorted(public_groups, key=lambda x: x['id']),
            }
        )
