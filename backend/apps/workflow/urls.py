"""
工作流路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import WorkflowViewSet

router = DefaultRouter()
router.register(r"", WorkflowViewSet, basename="workflow")

urlpatterns = [
    path("", include(router.urls)),
]


