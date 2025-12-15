<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { pluginApi, agentApi, knowledgeApi, workflowApi } from '@/api'
import type { Plugin, Operation, PathItem } from '@/types/plugin'
import type { ModelConfig } from '@/types/agent'
import type { KnowledgeBase } from '@/types/knowledge-base'

const props = defineProps<{
  agentId?: number
  workflowId?: number
  knowledgeBaseIds: number[]
  pluginIds: number[]
  modelConfig?: ModelConfig
}>()

const emit = defineEmits<{
  (e: 'update:workflowId', value: number | undefined): void
  (e: 'update:knowledgeBaseIds', value: number[]): void
  (e: 'update:pluginIds', value: number[]): void
  (e: 'update:modelConfig', value: ModelConfig): void
}>()

const router = useRouter()

// 从 API 获取的数据
const availablePlugins = ref<Plugin[]>([])
const availableKnowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)

// 插件展开状态
const expandedPlugins = ref<Set<number>>(new Set())

// 插件详情缓存（用于存储已加载的完整插件信息）
const pluginDetailsCache = ref<Map<number, Plugin>>(new Map())

// 工具信息接口
interface ToolInfo {
  path: string
  method: string
  operation: Operation
  operationId: string
}

// 从插件中提取工具列表
const getPluginTools = (plugin: Plugin): ToolInfo[] => {
  try {
    // 如果 openapiSpec 不存在或为空，返回空数组
    if (!plugin.openapiSpec || plugin.openapiSpec === '') {
      return []
    }

    const spec = typeof plugin.openapiSpec === 'string'
      ? JSON.parse(plugin.openapiSpec)
      : plugin.openapiSpec

    if (!spec || !spec.paths) return []

    const tools: ToolInfo[] = []
    const methods = ['get', 'post'] as const

    for (const [path, pathItem] of Object.entries(spec.paths)) {
      if (!pathItem) continue
      
      for (const method of methods) {
        const operation = (pathItem as PathItem)[method]
        if (operation && operation.operationId) {
          tools.push({
            path,
            method: method.toUpperCase(),
            operation,
            operationId: operation.operationId
          })
        }
      }
    }

    return tools
  } catch (error) {
    console.error('解析插件工具失败:', error, plugin)
    return []
  }
}

// 切换插件展开状态，如果需要工具列表但插件没有 openapiSpec，则懒加载详情
const togglePlugin = async (pluginId: number | undefined) => {
  if (!pluginId) return
  
  if (expandedPlugins.value.has(pluginId)) {
    // 收起
    expandedPlugins.value.delete(pluginId)
  } else {
    // 展开
    expandedPlugins.value.add(pluginId)
    
    // 检查是否需要加载详情
    const plugin = availablePlugins.value.find(p => p.id === pluginId)
    if (plugin && (!plugin.openapiSpec || plugin.openapiSpec === '')) {
      // 如果插件没有 openapiSpec，需要获取详情
      try {
        const fullPlugin = await pluginApi.getDetail(pluginId)
        // 更新缓存
        pluginDetailsCache.value.set(pluginId, fullPlugin)
        // 更新列表中的插件
        const index = availablePlugins.value.findIndex(p => p.id === pluginId)
        if (index !== -1) {
          availablePlugins.value[index] = fullPlugin
        }
      } catch (error) {
        console.error('获取插件详情失败:', error)
        // 即使失败也继续展开，只是工具列表为空
      }
    }
  }
}

// 检查插件是否被选中
const isPluginSelected = (pluginId: number | undefined) => {
  if (!pluginId) return false
  return props.pluginIds.includes(pluginId)
}

// 检查知识库是否被选中
const isKnowledgeBaseSelected = (knowledgeBaseId: number | undefined) => {
  if (!knowledgeBaseId) return false
  return props.knowledgeBaseIds.includes(knowledgeBaseId)
}

