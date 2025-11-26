<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { agentApi } from '@/api'
import type { Agent } from '@/types/agent'
import CreateAgentDialog from '@/components/CreateAgentDialog.vue'
import AgentChat from '@/components/AgentChat.vue'

// 视图状态
const currentView = ref<'list' | 'chat'>('list')
const selectedAgentId = ref<number | null>(null)

// 数据状态
const agents = ref<Agent[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedStatus = ref('all')
const showCreateDialog = ref(false)

// 获取智能体列表
const fetchAgents = async () => {
  loading.value = true
  try {
    const data = await agentApi.getList()
    agents.value = data
    updateFilteredAgents()
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
const formatDate = (dateString: string | undefined) => {
  if (!dateString) return '未知时间'
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
  const icons = ['📚', '🗣️', '🍳', '👤', '🤖', '💡', '⚡', '🔥']
  return icons[index % icons.length]
}

// 获取卡片颜色
const getCardColor = (index: number) => {
  const colors = ['#fff5f5', '#ffe0e6', '#fff0f3', '#ffeaef']
  return colors[index % colors.length]
}

// 打开创建对话框
const openCreateDialog = () => {
  showCreateDialog.value = true
}

// 关闭创建对话框
const closeCreateDialog = () => {
  showCreateDialog.value = false
}

// 创建成功后刷新列表
const handleCreateSuccess = () => {
  fetchAgents()
}

// 点击智能体卡片
const handleAgentClick = (agent: Agent) => {
  if (agent.id) {
    selectedAgentId.value = agent.id
    currentView.value = 'chat'
  }
}

// 返回列表
const handleBackToList = () => {
  currentView.value = 'list'
  selectedAgentId.value = null
}

// 显示提示
const showAlert = (message: string) => {
  window.alert(message)
}

// 组件挂载时获取数据
onMounted(async () => {
  await fetchAgents()
  updateFilteredAgents()
})
</script>

<template>
  <!-- 列表视图 -->
  <div v-if="currentView === 'list'" class="app-container">
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
        <button class="btn-secondary" @click="showAlert('文件夹功能开发中...')">+ 文件夹</button>
        <button class="btn-primary" @click="openCreateDialog">+ 项目</button>
      </div>
    </header>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <div class="filter-item">
        <label>项目</label>
        <select v-model="selectedStatus" @change="updateData" class="filter-select">
          <option value="all">全部</option>
          <option value="draft">草稿</option>
          <option value="published">已发布</option>
        </select>
      </div>
    </div>

    <!-- 智能体卡片列表 -->
    <div class="cards-container">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="filteredAgents.length === 0" class="empty-state">
        <div class="empty-icon">📦</div>
        <p>暂无智能体</p>
        <button class="btn-primary" @click="openCreateDialog">创建第一个智能体</button>
      </div>
      <div v-else class="cards-grid">
        <div
          v-for="(agent, index) in filteredAgents"
          :key="agent.id"
          class="card"
          :style="{ backgroundColor: getCardColor(index) }"
          @click="handleAgentClick(agent)"
        >
          <div class="card-icon">{{ getAgentIcon(index) }}</div>
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

    <!-- 创建智能体对话框 -->
    <CreateAgentDialog 
      :show="showCreateDialog"
      @close="closeCreateDialog"
      @success="handleCreateSuccess"
    />
  </div>

  <!-- 对话视图 -->
  <AgentChat 
    v-else-if="currentView === 'chat' && selectedAgentId"
    :agent-id="selectedAgentId"
    @back="handleBackToList"
  />
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #fef5f5 0%, #fff 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.header {
  background: white;
  padding: 24px 48px;
  box-shadow: 0 2px 8px rgba(196, 30, 58, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  background: linear-gradient(135deg, #c41e3a 0%, #8b1528 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-box {
  position: relative;
}

.search-input {
  padding: 10px 16px;
  border: 2px solid #ffe0e6;
  border-radius: 8px;
  font-size: 14px;
  width: 280px;
  transition: all 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #c41e3a;
  box-shadow: 0 0 0 3px rgba(196, 30, 58, 0.1);
}

.btn-secondary {
  padding: 10px 20px;
  border: 2px solid #c41e3a;
  background: white;
  color: #c41e3a;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: #fff5f5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.15);
}

.btn-primary {
  padding: 10px 20px;
  border: none;
  background: linear-gradient(135deg, #c41e3a 0%, #a01830 100%);
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.2);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(196, 30, 58, 0.3);
}

.filter-section {
  padding: 24px 48px;
  background: white;
  border-bottom: 1px solid #ffe0e6;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-item label {
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.filter-select {
  padding: 8px 16px;
  border: 2px solid #ffe0e6;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.filter-select:focus {
  outline: none;
  border-color: #c41e3a;
}

.cards-container {
  padding: 32px 48px;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  font-size: 16px;
  color: #c41e3a;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 16px;
  color: #666;
  margin-bottom: 24px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  cursor: pointer;
  border: 2px solid transparent;
  position: relative;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #c41e3a 0%, #8b1528 100%);
  transform: scaleX(0);
  transition: transform 0.3s;
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(196, 30, 58, 0.15);
  border-color: #c41e3a;
}

.card:hover::before {
  transform: scaleX(1);
}

.card-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #c41e3a 0%, #a01830 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.2);
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.card-description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  width: fit-content;
}

.badge.published {
  background: linear-gradient(135deg, #c41e3a 0%, #a01830 100%);
  color: white;
}

.badge.draft {
  background: #ffe0e6;
  color: #c41e3a;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

.meta-user,
.meta-time {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
