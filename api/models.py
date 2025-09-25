from django.db import models
import uuid


NODE_TYPE_CHOICES = (
    ('Standard_DS1_v2','Standard_DS1_v2'),
    ('Standard_DS3_v2','Standard_DS3_v2'),
    ('Standard_DS4_v2','Standard_DS4_v2'),
    ('Standard_DS5_v2','Standard_DS5_v2'),
    ('Standard_D3_v2','Standard_D3_v2'),
)


class Cluster(models.Model):
    cluster_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, serialize=True, null=False
    )
    cluster_name = models.CharField(max_length=200, default="my-cluster-name")
    worker_node_type = models.CharField(max_length=50, choices=NODE_TYPE_CHOICES, default='Standard_DS3_v2', verbose_name="Worker type")
    driver_node_type = models.CharField(max_length=50, choices=NODE_TYPE_CHOICES, default='Standard_DS3_v2', verbose_name="Driver type")
    num_workers = models.PositiveSmallIntegerField(default=1, verbose_name="Num. of workers")
    cluster_status = models.PositiveSmallIntegerField(
        default=0
    )  # 0: to be created, 1: being_created, 2: creation_completed
    python_script_url = models.CharField(max_length=5000)
    storage_name = models.CharField(max_length=200)
    container_name = models.CharField(max_length=200)
    access_key = models.CharField(max_length=200)
    delete_after_execution = models.BooleanField(default=True, verbose_name="Delete after execution?")
    ip = models.CharField(max_length=15, default="", blank=True, null=True)
    uri_master = models.CharField(max_length=150, default="", blank=True, null=True)
    create_from_image = models.BooleanField(default=False, verbose_name="Create from image?")
    image_id = models.CharField(max_length=250, default="")
    created_timestamp = models.DateTimeField(auto_now_add=True)
    start_timestamp = models.DateTimeField(null=True)
    end_timestamp = models.DateTimeField(null=True)
    message = models.TextField(default="")

    def __str__(self):
        return str(self.cluster_name)
