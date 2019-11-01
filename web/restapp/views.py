from mainapp.models import *
from annoying.functions import get_object_or_None
from .serializers import *
from rest_framework import viewsets
from rest_framework.response import Response


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
        topic_groups = TopicGroup.objects.filter(topic_modelling_name=topic_modelling_name)
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