// 切换知识库选择
const handleKnowledgeBaseToggle = async (knowledgeBaseId: number | undefined) => {
  if (!knowledgeBaseId) return
  
  const current = [...props.knowledgeBaseIds]
  const index = current.indexOf(knowledgeBaseId)
  const isAdding = index === -1

  // 如果有 agentId，直接调用 API 更新
  if (props.agentId) {
    try {
      // 更新知识库关联
      const updatedIds = isAdding 
        ? [...current, knowledgeBaseId]
        : current.filter(id => id !== knowledgeBaseId)
      
      await agentApi.update(props.agentId, {
        knowledgeBaseIds: updatedIds
      })
      emit('update:knowledgeBaseIds', updatedIds)
    } catch (error: any) {
      console.error('更新知识库关联失败:', error)
      alert('更新知识库关联失败: ' + (error?.message || '未知错误'))
    }
  } else {
    // 没有 agentId，只更新本地状态（用于新建场景）
    if (isAdding) {
      current.push(knowledgeBaseId)
    } else {
      current.splice(index, 1)
    }
    emit('update:knowledgeBaseIds', current)
  }
}

// 切换插件选择
const handlePluginToggle = async (pluginId: number | undefined) => {
  if (!pluginId) return
  
  const current = [...props.pluginIds]
  const index = current.indexOf(pluginId)
  const isAdding = index === -1

  // 如果有 agentId，直接调用 API
  if (props.agentId) {
    try {
      if (isAdding) {
        await agentApi.addPlugins(props.agentId, pluginId)
        current.push(pluginId)
      } else {
        await agentApi.removePlugins(props.agentId, pluginId)
        current.splice(index, 1)
      }
      emit('update:pluginIds', current)
    } catch (error: any) {
      console.error('更新插件失败:', error)
      alert('更新插件失败: ' + (error?.message || '未知错误'))
    }
  } else {
    // 没有 agentId，只更新本地状态（用于新建场景）
    if (isAdding) {
      current.push(pluginId)
    } else {
      current.splice(index, 1)
    }
    emit('update:pluginIds', current)
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const [plugins, knowledgeBases] = await Promise.all([
      pluginApi.getList(),
      knowledgeApi.getList()
    ])
    // 只显示启用的插件
    availablePlugins.value = plugins.filter(p => p.status === 'enabled')
    availableKnowledgeBases.value = knowledgeBases
  } catch (error) {
    console.error('加载配置数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取方法的颜色
const getMethodColor = (method: string) => {
  const colors: Record<string, string> = {
    GET: '#10b981',
    POST: '#3b82f6'
  }
  return colors[method] || '#6b7280'
}

// 大模型配置
const modelProvider = ref<'volcano' | 'openai'>('volcano')
const modelName = ref('doubao-seed-1-6-251015')
const temperature = ref(0.7)
const maxTokens = ref(2000)
const topP = ref(1.0)
const frequencyPenalty = ref(0.0)
const presencePenalty = ref(0.0)

// 可用的模型列表
const volcanoModels = [
  { value: 'doubao-seed-1-6-251015', label: '豆包 Seed 1.6' },
  { value: 'doubao-pro-4k', label: '豆包 Pro 4K' },
  { value: 'doubao-pro-32k', label: '豆包 Pro 32K' },
]

const openaiModels = [
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  { value: 'gpt-4', label: 'GPT-4' },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
]

// 初始化模型配置
const initModelConfig = () => {
  if (props.modelConfig && Object.keys(props.modelConfig).length > 0) {
    // 优先使用 provider，如果没有则根据模型名称判断
    if (props.modelConfig.provider) {
      modelProvider.value = props.modelConfig.provider
    } else {
      const model = props.modelConfig.model || 'doubao-seed-1-6-251015'
      if (model.startsWith('gpt-')) {
        modelProvider.value = 'openai'
      } else {
        modelProvider.value = 'volcano'
      }
    }
    
    modelName.value = props.modelConfig.model || (modelProvider.value === 'volcano' ? 'doubao-seed-1-6-251015' : 'gpt-3.5-turbo')
    temperature.value = props.modelConfig.temperature ?? 0.7
    maxTokens.value = props.modelConfig.maxTokens ?? 2000
    topP.value = props.modelConfig.topP ?? 1.0
    frequencyPenalty.value = props.modelConfig.frequencyPenalty ?? 0.0
    presencePenalty.value = props.modelConfig.presencePenalty ?? 0.0
  } else {
    // 如果没有配置，使用默认值
    modelProvider.value = 'volcano'
    modelName.value = 'doubao-seed-1-6-251015'
    temperature.value = 0.7
    maxTokens.value = 2000
    topP.value = 1.0
    frequencyPenalty.value = 0.0
    presencePenalty.value = 0.0
    updateModelConfig()
  }
}

// 更新模型配置
const updateModelConfig = () => {
  const config: ModelConfig = {
    provider: modelProvider.value,
    model: modelName.value,
    temperature: temperature.value,
    maxTokens: maxTokens.value,
    topP: topP.value,
    frequencyPenalty: frequencyPenalty.value,
    presencePenalty: presencePenalty.value,
  }
  emit('update:modelConfig', config)
}

// 当提供商切换时，自动切换到该提供商的第一个模型
watch(modelProvider, (newProvider) => {
  if (newProvider === 'volcano') {
    modelName.value = 'doubao-seed-1-6-251015'
  } else {
    modelName.value = 'gpt-3.5-turbo'
  }
  updateModelConfig()
})

// 监听配置变化
watch([modelName, temperature, maxTokens, topP, frequencyPenalty, presencePenalty], () => {
  updateModelConfig()
})

// 监听外部 modelConfig 变化
watch(() => props.modelConfig, () => {
  initModelConfig()
}, { deep: true, immediate: true })

onMounted(() => {
  loadData()
  initModelConfig()
})

// 打开工作流编辑页面
const openWorkflowEditor = async () => {
  try {
    // 如果已经绑定了工作流，直接跳转
    if (props.workflowId && props.agentId) {
      router.push({
        name: 'WorkflowEdit',
        params: { id: props.workflowId },
        query: { agentId: props.agentId },
      })
      return
    }

    // 没有工作流时，为当前智能体创建一个默认工作流
    if (!props.agentId) {
      alert('请先保存智能体，再配置工作流')
      return
    }

    const defaultWorkflow: import('@/types/workflow').WorkflowForm = {
      name: '智能体工作流',
      description: '由智能体自动创建的默认工作流',
      version: 'v1',
      nodes: [
        {
          id: 'start',
          type: 'start',
          name: '开始',
          position: { x: 80, y: 200 },
          config: {},
        },
        {
          id: 'llm-1',
          type: 'llm',
          name: '大模型',
          position: { x: 320, y: 200 },
          config: {
            agent_uuid: '',
            prompt:
              '根据下面的用户问题和工作流上下文回答用户。请使用简明、友好且准确的中文回答用户的问题。',
            temperature: 0.7,
            max_tokens: 2000,
          },
        },
        {
          id: 'end',
          type: 'end',
          name: '结束',
          position: { x: 560, y: 200 },
          config: {},
        },
      ],
      edges: [
        { id: 'e-start-llm-1', source: 'start', target: 'llm-1' },
        { id: 'e-llm-1-end', source: 'llm-1', target: 'end' },
      ],
      config: {
        timeout: 60,
        retry: 0,
        parallel: false,
        version: 'v1',
      },
    }

    const created = await workflowApi.create(defaultWorkflow)
    await agentApi.update(props.agentId, { workflowId: created.id })
    emit('update:workflowId', created.id)

    router.push({
      name: 'WorkflowEdit',
      params: { id: created.id },
      query: { agentId: props.agentId },
    })
  } catch (error: any) {
    console.error('打开工作流编辑器失败:', error)
    alert('打开工作流编辑器失败: ' + (error?.message || '未知错误'))
  }
}
</script>

<template>
  <div class="config-panel">
    <div v-if="loading" class="loading-state">
      <div class="loading-text">加载中...</div>
    </div>
    <template v-else>
      <!-- 知识库配置 -->
      <div class="config-section">
        <label class="section-label">知识库</label>
        <div v-if="availableKnowledgeBases.length === 0" class="empty-hint">
          暂无知识库
        </div>
        <div v-else class="knowledge-base-list">
          <div
            v-for="kb in availableKnowledgeBases"
            :key="kb.id"
            class="knowledge-base-item"
          >
            <label class="knowledge-base-checkbox">
              <input
                type="checkbox"
                :checked="isKnowledgeBaseSelected(kb.id!)"
                @change="handleKnowledgeBaseToggle(kb.id!)"
              />
              <div class="knowledge-base-info">
                <span class="knowledge-base-name">{{ kb.name }}</span>
                <span v-if="kb.description" class="knowledge-base-description">{{ kb.description }}</span>
                <span class="knowledge-base-meta">
                  {{ kb.documentCount || 0 }} 个文档
                </span>
              </div>
            </label>
          </div>
        </div>
      </div>

      <div class="config-section">
        <label class="section-label">插件</label>
        <div v-if="availablePlugins.length === 0" class="empty-hint">
          暂无插件
        </div>
        <div v-else class="plugin-list">
          <div
            v-for="plugin in availablePlugins"
            :key="plugin.id"
            class="plugin-item"
          >
            <div class="plugin-header" @click="togglePlugin(plugin.id!)">
              <label class="plugin-checkbox" @click.stop>
                <input
                  type="checkbox"
                  :checked="isPluginSelected(plugin.id!)"
                  @change="handlePluginToggle(plugin.id!)"
                />
              </label>
              <span class="plugin-name">{{ plugin.name }}</span>
              <button class="expand-btn" :class="{ expanded: expandedPlugins.has(plugin.id!) }">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
            <div v-if="expandedPlugins.has(plugin.id!)" class="plugin-tools">
              <div
                v-for="tool in getPluginTools(plugin)"
                :key="`${tool.path}-${tool.method}`"
                class="tool-item"
              >
                <div class="tool-method" :style="{ backgroundColor: getMethodColor(tool.method) }">
                  {{ tool.method }}
                </div>
                <div class="tool-info">
                  <div class="tool-name">{{ tool.operationId }}</div>
                  <div class="tool-path">{{ tool.path }}</div>
                  <div v-if="tool.operation.summary" class="tool-summary">{{ tool.operation.summary }}</div>
                </div>
              </div>
              <div v-if="getPluginTools(plugin).length === 0" class="no-tools">
                <span v-if="!plugin.openapiSpec || plugin.openapiSpec === ''">正在加载工具列表...</span>
                <span v-else>该插件暂无可用工具</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 大模型配置 -->
      <div class="config-section">
        <label class="section-label">大模型配置</label>
        
        <!-- 模型提供商 -->
        <div class="config-item">
          <label class="config-item-label">提供商</label>
          <select v-model="modelProvider" class="config-select" @change="updateModelConfig">
            <option value="volcano">火山引擎（豆包）</option>
            <option value="openai">OpenAI</option>
          </select>
        </div>

        <!-- 模型名称 -->
        <div class="config-item">
          <label class="config-item-label">模型</label>
          <select v-model="modelName" class="config-select" @change="updateModelConfig">
            <option 
              v-for="model in (modelProvider === 'volcano' ? volcanoModels : openaiModels)"
              :key="model.value"
              :value="model.value"
            >
              {{ model.label }}
            </option>
          </select>
        </div>

        <!-- Temperature -->
        <div class="config-item">
          <label class="config-item-label">
            Temperature
            <span class="config-hint">(0-2，控制随机性)</span>
          </label>
          <div class="config-slider-wrapper">
            <input 
              v-model.number="temperature" 
              type="range" 
              min="0" 
              max="2" 
              step="0.1"
              class="config-slider"
              @input="updateModelConfig"
            />
            <span class="config-value">{{ temperature.toFixed(1) }}</span>
          </div>
        </div>

        <!-- Max Tokens -->
        <div class="config-item">
          <label class="config-item-label">
            Max Tokens
            <span class="config-hint">(最大输出长度)</span>
          </label>
          <input 
            v-model.number="maxTokens" 
            type="number" 
            min="1" 
            max="32000"
            class="config-input"
            @input="updateModelConfig"
          />
        </div>

        <!-- Top P -->
        <div class="config-item">
          <label class="config-item-label">
            Top P
            <span class="config-hint">(0-1，核采样参数)</span>
          </label>
          <div class="config-slider-wrapper">
            <input 
              v-model.number="topP" 
              type="range" 
              min="0" 
              max="1" 
              step="0.1"
              class="config-slider"
              @input="updateModelConfig"
            />
            <span class="config-value">{{ topP.toFixed(1) }}</span>
          </div>
        </div>

        <!-- Frequency Penalty -->
        <div class="config-item">
          <label class="config-item-label">
            Frequency Penalty
            <span class="config-hint">(-2到2，降低重复)</span>
          </label>
          <div class="config-slider-wrapper">
            <input 
              v-model.number="frequencyPenalty" 
              type="range" 
              min="-2" 
              max="2" 
              step="0.1"
              class="config-slider"
              @input="updateModelConfig"
            />
            <span class="config-value">{{ frequencyPenalty.toFixed(1) }}</span>
          </div>
        </div>

        <!-- Presence Penalty -->
        <div class="config-item">
          <label class="config-item-label">
            Presence Penalty
            <span class="config-hint">(-2到2，鼓励新话题)</span>
          </label>
          <div class="config-slider-wrapper">
            <input 
              v-model.number="presencePenalty" 
              type="range" 
              min="-2" 
              max="2" 
              step="0.1"
              class="config-slider"
              @input="updateModelConfig"
            />
            <span class="config-value">{{ presencePenalty.toFixed(1) }}</span>
          </div>
        </div>
      </div>

      <!-- 工作流配置入口 -->
      <div class="config-section">
        <label class="section-label">工作流</label>
        <div class="workflow-row">
          <div class="workflow-info">
            <div class="workflow-title">
              {{ workflowId ? `已绑定工作流 #${workflowId}` : '尚未绑定工作流' }}
            </div>
            <div class="workflow-desc">
              使用工作流可以通过「开始 → 意图识别 → 大模型 → 结束」等节点，编排更复杂的回复流程。
            </div>
          </div>
          <button class="workflow-btn" @click="openWorkflowEditor">
            {{ workflowId ? '编辑工作流' : '创建并编辑工作流' }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.config-panel {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.config-section {
  margin-bottom: 32px;
}

.section-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.config-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  color: #1f2937;
  cursor: pointer;
  transition: all 0.2s;
}

.config-select:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.empty-hint {
  color: #9ca3af;
  font-size: 13px;
  padding: 24px;
  text-align: center;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px dashed #d1d5db;
}

.checkbox-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s;
}

.checkbox-item:hover {
  border-color: #2563eb;
  background: #eff6ff;
}

.checkbox-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #2563eb;
}

.checkbox-item span {
  font-size: 14px;
  color: #374151;
  flex: 1;
}

.plugin-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.plugin-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  overflow: hidden;
}

.plugin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f9fafb;
}

