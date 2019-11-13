import json
import datetime

from annoying.functions import get_object_or_None
from django.db.utils import IntegrityError
from elasticsearch_dsl import Search
from rest_framework import viewsets
from rest_framework.response import Response

from evaluation.models import EvalCriterion, TopicsEval, TopicIDEval
from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT, ES_INDEX_TOPIC_DOCUMENT
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
                                      is_public=request.user.is_superuser
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
        topics_evals = TopicsEval.objects.filter(topicideval__in=topic_id_evals, author=request.user)
        criterions = EvalCriterion.objects.filter(topicseval__in=topics_evals)

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
    def list(self, request):
        topic_modelling = request.GET['topic_modelling']
        topics = json.loads(request.GET['topics'])
        date_from = datetime.datetime.strptime(request.GET['date_from'][:10], "%Y-%m-%d")
        date_to = datetime.datetime.strptime(request.GET['date_to'][:10], "%Y-%m-%d")

        std = Search(using=ES_CLIENT, index=ES_INDEX_TOPIC_DOCUMENT) \
                  .filter("term", topic_modelling=topic_modelling) \
                  .filter("terms", topic_id=topics).sort("-topic_weight") \
                  .filter("range", topic_weight={"gte": 0.001}) \
                  .filter("range", datetime={"gte": date_from}) \
                  .filter("range", datetime={"lte": date_to}) \
                  .source(['document_es_id', 'topic_weight'])[:100]
        std.aggs.bucket(name="source", agg_type="terms", field="document_source.keyword") \
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

        return Response(
            {
                "status": 200,
                "documents": [
                    {
                        "id": document.id,
                        "title": document.title,
                        "source": document.source,
                        "datetime": document.datetime,
                    } for document in documents
                ],
                "source_weights": [
                    {
                        "source": bucket.key,
                        "weight": bucket.source_weight.value,
                    } for bucket in topic_documents.aggregations.source.buckets
                ]
            }
        )
