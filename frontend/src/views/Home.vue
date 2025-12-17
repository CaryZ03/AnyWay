<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { agentApi, pluginApi, workflowApi, knowledgeApi } from '@/api'
import type { Agent } from '@/types/agent'
import type { Plugin } from '@/types/plugin'
import type { WorkflowForm } from '@/types/workflow'
import type { KnowledgeBase } from '@/types/knowledge-base'
import Sidebar, { type SidebarItem } from '@/components/common/Sidebar.vue'
import ContentList from '@/components/common/ContentList.vue'
import AgentCard from '@/components/agent/AgentCard.vue'
import PluginCard from '@/components/plugin/PluginCard.vue'
import WorkflowCard from '@/components/workflow/WorkflowCard.vue'
import KnowledgeCard from '@/components/knowledge/KnowledgeCard.vue'
import KnowledgeDialog from '@/components/knowledge/KnowledgeDialog.vue'
import AgentEditorDialog from '@/components/agent/AgentEditorDialog.vue'
import CreateAgentDialog from '@/components/agent/AgentCreateDialog.vue'
import PluginEditDialog from '@/components/plugin/PluginEditDialog.vue'

const router = useRouter()
const route = useRoute()

// 侧边栏状态
const activeSidebarItem = ref<SidebarItem>('agent')

// 调试：监听侧边栏切换
watch(activeSidebarItem, (newValue) => {
  console.log('侧边栏切换到:', newValue)
  if (newValue === 'workflow') {
    console.log('切换到工作流，准备加载数据...')
  }
})

// 数据状态
const agents = ref<Agent[]>([])
const plugins = ref<Plugin[]>([])
const workflows = ref<WorkflowForm[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedStatus = ref('all')
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const editingAgent = ref<Agent | undefined>()
const showPluginDialog = ref(false)
const editingPlugin = ref<Plugin | null>(null)
const showKnowledgeDialog = ref(false)
const editingKB = ref<KnowledgeBase | null>(null)

// 过滤后的列表（仅智能体）
const filteredAgents = computed(() => {
  let result = agents.value

  // 按状态过滤（仅对智能体有效）
  if (selectedStatus.value !== 'all') {
    result = result.filter((item) => item.status === selectedStatus.value)
  }

  // 按搜索关键词过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter((item) =>
      item.name.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query))
    )
  }

  return result
})

// 过滤后的插件列表
const filteredPlugins = computed(() => {
  let result = plugins.value

  // 按搜索关键词过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter((item) =>
      item.name.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query))
    )
  }

  return result
})

// 过滤后的工作流列表
const filteredWorkflows = computed(() => {
  let result = workflows.value

  // 按搜索关键词过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter((item) =>
      item.name.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query))
    )
  }

  return result
})

// 过滤后的知识库列表
const filteredKnowledgeBases = computed(() => {
  let result = knowledgeBases.value

  // 按搜索关键词过滤
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter((item) =>
      item.name.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query))
    )
  }

  return result
})


// 获取标题和按钮文字
const pageTitle = computed(() => {
  const titles: Record<SidebarItem, string> = {
    agent: '智能体',
    plugin: '插件',
    knowledge: '知识库',
    workflow: '工作流'
  }
  return titles[activeSidebarItem.value]
})

const createButtonText = computed(() => {
  const texts: Record<SidebarItem, string> = {
    agent: '新建智能体',
    plugin: '新建插件',
    knowledge: '新建知识库',
    workflow: '新建工作流'
  }
  return texts[activeSidebarItem.value]
})

// 获取智能体列表
const fetchAgents = async () => {
  try {
    const data = await agentApi.getList()
    agents.value = data
  } catch (error) {
    console.error('获取智能体列表失败:', error)
    alert('获取智能体列表失败: ' + (error instanceof Error ? error.message : String(error)))
  }
}

// 获取插件列表
const fetchPlugins = async () => {
  try {
    const data = await pluginApi.getList()
    plugins.value = data
  } catch (error) {
    console.error('获取插件列表失败:', error)
  }
}

// 获取工作流列表
const fetchWorkflows = async () => {
  try {
    const data = await workflowApi.getList()
    console.log('获取到的工作流数据:', data)
    workflows.value = data || []
    console.log('工作流列表已更新，数量:', workflows.value.length)
  } catch (error) {
    console.error('获取工作流列表失败:', error)
    alert('获取工作流列表失败: ' + (error instanceof Error ? error.message : String(error)))
    workflows.value = []
  }
}

