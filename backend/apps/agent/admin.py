"""
智能体后台管理
"""
from django.contrib import admin
from .models import Agent, Conversation


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'agent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user_message', 'assistant_message']
    readonly_fields = ['created_at']
