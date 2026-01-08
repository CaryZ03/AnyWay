<script setup lang="ts">
import type { Agent } from '@/types/agent'

const props = defineProps<{
  agent: Agent
  index?: number
}>()

const emit = defineEmits<{
  (e: 'click', agent: Agent): void
  (e: 'edit', agent: Agent): void
  (e: 'delete', agent: Agent): void
}>()

const getAgentIcon = (index: number) => {
  const icons = ['🤖', '💡', '⚡', '🔮', '🎯', '🚀', '🌟', '✨']
  return icons[index % icons.length]
}

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric'
  })
}

const handleClick = () => {
  emit('click', props.agent)
}

const handleEdit = (e: Event) => {
  e.stopPropagation()
  emit('edit', props.agent)
}

const handleDelete = (e: Event) => {
  e.stopPropagation()
  if (confirm(`确定要删除智能体 "${props.agent.name}" 吗？`)) {
    emit('delete', props.agent)
  }
}
</script>

<template>
  <div class="agent-card" @click="handleClick">
    <div class="card-header">
      <div class="card-icon">{{ getAgentIcon(index || 0) }}</div>
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
      <h3 class="card-title">{{ agent.name }}</h3>
      <p class="card-description">{{ agent.description || '暂无描述' }}</p>
    </div>
    <div class="card-footer">
      <span class="status-badge" :class="agent.status">
        {{ agent.status === 'published' ? '已发布' : '草稿' }}
      </span>
      <span class="card-time">{{ formatDate(agent.updatedAt) }}</span>
    </div>
  </div>
</template>

<style scoped>
.agent-card {
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

.agent-card:hover {
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
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
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

.agent-card:hover .card-actions {
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
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.published {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.draft {
  background: #fef3c7;
  color: #92400e;
}

.card-time {
  font-size: 12px;
  color: #9ca3af;
}
</style>
