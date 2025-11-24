"""
工作流后台管理
"""
from django.contrib import admin
from .models import Workflow, WorkflowExecution


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    list_display = ['id', 'workflow', 'status', 'started_at', 'completed_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
