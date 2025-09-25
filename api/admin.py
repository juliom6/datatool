from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import Cluster


class ClusterAdmin(admin.ModelAdmin):
    list_display = (
        "cluster_id",
        "cluster_name",
        "worker_node_type",
        "driver_node_type",
        "num_workers",
        "cluster_status",
        "python_script_url",
        "storage_name",
        "container_name",
        "create_from_image",
        "image_id",
    )
    readonly_fields = (
        "cluster_status",
        "message",
        "created_timestamp",
        "start_timestamp",
        "end_timestamp",
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 60, 'cols': 90})},
    }
    exclude = ("access_key",)
    ordering = ("-created_timestamp",)


admin.site.register(Cluster, ClusterAdmin)


admin.site.site_title = "Datatool"
admin.site.site_header = "Datatool administration"
# admin.site.index_title = "index_title YYY" # default "Site administration"
