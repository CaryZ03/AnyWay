<script setup lang="ts">
import type { KnowledgeBase } from '@/types/knowledge-base'

const props = defineProps<{
  knowledgeBase: KnowledgeBase
  index?: number
}>()

const emit = defineEmits<{
  (e: 'view', kb: KnowledgeBase): void
  (e: 'edit', kb: KnowledgeBase): void
  (e: 'delete', kb: KnowledgeBase): void
}>()

const getIcon = (index: number) => {
  const icons = ['📚', '🧠', '📖', '🗂️', '📝', '📦', '📂', '🔎']
  return icons[index % icons.length]
}

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric'
  })
}

const handleView = () => emit('view', props.knowledgeBase)
const handleEdit = (e: Event) => {
  e.stopPropagation()
  emit('edit', props.knowledgeBase)
}
const handleDelete = (e: Event) => {
  e.stopPropagation()
  if (confirm(`确定要删除知识库 "${props.knowledgeBase.name}" 吗？`)) {
    emit('delete', props.knowledgeBase)
  }
}
</script>

<template>
  <div class="kb-card" @click="handleView">
    <div class="card-header">
      <div class="card-icon">{{ getIcon(index || 0) }}</div>
      <div class="card-actions">
        <button class="action-btn" @click="handleEdit" title="编辑">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M11.333 2a1.414 1.414 0 0 1 2 2L4.667 13l-3.334 1L2.333 10.667L11.333 2Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="action-btn delete-btn" @click="handleDelete" title="删除">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M2 4h12M5.333 4V2.667A1.333 1.333 0 0 1 6.667 1.333h2.666A1.333 1.333 0 0 1 10.667 2.667V4m2 0v9.333A1.333 1.333 0 0 1 11.333 14.667H4.667A1.333 1.333 0 0 1 3.333 13.333V4h9.334Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ knowledgeBase.name }}</h3>
      <p class="card-description">{{ knowledgeBase.description || '暂无描述' }}</p>
      <div class="card-meta">
        <span class="meta-item">{{ knowledgeBase.documentCount || 0 }} 个文档</span>
        <span class="meta-item">模型：{{ knowledgeBase.embeddingModel }}</span>
      </div>
    </div>
    <div class="card-footer">
      <span class="card-time">创建于 {{ formatDate(knowledgeBase.createdAt) }}</span>
      <button class="view-btn" @click.stop="handleView">管理文档</button>
    </div>
  </div>
</template>

<style scoped>
.kb-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.kb-card:hover {
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #e0f2fe 0%, #bfdbfe 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.card-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.kb-card:hover .card-actions {
  opacity: 1;
}

.action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.action-btn.delete-btn:hover {
  background: #fee2e2;
  color: #dc2626;
}

.card-body {
  flex: 1;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.card-description {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
  margin: 0 0 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  color: #6b7280;
  font-size: 12px;
}

.meta-item {
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 6px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.card-time {
  font-size: 12px;
  color: #9ca3af;
}

.view-btn {
  padding: 6px 12px;
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn:hover {
  background: #1d4ed8;
}
</style>
