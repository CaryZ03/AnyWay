"""
LLM服务路由配置
"""
from django.urls import path
from .views import ChatView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='llm-chat'),
]
