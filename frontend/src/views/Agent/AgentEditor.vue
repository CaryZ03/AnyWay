<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { agentApi } from '@/api'
import type { Agent, AgentForm } from '@/types/agent'
import ConfigPanel from '@/components/business/ConfigPanel.vue'
import ChatPanel from '@/components/business/ChatPanel.vue'

const router = useRouter()
const route = useRoute()

const agentId = computed(() => {
  const id = route.params.id
  return id === 'new' ? null : Number(id)
})

const agent = ref<Agent | null>(null)
const loading = ref(false)

// 表单数据
const formData = ref<AgentForm>({
  name: '',
  description: '',
  systemPrompt: '',
  userPromptTemplate: '{user_message}',
  modelConfig: {
    provider: 'volcano',
    model: 'doubao-seed-1-6-251015',
    temperature: 0.7,
    maxTokens: 2000,
    topP: 1.0,
    frequencyPenalty: 0.0,
    presencePenalty: 0.0
  },
  workflowId: undefined,
  knowledgeBaseIds: [],
  pluginIds: [],
  status: 'draft'
})

// 加载智能体数据
const loadAgent = async () => {
  if (!agentId.value) {
    // 新建模式
    return
  }

  loading.value = true
  try {
    const data = await agentApi.getDetail(agentId.value)
    agent.value = data
    
    // 解析数据到表单
    formData.value = {
      id: data.id,
      name: data.name,
      description: data.description || '',
      systemPrompt: data.systemPrompt,
      userPromptTemplate: data.userPromptTemplate,
      modelConfig: (() => {
        const config = typeof data.modelConfig === 'string' 
          ? JSON.parse(data.modelConfig || '{}') 
          : (data.modelConfig || {})
        // 确保有默认值
        return {
          provider: config.provider || 'volcano',
          model: config.model || 'doubao-seed-1-6-251015',
          temperature: config.temperature ?? 0.7,
          maxTokens: config.maxTokens ?? 2000,
          topP: config.topP ?? 1.0,
          frequencyPenalty: config.frequencyPenalty ?? 0.0,
          presencePenalty: config.presencePenalty ?? 0.0,
        }
      })(),
      workflowId: data.workflowId,
      knowledgeBaseIds: Array.isArray(data.knowledgeBaseIds)
        ? data.knowledgeBaseIds
        : JSON.parse(data.knowledgeBaseIds as string || '[]'),
      pluginIds: Array.isArray(data.pluginIds)
        ? data.pluginIds
        : JSON.parse(data.pluginIds as string || '[]'),
      status: data.status
    }
  } catch (error) {
    console.error('加载智能体失败:', error)
  } finally {
    loading.value = false
  }
}

// 保存智能体
const saveAgent = async () => {
  try {
    if (agentId.value) {
      // 更新（注意：插件已通过 ConfigPanel 直接更新，这里只更新其他字段）
      await agentApi.update(agentId.value, {
        name: formData.value.name,
        description: formData.value.description,
        systemPrompt: formData.value.systemPrompt,
        userPromptTemplate: formData.value.userPromptTemplate,
        modelConfig: formData.value.modelConfig,
        workflowId: formData.value.workflowId,
        knowledgeBaseIds: formData.value.knowledgeBaseIds,
        // pluginIds 不需要在这里更新，因为 ConfigPanel 已经通过 API 更新了
        status: formData.value.status
      })
      agent.value = await agentApi.getDetail(agentId.value)
    } else {
      // 创建
      const newAgent = await agentApi.create(formData.value)
      router.replace(`/agent/${newAgent.id}/edit`)
    }
    alert('保存成功')
  } catch (error: any) {
    console.error('保存智能体失败:', error)
    alert('保存失败: ' + (error?.message || '未知错误'))
  }
}

// 发布智能体
const publishAgent = async () => {
  if (!agentId.value) {
    alert('请先保存智能体')
    return
  }

  try {
    // 先保存
    await agentApi.update(agentId.value, formData.value)
    // 然后发布
    await agentApi.publish(agentId.value)
    // 重新加载数据
    await loadAgent()
    alert('发布成功')
  } catch (error: any) {
    console.error('发布智能体失败:', error)
    alert('发布失败: ' + (error?.message || '未知错误'))
  }
}

