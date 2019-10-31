from rest_framework import viewsets
from rest_framework.response import Response


class TestViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response([{"ansha": "abdul"}])

    def retrieve(self, request, pk=None):
        return Response({"bibo": "ran"})
