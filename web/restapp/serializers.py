from rest_framework import serializers
from mainapp.models import *


class TopicIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicID
        fields = '__all__'


class TopicGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicGroup
        exclude = ('owner',)

    topics = TopicIDSerializer(read_only=True, many=True)
