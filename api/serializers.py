from rest_framework import serializers

from .models import Cluster

class MaskedAccessKeyField(serializers.CharField):
    def to_representation(self, value):
        return "__SECRET__"

class ClusterSerializer(serializers.ModelSerializer):
    access_key = MaskedAccessKeyField()

    class Meta:
        model = Cluster
        fields = (
            "cluster_id",
            "cluster_name",
            "worker_node_type",
            "driver_node_type",
            "num_workers",
            "cluster_status",
            "python_script_url",
            "storage_name",
            "container_name",
            "access_key",
            "delete_after_execution",
            "create_from_image",
            "image_id",
            "created_timestamp",
            "start_timestamp",
            "end_timestamp",
            "message",
        )
