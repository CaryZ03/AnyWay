"""
知识库路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KnowledgeBaseViewSet

router = DefaultRouter()
router.register(r'', KnowledgeBaseViewSet, basename='knowledge')

urlpatterns = [
    path('', include(router.urls)),
]
