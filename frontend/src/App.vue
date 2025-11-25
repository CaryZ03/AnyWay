<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { agentApi, workflowApi, knowledgeApi, pluginApi } from '@/api'
import type { Agent } from '@/types/agent'
import type { Workflow } from '@/types/workflow'
import type { KnowledgeBase } from '@/types/knowledge-base'
import type { Plugin } from '@/types/plugin'

// 数据状态
const agents = ref<Agent[]>([])
const workflows = ref<Workflow[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const plugins = ref<Plugin[]>([])

// 加载状态
const loading = ref({
  agents: false,
  workflows: false,
  knowledgeBases: false,
  plugins: false,
})

// 错误信息
const errors = ref({
  agents: '',
  workflows: '',
  knowledgeBases: '',
  plugins: '',
})

// 获取智能体列表
const fetchAgents = async () => {
  loading.value.agents = true
  errors.value.agents = ''
  try {
    agents.value = await agentApi.getList()
  } catch (error) {
    // request.ts 已经统一处理了错误格式，这里直接使用 error.message
    errors.value.agents = error instanceof Error ? error.message : '获取智能体列表失败'
  } finally {
    loading.value.agents = false
  }
}

// 获取工作流列表
const fetchWorkflows = async () => {
  loading.value.workflows = true
  errors.value.workflows = ''
  try {
    workflows.value = await workflowApi.getList()
  } catch (error) {
    errors.value.workflows = error instanceof Error ? error.message : '获取工作流列表失败'
  } finally {
    loading.value.workflows = false
  }
}

// 获取知识库列表
const fetchKnowledgeBases = async () => {
  loading.value.knowledgeBases = true
  errors.value.knowledgeBases = ''
  try {
    knowledgeBases.value = await knowledgeApi.getList()
  } catch (error) {
    errors.value.knowledgeBases = error instanceof Error ? error.message : '获取知识库列表失败'
  } finally {
    loading.value.knowledgeBases = false
  }
}

// 获取插件列表
const fetchPlugins = async () => {
  loading.value.plugins = true
  errors.value.plugins = ''
  try {
    plugins.value = await pluginApi.getList()
  } catch (error) {
    errors.value.plugins = error instanceof Error ? error.message : '获取插件列表失败'
  } finally {
    loading.value.plugins = false
  }
}

// 刷新所有数据
const refreshAll = async () => {
  await Promise.all([
    fetchAgents(),
    fetchWorkflows(),
    fetchKnowledgeBases(),
    fetchPlugins(),
  ])
}

// 组件挂载时获取数据
onMounted(() => {
  refreshAll()
})
</script>

<template>
  <div class="app-container">
    <header class="header">
      <h1>AnyWay AI Agent Platform</h1>
      <button @click="refreshAll" class="refresh-btn">刷新数据</button>
    </header>

    <div class="content">
      <!-- 智能体列表 -->
      <section class="section">
        <h2>智能体 (Agents)</h2>
        <div v-if="loading.agents" class="loading">加载中...</div>
        <div v-else-if="errors.agents" class="error">{{ errors.agents }}</div>
        <div v-else-if="agents.length === 0" class="empty">暂无数据</div>
        <div v-else class="card-list">
          <div v-for="agent in agents" :key="agent.id" class="card">
            <h3>{{ agent.name }}</h3>
            <p class="description">{{ agent.description || '无描述' }}</p>
            <div class="meta">
              <span class="badge" :class="agent.status">{{ agent.status === 'published' ? '已发布' : '草稿' }}</span>
              <span class="info">ID: {{ agent.id }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 工作流列表 -->
      <section class="section">
        <h2>工作流 (Workflows)</h2>
        <div v-if="loading.workflows" class="loading">加载中...</div>
        <div v-else-if="errors.workflows" class="error">{{ errors.workflows }}</div>
        <div v-else-if="workflows.length === 0" class="empty">暂无数据</div>
        <div v-else class="card-list">
          <div v-for="workflow in workflows" :key="workflow.id" class="card">
            <h3>{{ workflow.name }}</h3>
            <p class="description">{{ workflow.description || '无描述' }}</p>
            <div class="meta">
              <span class="info">节点数: {{ Array.isArray(workflow.nodes) ? workflow.nodes.length : 0 }}</span>
              <span class="info">边数: {{ Array.isArray(workflow.edges) ? workflow.edges.length : 0 }}</span>
              <span class="info">ID: {{ workflow.id }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 知识库列表 -->
      <section class="section">
        <h2>知识库 (Knowledge Bases)</h2>
        <div v-if="loading.knowledgeBases" class="loading">加载中...</div>
        <div v-else-if="errors.knowledgeBases" class="error">{{ errors.knowledgeBases }}</div>
        <div v-else-if="knowledgeBases.length === 0" class="empty">暂无数据</div>
        <div v-else class="card-list">
          <div v-for="kb in knowledgeBases" :key="kb.id" class="card">
            <h3>{{ kb.name }}</h3>
            <p class="description">{{ kb.description || '无描述' }}</p>
            <div class="meta">
              <span class="info">向量数据库: {{ kb.vectorDbType }}</span>
              <span class="info">分块大小: {{ kb.chunkSize }}</span>
              <span class="info">ID: {{ kb.id }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 插件列表 -->
      <section class="section">
        <h2>插件 (Plugins)</h2>
        <div v-if="loading.plugins" class="loading">加载中...</div>
        <div v-else-if="errors.plugins" class="error">{{ errors.plugins }}</div>
        <div v-else-if="plugins.length === 0" class="empty">暂无数据</div>
        <div v-else class="card-list">
          <div v-for="plugin in plugins" :key="plugin.id" class="card">
            <h3>{{ plugin.name }}</h3>
            <p class="description">{{ plugin.description || '无描述' }}</p>
            <div class="meta">
              <span class="badge" :class="plugin.status">{{ plugin.status === 'enabled' ? '已启用' : '已禁用' }}</span>
              <span class="info">类型: {{ plugin.type }}</span>
              <span class="info">ID: {{ plugin.id }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #646cff;
}

.header h1 {
  margin: 0;
  font-size: 2rem;
  color: #646cff;
}

.refresh-btn {
  padding: 0.5rem 1rem;
  background-color: #646cff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.refresh-btn:hover {
  background-color: #535bf2;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 1.5rem;
}

.section h2 {
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
  color: #646cff;
}

.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(100, 108, 255, 0.3);
}

.card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: #fff;
}

.description {
  margin: 0.5rem 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  line-height: 1.4;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.badge.published,
.badge.enabled {
  background-color: #4caf50;
  color: white;
}

.badge.draft,
.badge.disabled {
  background-color: #ff9800;
  color: white;
}

.info {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.loading,
.error,
.empty {
  padding: 2rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
}

.error {
  color: #ff6b6b;
}

@media (prefers-color-scheme: light) {
  .section {
    background: rgba(0, 0, 0, 0.02);
  }

  .card {
    background: rgba(0, 0, 0, 0.03);
    border-color: rgba(0, 0, 0, 0.1);
  }

  .card h3 {
    color: #213547;
  }

  .description {
    color: rgba(0, 0, 0, 0.7);
  }

  .meta {
    border-top-color: rgba(0, 0, 0, 0.1);
  }

  .info {
    color: rgba(0, 0, 0, 0.6);
  }

  .loading,
  .error,
  .empty {
    color: rgba(0, 0, 0, 0.7);
  }
}
</style>