.plugin-header:hover {
  background: #f3f4f6;
}

.plugin-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  cursor: pointer;
}

.plugin-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #2563eb;
}

.plugin-name {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.expand-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 4px;
}

.expand-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.expand-btn.expanded {
  transform: rotate(90deg);
}

.plugin-tools {
  border-top: 1px solid #e5e7eb;
  padding: 8px;
  background: white;
}

.tool-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 6px;
  transition: all 0.2s;
  cursor: pointer;
}

.tool-item:hover {
  background: #f9fafb;
}

.tool-method {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  min-width: 45px;
  text-align: center;
  flex-shrink: 0;
}

.tool-info {
  flex: 1;
  min-width: 0;
}

.tool-name {
  font-size: 13px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 2px;
  word-break: break-word;
}

.tool-path {
  font-size: 12px;
  color: #6b7280;
  font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  margin-bottom: 4px;
  word-break: break-all;
}

.tool-summary {
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.4;
}

.no-tools {
  padding: 16px;
  text-align: center;
  color: #9ca3af;
  font-size: 13px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.loading-text {
  color: #9ca3af;
  font-size: 14px;
}

.config-item {
  margin-bottom: 16px;
}

.config-item-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.config-hint {
  font-weight: normal;
  color: #9ca3af;
  font-size: 12px;
}

.config-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  color: #1f2937;
  transition: all 0.2s;
}

.config-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.config-slider-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.config-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e5e7eb;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.config-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  transition: all 0.2s;
}

.config-slider::-webkit-slider-thumb:hover {
  background: #1d4ed8;
  transform: scale(1.1);
}

.config-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.config-slider::-moz-range-thumb:hover {
  background: #1d4ed8;
  transform: scale(1.1);
}

.config-value {
  min-width: 40px;
  text-align: right;
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

.knowledge-base-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.knowledge-base-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  transition: all 0.2s;
}

.knowledge-base-item:hover {
  border-color: #2563eb;
  background: #f9fafb;
}

.knowledge-base-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
}

.knowledge-base-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #2563eb;
  margin-top: 2px;
  flex-shrink: 0;
}

.knowledge-base-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.knowledge-base-name {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.knowledge-base-description {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

.knowledge-base-meta {
  font-size: 12px;
  color: #9ca3af;
}

.workflow-row {
  margin-top: 8px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.workflow-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.workflow-title {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
}

.workflow-desc {
  font-size: 12px;
  color: #6b7280;
}

.workflow-btn {
  padding: 6px 12px;
  border-radius: 999px;
  border: none;
  background: #2563eb;
  color: #ffffff;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.workflow-btn:hover {
  background: #1d4ed8;
}
</style>
