from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView

from .models import Cluster
from .serializers import ClusterSerializer


class CreateCluster(CreateAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class ListCluster(ListAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class DetailCluster(RetrieveAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class DeleteCluster(DestroyAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
