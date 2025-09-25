from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import CreateCluster, ListCluster, DetailCluster, DeleteCluster


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("clusters/create/", CreateCluster.as_view(), name="cluster_create"),
    path("clusters/<str:pk>/", DetailCluster.as_view(), name="cluster_detail"),
    path("clusters/", ListCluster.as_view(), name="cluster_list"),
    path("clusters/<str:pk>/", DetailCluster.as_view(), name="cluster_detail"),
    path("clusters/<str:pk>/delete/", DeleteCluster.as_view(), name='cluster_delete'),
]
