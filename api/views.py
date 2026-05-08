from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView

from .models import Cluster
from .serializers import ClusterSerializer


class CreateCluster(CreateAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer

    def perform_create(self, serializer):
    	instance = serializer.save()
    	self.schedule_job_cluster(instance)
    	
    def schedule_job_cluster(self, instance):
    	print(instance.cluster_id)


class ListCluster(ListAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class DetailCluster(RetrieveAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class DeleteCluster(DestroyAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
