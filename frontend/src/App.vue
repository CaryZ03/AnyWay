<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { agentApi } from '@/api'
import type { Agent } from '@/types/agent'

// 数据状态
const agents = ref<Agent[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedStatus = ref('all')

// 获取智能体列表
const fetchAgents = async () => {
  loading.value = true
  try {
    const data = await agentApi.getList()
    agents.value = data
  } catch (error) {
    console.error('获取智能体列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 过滤智能体
const filteredAgents = ref<Agent[]>([])
const updateFilteredAgents = () => {
  let result = agents.value
  
  // 按状态过滤
  if (selectedStatus.value !== 'all') {
    result = result.filter(agent => agent.status === selectedStatus.value)
  }
  
  // 按搜索关键词过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(agent => 
      agent.name.toLowerCase().includes(query) ||
      (agent.description && agent.description.toLowerCase().includes(query))
    )
  }
  
  filteredAgents.value = result
}

// 监听数据变化
const updateData = () => {
  updateFilteredAgents()
}

// 格式化时间
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取智能体图标
const getAgentIcon = (index: number) => {
  const icons = ['📚', '🗣️', '🍳', '👤']
  return icons[index % icons.length]
}

// 获取卡片颜色
const getCardColor = (index: number) => {
  const colors = ['#f5f5f5', '#fff3e0', '#e3f2fd', '#f3e5f5']
  return colors[index % colors.length]
}

// 组件挂载时获取数据
onMounted(async () => {
  await fetchAgents()
  updateFilteredAgents()
})
</script>

<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="header">
      <h1 class="title">项目开发</h1>
      <div class="header-actions">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            @input="updateData"
            type="text" 
            placeholder="搜索项目"
            class="search-input"
          />
        </div>
        <button class="btn-secondary">+ 文件夹</button>
        <button class="btn-primary">+ 项目</button>
      </div>
    </header>

    <!-- 过滤器 -->
    <div class="filters">
      <div class="filter-section">
        <label>项目</label>
        <select v-model="selectedStatus" @change="updateData" class="filter-select">
          <option value="all">全部</option>
          <option value="published">已发布</option>
          <option value="draft">草稿</option>
        </select>
      </div>
    </div>

    <!-- 智能体列表 -->
    <div class="agents-grid">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="filteredAgents.length === 0" class="empty-state">
        <p>暂无智能体</p>
      </div>
      
      <div 
        v-else
        v-for="(agent, index) in filteredAgents" 
        :key="agent.id" 
        class="agent-card"
      >
        <div class="card-icon" :style="{ backgroundColor: getCardColor(index) }">
          {{ getAgentIcon(index) }}
        </div>
        <div class="card-content">
          <h3 class="card-title">{{ agent.name }}</h3>
          <p class="card-description">{{ agent.description || '暂无描述' }}</p>
          <div class="card-footer">
            <span class="badge" :class="agent.status">
              {{ agent.status === 'published' ? '智能体' : '智能体' }}
            </span>
            <div class="card-meta">
              <span class="meta-user">👤 RootUser_{{ agent.id }}</span>
              <span class="meta-time">最近编辑 {{ formatDate(agent.updatedAt) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.app-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 0;
  margin: 0;
}

/* 顶部导航栏 */
.header {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.search-box {
  position: relative;
}

.search-input {
  padding: 0.5rem 1rem;
  padding-left: 2.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  width: 240px;
  background: white;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.search-input::placeholder {
  color: #9ca3af;
}

.btn-primary, .btn-secondary {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #6366f1;
  color: white;
}

.btn-primary:hover {
  background: #4f46e5;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
}

/* 过滤器 */
.filters {
  background: white;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-section label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.filter-select {
  padding: 0.375rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #6366f1;
}

/* 智能体网格 */
.agents-grid {
  padding: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

/* 加载和空状态 */
.loading-state, .empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 智能体卡片 */
.agent-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  gap: 1rem;
}

.agent-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  flex-shrink: 0;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-title {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-description {
  margin: 0 0 1rem 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-footer {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  background: #eff6ff;
  color: #1d4ed8;
  width: fit-content;
}

.badge.published {
  background: #dcfce7;
  color: #166534;
}

.badge.draft {
  background: #fef3c7;
  color: #92400e;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #9ca3af;
}

.meta-user, .meta-time {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* 响应式 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-actions {
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 100%;
  }
  
  .agents-grid {
    grid-template-columns: 1fr;
    padding: 1rem;
  }
}
</style>