// 获取知识库列表
const fetchKnowledgeBases = async () => {
  try {
    console.log('[知识库] 开始获取知识库列表...')
    const data = await knowledgeApi.getList()
    console.log('[知识库] 获取到的数据:', data)
    knowledgeBases.value = Array.isArray(data) ? data : []
    console.log('[知识库] 列表已更新，数量:', knowledgeBases.value.length)
  } catch (error) {
    console.error('[知识库] 获取知识库列表失败:', error)
    alert('获取知识库列表失败: ' + (error instanceof Error ? error.message : String(error)))
    knowledgeBases.value = []
  }
}

// 加载当前项的数据
const fetchCurrentData = async () => {
  loading.value = true
  try {
    switch (activeSidebarItem.value) {
      case 'agent':
        await fetchAgents()
        break
      case 'plugin':
        await fetchPlugins()
        break
      case 'workflow':
        await fetchWorkflows()
        break
      case 'knowledge':
        await fetchKnowledgeBases()
        break
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 侧边栏切换
const handleSidebarChange = (item: SidebarItem) => {
  console.log('侧边栏切换:', item)

  // 如果是智能体、插件、工作流或知识库，确保在首页
  if (item === 'agent' || item === 'plugin' || item === 'workflow' || item === 'knowledge') {
    // 如果当前不在首页，先跳转到首页
    if (route.path !== '/') {
      router.push('/')
      // 等待路由切换完成后再更新状态
      nextTick(() => {
        activeSidebarItem.value = item
        selectedStatus.value = 'all'
        searchQuery.value = ''
        console.log('路由切换后，准备加载数据，当前项:', item)
        fetchCurrentData()
      })
      return
    }
    
    // 如果已经在首页，直接切换
    activeSidebarItem.value = item
    selectedStatus.value = 'all'
    searchQuery.value = ''
    console.log('切换侧边栏到:', item, '准备加载数据')
    fetchCurrentData()
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  if (activeSidebarItem.value === 'plugin') {
    openCreatePluginDialog()
    return
  }
  if (activeSidebarItem.value === 'workflow') {
    handleCreateWorkflow()
    return
  }
  if (activeSidebarItem.value === 'knowledge') {
    handleCreateKnowledgeBase()
    return
  }
  showCreateDialog.value = true
}

// 关闭创建对话框
const closeCreateDialog = () => {
  showCreateDialog.value = false
}

// 创建成功后刷新列表
const handleCreateSuccess = () => {
  fetchCurrentData()
}

// 点击智能体卡片 - 跳转到编辑页面
const handleAgentClick = (agent: Agent) => {
  if (agent.id) {
    router.push(`/agent/${agent.id}/edit`)
  }
}

// 点击编辑按钮 - 打开编辑对话框
const handleAgentEdit = (agent: Agent) => {
  editingAgent.value = agent
  showEditDialog.value = true
}

// 关闭编辑对话框
const closeEditDialog = () => {
  showEditDialog.value = false
  editingAgent.value = undefined
}

// 保存编辑
const handleEditSave = async (data: Partial<Agent>) => {
  if (editingAgent.value?.id) {
    try {
      // 转换 Agent 格式到 AgentForm 格式
      const formData: Partial<import('@/types/agent').AgentForm> = {
        name: data.name,
        description: data.description,
        systemPrompt: data.systemPrompt,
        userPromptTemplate: data.userPromptTemplate,
        modelConfig: typeof data.modelConfig === 'string'
          ? JSON.parse(data.modelConfig)
          : data.modelConfig,
        workflowId: data.workflowId,
        knowledgeBaseIds: Array.isArray(data.knowledgeBaseIds)
          ? data.knowledgeBaseIds
          : typeof data.knowledgeBaseIds === 'string'
            ? JSON.parse(data.knowledgeBaseIds)
            : [],
        pluginIds: Array.isArray(data.pluginIds)
          ? data.pluginIds
          : typeof data.pluginIds === 'string'
            ? JSON.parse(data.pluginIds)
            : [],
        status: data.status
      }
      await agentApi.update(editingAgent.value.id, formData)
      await fetchCurrentData()
      closeEditDialog()
    } catch (error) {
      console.error('更新智能体失败:', error)
    }
  }
}

// 删除智能体
const handleAgentDelete = async (agent: Agent) => {
  if (!agent.id) return

  try {
    await agentApi.delete(agent.id)
    await fetchCurrentData()
    // 删除成功提示（可选，因为列表会自动刷新）
  } catch (error: any) {
    console.error('删除智能体失败:', error)
    alert('删除失败: ' + (error?.message || '未知错误'))
  }
}

// 点击插件卡片 - 跳转到插件详情页面
const handlePluginClick = (plugin: Plugin) => {
  if (plugin.id) {
    router.push(`/plugins/${plugin.id}`)
  }
}

// 点击编辑插件按钮
const handlePluginEdit = async (plugin: Plugin) => {
  // 如果插件没有 openapiSpec（列表接口可能不返回），需要先获取详情
  if (!plugin.openapiSpec || plugin.openapiSpec === '') {
    if (plugin.id) {
      try {
        const fullPlugin = await pluginApi.getDetail(plugin.id)
        editingPlugin.value = fullPlugin
      } catch (error) {
        console.error('获取插件详情失败:', error)
        alert('获取插件详情失败，请稍后重试')
        return
      }
    } else {
      editingPlugin.value = plugin
    }
  } else {
    editingPlugin.value = plugin
  }
  showPluginDialog.value = true
}

// 打开创建插件对话框
const openCreatePluginDialog = () => {
  editingPlugin.value = null
  showPluginDialog.value = true
}

// 插件保存成功
const handlePluginSaveSuccess = () => {
  fetchCurrentData()
  showPluginDialog.value = false
  editingPlugin.value = null
}

// 导入插件
const handleImportPlugin = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = async (e: Event) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (!file) return

    try {
      const text = await file.text()
      const jsonData = JSON.parse(text)

      // 验证是否为有效的 OpenAPI 规范
      if (!jsonData.openapi || !jsonData.info || !jsonData.paths) {
        alert('无效的 OpenAPI 规范文件，请确保文件包含 openapi、info 和 paths 字段')
        return
      }

      // 创建插件
      const pluginForm: import('@/types/plugin').PluginForm = {
        name: jsonData.info.title || file.name.replace('.json', ''),
        description: jsonData.info.description || '',
        type: 'custom',
        openapiSpec: jsonData,
        config: {
          baseUrl: jsonData.servers?.[0]?.url || ''
        },
        status: 'disabled'
      }

      await pluginApi.create(pluginForm)
      await fetchCurrentData()
      alert('插件导入成功')
    } catch (error: any) {
      console.error('导入插件失败:', error)
      alert('导入失败: ' + (error?.message || '文件格式错误'))
    }
  }
  input.click()
}

// 删除插件
const handlePluginDelete = async (plugin: Plugin) => {
  if (!plugin.id) return

  try {
    await pluginApi.delete(plugin.id)
    await fetchCurrentData()
  } catch (error: any) {
    console.error('删除插件失败:', error)
    alert('删除失败: ' + (error?.message || '未知错误'))
  }
}

// 切换插件状态
const handlePluginToggleStatus = async (plugin: Plugin) => {
  if (!plugin.id) return

  try {
    if (plugin.status === 'enabled') {
      await pluginApi.disable(plugin.id)
    } else {
      await pluginApi.enable(plugin.id)
    }
    await fetchCurrentData()
  } catch (error: any) {
    console.error('切换插件状态失败:', error)
    alert('切换状态失败: ' + (error?.message || '未知错误'))
  }
}

// 创建工作流
const handleCreateWorkflow = async () => {
  try {
    const name = prompt('请输入工作流名称:')
    if (!name || !name.trim()) return

    const description = prompt('请输入工作流描述（可选）:') || ''

    const newWorkflow: WorkflowForm = {
      name: name.trim(),
      description: description.trim() || undefined,
      nodes: [{
        id: 'node-end',
        type: 'start',
        data: {
          name: '开始节点',
          input_text: '用户输入',
          output: {
            result: 'str'
          }
        },
        position: { x: 250, y: 0 }
      }, 
      {
        id: 'node-end',
        type: 'end',
        data: {
          name: '结束节点',
          output_text: '最终结果',
          output: {
            final_answer: 'str'
          }
        },
        position: { x: 300, y: 400 }
      },],
      edges: [],
      config: {},
    }

    const created = await workflowApi.create(newWorkflow)
    await fetchCurrentData()
    console.log('created', created)
    // 创建成功后跳转到编辑页面
    // if (created.id) {
    //   router.push(`/workflow/${created.id}/edit`)
    // }
  } catch (error: any) {
    console.error('创建工作流失败:', error)
    alert('创建失败: ' + (error?.message || '未知错误'))
  }
}

// 点击工作流卡片 - 跳转到编辑页面
const handleWorkflowClick = (workflow: WorkflowForm) => {
  if (workflow.id) {
    router.push(`/workflow/${workflow.id}/edit`)
  }
}

// 编辑工作流（直接跳转到编辑页面）
const handleWorkflowEdit = (workflow: WorkflowForm) => {
  handleWorkflowClick(workflow)
}

// 删除工作流
const handleWorkflowDelete = async (workflow: WorkflowForm) => {
  if (!workflow.id) return

  try {
    await workflowApi.delete(String(workflow.id))
    await fetchCurrentData()
  } catch (error: any) {
    console.error('删除工作流失败:', error)
    alert('删除失败: ' + (error?.message || '未知错误'))
  }
}

// 创建知识库
const handleCreateKnowledgeBase = async () => {
  editingKB.value = null
  showKnowledgeDialog.value = true
}

// 点击知识库卡片 - 跳转到详情页面
const handleKnowledgeBaseClick = (kb: KnowledgeBase) => {
  if (kb.id) {
    router.push(`/knowledge/${kb.id}`)
  }
}

// 编辑知识库
const handleKnowledgeBaseEdit = (kb: KnowledgeBase) => {
  editingKB.value = kb
  showKnowledgeDialog.value = true
}

// 删除知识库
const handleKnowledgeBaseDelete = async (kb: KnowledgeBase) => {
  if (!kb.id) return

  try {
    await knowledgeApi.delete(kb.id)
    await fetchCurrentData()
  } catch (error: any) {
    console.error('删除知识库失败:', error)
    alert('删除失败: ' + (error?.message || '未知错误'))
  }
}

// 关闭知识库对话框
const closeKnowledgeDialog = () => {
  showKnowledgeDialog.value = false
  editingKB.value = null
}

// 知识库保存成功回调
const handleKnowledgeBaseSaved = () => {
  closeKnowledgeDialog()
  fetchCurrentData()
}


// 组件挂载时获取数据
onMounted(async () => {
  await fetchCurrentData()
})
</script>

<template>
  <div class="home-container">
    <!-- 顶部标题栏 -->
    <header class="title-header">
      <div class="title-content">
        <h1 class="title">AnyWay</h1>
        <span class="subtitle">
          {{ activeSidebarItem === 'agent'
            ? filteredAgents.length
            : activeSidebarItem === 'plugin'
              ? filteredPlugins.length
              : activeSidebarItem === 'workflow'
                ? filteredWorkflows.length
                : activeSidebarItem === 'knowledge'
                  ? filteredKnowledgeBases.length
                  : 0 }} 个项目
        </span>
      </div>
    </header>

    <!-- 下方内容区域：侧边栏 + 主内容 -->
    <div class="content-wrapper">
      <!-- 左侧边栏 -->
      <Sidebar :active-item="activeSidebarItem" @change="handleSidebarChange" />

      <!-- 主内容区 -->
      <div class="main-content">

        <!-- 操作栏（搜索和按钮） -->
        <div class="action-bar">
          <div class="search-box">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M7.333 12.667A5.333 5.333 0 1 0 7.333 2a5.333 5.333 0 0 0 0 10.667ZM14 14l-2.9-2.9"
                stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <input v-model="searchQuery" type="text" :placeholder="`搜索${pageTitle}...`" class="search-input" />
          </div>
          <div class="action-buttons">
            <button v-if="activeSidebarItem === 'plugin'" class="btn-secondary" @click="handleImportPlugin"
              title="导入插件">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 2v8M5 7l3-3 3 3M2 12h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
                  stroke-linejoin="round" />
              </svg>
              导入
            </button>
            <button class="btn-primary" @click="openCreateDialog">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
              </svg>
              {{ createButtonText }}
            </button>
          </div>
        </div>

        <!-- 筛选区域（仅智能体显示） -->
        <div v-if="activeSidebarItem === 'agent'" class="filter-section">
          <div class="filter-tabs">
            <button v-for="option in [
              { value: 'all', label: '全部' },
              { value: 'draft', label: '草稿' },
              { value: 'published', label: '已发布' }
            ]" :key="option.value" class="filter-tab" :class="{ active: selectedStatus === option.value }"
              @click="selectedStatus = option.value">
              {{ option.label }}
            </button>
          </div>
        </div>

        <!-- 内容列表 -->
        <ContentList :loading="loading" :empty="activeSidebarItem === 'agent'
          ? filteredAgents.length === 0
          : activeSidebarItem === 'plugin'
            ? filteredPlugins.length === 0
            : activeSidebarItem === 'workflow'
              ? filteredWorkflows.length === 0
              : activeSidebarItem === 'knowledge'
                ? filteredKnowledgeBases.length === 0
                : false">
          <template #empty>
            <div class="empty-state">
              <div class="empty-icon">{{ 
                activeSidebarItem === 'workflow' ? '⚙️' 
                : activeSidebarItem === 'knowledge' ? '📚'
                : '🤖' 
              }}</div>
              <h3 class="empty-title">还没有{{ pageTitle }}</h3>
              <p class="empty-desc">创建你的第一个{{ pageTitle }}，开始 AI 之旅</p>
              <button class="btn-primary" @click="openCreateDialog">创建{{ pageTitle }}</button>
            </div>
          </template>
          <!-- 智能体卡片 -->
          <template v-if="activeSidebarItem === 'agent'">
            <AgentCard v-for="(item, index) in filteredAgents" :key="item.id || index" :agent="item" :index="index"
              @click="handleAgentClick" @edit="handleAgentEdit" @delete="handleAgentDelete" />
          </template>
          <!-- 插件卡片 -->
          <template v-if="activeSidebarItem === 'plugin'">
            <PluginCard v-for="(item, index) in filteredPlugins" :key="item.id || index" :plugin="item" :index="index"
              @click="handlePluginClick" @edit="handlePluginEdit" @delete="handlePluginDelete"
              @toggle-status="handlePluginToggleStatus" />
          </template>
          <!-- 工作流卡片 -->
          <template v-if="activeSidebarItem === 'workflow'">
            <WorkflowCard v-for="(item, index) in filteredWorkflows" :key="item.id || index" :workflow="item"
              :index="index" @click="handleWorkflowClick" @edit="handleWorkflowEdit" @delete="handleWorkflowDelete" />
          </template>
          <!-- 知识库卡片 -->
          <template v-if="activeSidebarItem === 'knowledge'">
            <KnowledgeCard v-for="(item, index) in filteredKnowledgeBases" :key="item.id || index" 
              :knowledgeBase="item" :index="index"
              @view="handleKnowledgeBaseClick" @edit="handleKnowledgeBaseEdit" @delete="handleKnowledgeBaseDelete" />
          </template>
        </ContentList>
      </div>
    </div>

    <!-- 创建智能体对话框（仅智能体时显示） -->
    <CreateAgentDialog v-if="activeSidebarItem === 'agent'" :show="showCreateDialog" @close="closeCreateDialog"
      @success="handleCreateSuccess" />

    <!-- 编辑智能体对话框 -->
    <AgentEditorDialog v-if="activeSidebarItem === 'agent'" :show="showEditDialog" :agent="editingAgent"
      @close="closeEditDialog" @save="handleEditSave" />

    <!-- 插件编辑/创建对话框 -->
    <PluginEditDialog v-if="activeSidebarItem === 'plugin'" v-model="showPluginDialog" :plugin="editingPlugin"
      @success="handlePluginSaveSuccess" />

    <!-- 知识库编辑/创建对话框 -->
    <KnowledgeDialog v-if="activeSidebarItem === 'knowledge'" :show="showKnowledgeDialog"
      :knowledge-base="editingKB || undefined" @close="closeKnowledgeDialog" @saved="handleKnowledgeBaseSaved" />
  </div>
</template>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f9fafb;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.title-header {
  background: white;
  padding: 20px 32px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
  z-index: 10;
}

.content-wrapper {
  flex: 1;
  display: flex;
  min-height: 0;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.title-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
}

.action-bar {
  background: white;
  padding: 16px 32px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: #9ca3af;
  pointer-events: none;
}

.search-input {
  padding: 8px 12px 8px 36px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  width: 100%;
  transition: all 0.2s;
  background: #f9fafb;
  color: #1f2937;
}

.search-input::placeholder {
  color: #9ca3af;
}

.search-input:focus {
  outline: none;
  border-color: #2563eb;
  background: white;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-primary:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-primary:active {
  transform: translateY(0);
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.filter-section {
  background: white;
  padding: 16px 32px;
  border-bottom: 1px solid #e5e7eb;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 6px 16px;
  border: none;
  background: transparent;
  color: #6b7280;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.filter-tab.active {
  background: #eff6ff;
  color: #2563eb;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.empty-desc {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 24px 0;
}
</style>