// 返回列表
const handleBack = () => {
  router.push('/')
}

onMounted(() => {
  loadAgent()
})
</script>

<template>
  <div class="agent-editor">
    <!-- 顶部导航栏 -->
    <header class="editor-header">
      <button class="back-btn" @click="handleBack">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回
      </button>
      <div class="header-center">
        <h1 class="editor-title">{{ agentId ? agent?.name || '编辑智能体' : '新建智能体' }}</h1>
        <span v-if="agentId" class="editor-subtitle">ID: {{ agentId }}</span>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="saveAgent">保存草稿</button>
        <button 
          class="btn-primary" 
          @click="publishAgent"
          :disabled="!agentId || agent?.status === 'published'"
        >
          {{ agent?.status === 'published' ? '已发布' : '发布' }}
        </button>
      </div>
    </header>

    <!-- 三列布局 -->
    <div class="editor-layout">
      <!-- 左侧：提示词编辑（系统提示词 + 用户提示词模板） -->
      <div class="editor-column prompt-column">
        <!-- 系统提示词 -->
        <div class="prompt-section">
          <div class="column-header">
            <h3 class="column-title">系统提示词</h3>
          </div>
          <textarea
            v-model="formData.systemPrompt"
            class="prompt-input"
            placeholder="输入系统提示词，定义智能体的角色和行为..."
          />
        </div>
        
        <!-- 用户提示词模板 -->
        <div class="prompt-section user-prompt-section">
          <div class="column-header">
            <h3 class="column-title">用户提示词模板</h3>
            <span class="hint-text">支持变量：{user_message}, {conversation_history}, {knowledge_context}, {plugin_response}</span>
          </div>
          <textarea
            v-model="formData.userPromptTemplate"
            class="prompt-input"
            :placeholder="`用户问题：{user_message}\n\n对话历史：\n{conversation_history}\n\n相关知识：\n{knowledge_context}\n\n请基于以上信息回答用户问题。`"
          />
        </div>
      </div>

      <!-- 中间：配置面板 -->
      <div class="editor-column config-column">
        <div class="column-header">
          <h3 class="column-title">配置</h3>
        </div>
        <ConfigPanel
          :agent-id="agentId || undefined"
          :workflow-id="formData.workflowId"
          :knowledge-base-ids="formData.knowledgeBaseIds"
          :plugin-ids="formData.pluginIds"
          :model-config="formData.modelConfig"
          @update:workflow-id="formData.workflowId = $event"
          @update:knowledge-base-ids="formData.knowledgeBaseIds = $event"
          @update:plugin-ids="formData.pluginIds = $event"
          @update:model-config="formData.modelConfig = $event"
        />
      </div>

      <!-- 右侧：对话面板 -->
      <div class="editor-column chat-column">
        <div class="column-header">
          <h3 class="column-title">测试</h3>
        </div>
        <ChatPanel :agent-id="agentId || undefined" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.agent-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f9fafb;
}

.editor-header {
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 10;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.header-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.editor-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.editor-subtitle {
  font-size: 12px;
  color: #9ca3af;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-secondary {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-primary {
  padding: 8px 16px;
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.editor-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1px;
  background: #e5e7eb;
  overflow: hidden;
}

.editor-column {
  background: white;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.prompt-column,
.config-column {
  border-right: 1px solid #e5e7eb;
}

.prompt-section {
  display: flex;
  flex-direction: column;
  min-height: 0;
  border-bottom: 1px solid #e5e7eb;
  flex: 1;
  overflow: hidden;
}

.prompt-section:last-child {
  border-bottom: none;
}

.user-prompt-section {
  flex: 1;
}

.column-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.column-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.hint-text {
  font-size: 12px;
  color: #6b7280;
  font-weight: normal;
}

.prompt-input {
  flex: 1;
  width: 100%;
  padding: 20px;
  border: none;
  font-size: 14px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  resize: none;
  transition: all 0.2s;
  background: white;
  color: #1f2937;
  line-height: 1.6;
  min-height: 0;
  box-sizing: border-box;
}

.prompt-input:focus {
  outline: none;
}

.prompt-input::placeholder {
  color: #9ca3af;
  font-family: inherit;
}
</style>
