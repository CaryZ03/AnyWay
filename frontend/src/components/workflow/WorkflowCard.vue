<script setup lang="ts">
import type { WorkflowForm } from '@/types/workflow'

interface Props {
  workflow: WorkflowForm
  index: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [workflow: WorkflowForm]
  edit: [workflow: WorkflowForm]
  delete: [workflow: WorkflowForm]
}>()

const handleClick = () => {
  emit('click', props.workflow)
}

const handleEdit = (e: Event) => {
  e.stopPropagation()
  emit('edit', props.workflow)
}

const handleDelete = (e: Event) => {
  e.stopPropagation()
  if (confirm('确定要删除这个工作流吗？')) {
    emit('delete', props.workflow)
  }
}

const getStatusLabel = (status?: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    active: '已启用',
  }
  return statusMap[status || 'draft'] || '未知'
}

const getStatusClass = (status?: string) => {
  return status === 'active' ? 'status-active' : 'status-draft'
}
</script>

<template>
  <div class="workflow-card" @click="handleClick">
    <div class="card-header">
      <div class="card-title-section">
        <h3 class="card-title">{{ workflow.name }}</h3>
        <span :class="['status-badge', getStatusClass(workflow.status)]">
          {{ getStatusLabel(workflow.status) }}
        </span>
      </div>
      <div class="card-actions">
        <button class="action-btn edit-btn" @click="handleEdit" title="编辑">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 12h4M9.5 2.5l4 4L5.5 14.5H2v-3.5L9.5 2.5z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="action-btn delete-btn" @click="handleDelete" title="删除">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M2 4h12M6 4V2.667A1.333 1.333 0 0 1 7.333 2h1.334A1.333 1.333 0 0 1 10 2.667V4m2 0v9.333A1.333 1.333 0 0 1 10.667 14.667H5.333A1.333 1.333 0 0 1 4 13.333V4h8z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
    
    <p v-if="workflow.description" class="card-description">{{ workflow.description }}</p>
    
    <div class="card-footer">
      <div class="card-meta">
        <span class="meta-item">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M8 2v8M5 7l3-3 3 3M2 12h12" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          {{ workflow.nodes?.length || 0 }} 个节点
        </span>
        <span v-if="workflow.updatedAt || workflow.createdAt" class="meta-item">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M8 14A6 6 0 1 0 8 2a6 6 0 0 0 0 12zM8 5v3l2 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ new Date(workflow.updatedAt || workflow.createdAt || '').toLocaleDateString('zh-CN') }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workflow-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 12px;
}

.workflow-card:hover {
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.card-title-section {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.status-draft {
  background: #f3f4f6;
  color: #6b7280;
}

.status-badge.status-active {
  background: #d1fae5;
  color: #065f46;
}

.card-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #6b7280;
}

.action-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  color: #1f2937;
}

.action-btn.delete-btn:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
}

.card-description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #9ca3af;
}

.meta-item svg {
  flex-shrink: 0;
}
</style>

