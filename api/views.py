from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView

from .models import Cluster
from .serializers import ClusterSerializer

from crontab import CronTab


class CreateCluster(CreateAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        self.schedule_job_cluster(instance)

    def schedule_job_cluster(self, instance):
        cron = CronTab(user=True)
        job = cron.new(command=f'./git/datatool/run_env.sh {str(instance.cluster_id)} >> ./cron.log 2>&1')
        job.setall(instance.trigger_at)
        cron.write()
        print(str(instance.cluster_id))


class ListCluster(ListAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class DetailCluster(RetrieveAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class DeleteCluster(DestroyAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
