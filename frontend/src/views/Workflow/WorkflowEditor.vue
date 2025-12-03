<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { workflowApi, agentApi } from '@/api'
import type {
  WorkflowForm,
  WorkflowNode,
  StartWorkflowNode,
  EndWorkflowNode,
  IntentWorkflowNode,
  LLMWorkflowNode,
} from '@/types/workflow'

const router = useRouter()
const route = useRoute()

const workflowId = computed(() => {
  const id = route.params.id
  return id ? Number(id) : null
})

const agentId = computed(() => {
  const id = route.query.agentId
  return id ? Number(id) : null
})

const loading = ref(false)
const saving = ref(false)
const workflow = ref<WorkflowForm | null>(null)
const selectedNodeId = ref<string | null>(null)

const nodes = computed(() => workflow.value?.nodes || [])

const selectedNode = computed<WorkflowNode | null>(() => {
  if (!workflow.value || !selectedNodeId.value) return null
  return workflow.value.nodes.find((n) => n.id === selectedNodeId.value) || null
})

const title = computed(() => workflow.value?.name || '工作流编辑')

const initNewWorkflow = (): WorkflowForm => {
  const start: StartWorkflowNode = {
    id: 'start',
    type: 'start',
    name: '开始',
    position: { x: 80, y: 200 },
    config: {},
  }

  const llm: LLMWorkflowNode = {
    id: 'llm-1',
    type: 'llm',
    name: '大模型',
    position: { x: 320, y: 200 },
    config: {
      model: 'doubao-seed-1-6-251015',
      systemPrompt:
        '你是一个对话型 AI 助手，负责根据工作流上下文为用户生成最终回答。请严格按照用户提供的问题和上下文信息进行回答。',
      prompt:
        '根据下面的用户问题和工作流上下文回答用户。请使用简明、友好且准确的中文回答用户的问题。',
      temperature: 0.7,
      maxTokens: 2000,
    },
  }

  const end: EndWorkflowNode = {
    id: 'end',
    type: 'end',
    name: '结束',
    position: { x: 560, y: 200 },
    config: {},
  }

  return {
    name: '未命名工作流',
    description: '',
    version: 'v1',
    nodes: [start, llm, end],
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
}

const loadWorkflow = async () => {
  loading.value = true
  try {
    if (workflowId.value) {
      workflow.value = await workflowApi.getDetail(workflowId.value)
    } else {
      workflow.value = initNewWorkflow()
    }

    const wf = workflow.value
    if (!wf) {
      return
    }
    if (wf.nodes.length > 0) {
      selectedNodeId.value = wf.nodes[0]!.id
    }
  } catch (error) {
    console.error('加载工作流失败:', error)
    alert('加载工作流失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const persistWorkflow = async () => {
  if (!workflow.value) return
  saving.value = true
  try {
    if (workflowId.value) {
      workflow.value = await workflowApi.update(workflowId.value, workflow.value)
    } else {
      const created = await workflowApi.create(workflow.value)
      workflow.value = created

      if (agentId.value) {
        await agentApi.update(agentId.value, { workflowId: created.id })
      }

      router.replace({
        name: 'WorkflowEdit',
        params: { id: created.id },
        query: { agentId: agentId.value ?? undefined },
      })
    }
    alert('工作流已保存')
  } catch (error: any) {
    console.error('保存工作流失败:', error)
    alert('保存失败: ' + (error?.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

const handleBack = () => {
  if (agentId.value) {
    router.push(`/agent/${agentId.value}/edit`)
  } else {
    router.push('/')
  }
}

const selectNode = (nodeId: string) => {
  selectedNodeId.value = nodeId
}

const addIntentNode = () => {
  if (!workflow.value) return
  const wf = workflow.value as WorkflowForm

  const intentNode: IntentWorkflowNode = {
    id: `intent-${Date.now()}`,
    type: 'intent',
    name: '意图识别',
    position: { x: 200, y: 80 + wf.nodes.length * 40 },
    config: {
      model: 'doubao-seed-1-6-251015',
      temperature: 0.2,
      intents: [
        {
          id: 'general',
          name: '普通问答',
          description: '用户提出一般性的咨询或问题，需要直接给出回答。',
        },
      ],
    },
  }

  const endIndex = wf.nodes.findIndex((n) => n.type === 'end')
  const insertIndex = endIndex > 0 ? endIndex : wf.nodes.length - 1
  wf.nodes.splice(insertIndex, 0, intentNode)

  const lastEdgeToEndIndex = wf.edges.findIndex((e) => e.target === 'end')
  if (lastEdgeToEndIndex >= 0) {
    const prevSource = wf.edges[lastEdgeToEndIndex]!.source
    wf.edges.splice(lastEdgeToEndIndex, 1)
    wf.edges.push({
      id: `e-${prevSource}-${intentNode.id}`,
      source: prevSource,
      target: intentNode.id,
    })
    wf.edges.push({
      id: `e-${intentNode.id}-end`,
      source: intentNode.id,
      target: 'end',
    })
  }

  selectedNodeId.value = intentNode.id
}

const addLLMNode = () => {
  if (!workflow.value) return
  const wf = workflow.value as WorkflowForm

  const node: LLMWorkflowNode = {
    id: `llm-${Date.now()}`,
    type: 'llm',
    name: '大模型',
    position: { x: 320, y: 80 + wf.nodes.length * 40 },
    config: {
      model: 'doubao-seed-1-6-251015',
      systemPrompt:
        '你是一个对话型 AI 助手，负责根据工作流上下文为用户生成最终回答。请严格按照用户提供的问题和上下文信息进行回答。',
      prompt:
        '根据下面的用户问题和工作流上下文回答用户。请使用简明、友好且准确的中文回答用户的问题。',
      temperature: 0.7,
      maxTokens: 2000,
    },
  }

  const endIndex = wf.nodes.findIndex((n) => n.type === 'end')
  const insertIndex = endIndex > 0 ? endIndex : wf.nodes.length - 1
  wf.nodes.splice(insertIndex, 0, node)

  const lastEdgeToEndIndex = wf.edges.findIndex((e) => e.target === 'end')
  if (lastEdgeToEndIndex >= 0) {
    const prevSource = wf.edges[lastEdgeToEndIndex]!.source
    wf.edges.splice(lastEdgeToEndIndex, 1)
    wf.edges.push({
      id: `e-${prevSource}-${node.id}`,
      source: prevSource,
      target: node.id,
    })
    wf.edges.push({
      id: `e-${node.id}-end`,
      source: node.id,
      target: 'end',
    })
  }

  selectedNodeId.value = node.id
}

const updateSelectedNodeField = (field: string, value: any) => {
  if (!workflow.value || !selectedNode.value) return
  const wf = workflow.value as WorkflowForm
  const idx = wf.nodes.findIndex((n) => n.id === selectedNode.value!.id)
  if (idx < 0) return

  const node = { ...wf.nodes[idx] } as any
  node.config = { ...(node.config || {}), [field]: value }
  wf.nodes.splice(idx, 1, node)
}

onMounted(() => {
  loadWorkflow()
})
</script>

<template>
  <div class="workflow-editor">
    <header class="editor-header">
      <button class="back-btn" @click="handleBack">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path
            d="M12.5 15L7.5 10L12.5 5"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
        返回
      </button>
      <div class="header-center">
        <h1 class="editor-title">{{ title }}</h1>
        <span v-if="workflowId" class="editor-subtitle">Workflow ID: {{ workflowId }}</span>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="loadWorkflow">重新加载</button>
        <button class="btn-primary" :disabled="saving" @click="persistWorkflow">
          {{ saving ? '保存中...' : '保存工作流' }}
        </button>
      </div>
    </header>

    <div class="editor-layout">
      <div class="canvas-column">
        <div class="column-header">
          <h3 class="column-title">节点编排</h3>
          <div class="node-buttons">
            <button class="btn-chip" @click="addIntentNode">+ 意图识别节点</button>
            <button class="btn-chip" @click="addLLMNode">+ 大模型节点</button>
          </div>
        </div>

        <div class="canvas-body">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else class="node-flow">
            <div
              v-for="node in nodes"
              :key="node.id"
              class="node-card"
              :class="{ selected: node.id === selectedNodeId }"
              @click="selectNode(node.id)"
            >
              <div class="node-type-badge">
                {{
                  node.type === 'start'
                    ? '开始'
                    : node.type === 'end'
                      ? '结束'
                      : node.type === 'intent'
                        ? '意图识别'
                        : '大模型'
                }}
              </div>
              <div class="node-name">{{ node.name || node.id }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="config-column">
        <div class="column-header">
          <h3 class="column-title">节点配置</h3>
        </div>
        <div class="config-body" v-if="selectedNode">
          <template v-if="selectedNode.type === 'start'">
            <p class="hint-text">
              开始节点负责接收用户输入，自动构建统一的输入 JSON：
              <code>{"user_input": "用户输入内容"}</code>。
            </p>
          </template>

          <template v-else-if="selectedNode.type === 'intent'">
            <p class="hint-text">
              意图识别节点会调用大模型，对用户输入进行分类，并严格要求模型返回
              <code>{"intent_id": "...", "intent_name": "...", "reason": "..."}</code>
              形式的 JSON。
            </p>

            <label class="field-label">温度（0-2，数值越小越稳定）</label>
            <input
              type="number"
              min="0"
              max="2"
              step="0.1"
              class="field-input"
              :value="(selectedNode as IntentWorkflowNode).config.temperature ?? 0.2"
              @input="updateSelectedNodeField('temperature', Number(($event.target as HTMLInputElement).value))"
            />

            <label class="field-label">意图列表（JSON 数组）</label>
            <textarea
              class="field-textarea"
              rows="8"
              :value="JSON.stringify((selectedNode as IntentWorkflowNode).config.intents, null, 2)"
              @input="
                updateSelectedNodeField(
                  'intents',
                  JSON.parse(($event.target as HTMLTextAreaElement).value || '[]'),
                )
              "
            />
          </template>

          <template v-else-if="selectedNode.type === 'llm'">
            <p class="hint-text">
              大模型节点会读取当前工作流上下文 JSON，并要求模型严格返回
              <code>{"answer": "最终回答"}</code>
              的 JSON，用于后续结束节点输出。
            </p>

            <label class="field-label">模型名称</label>
            <input
              type="text"
              class="field-input"
              :value="(selectedNode as LLMWorkflowNode).config.model"
              @input="updateSelectedNodeField('model', ($event.target as HTMLInputElement).value)"
            />

            <label class="field-label">系统提示词</label>
            <textarea
              class="field-textarea"
              rows="4"
              :value="(selectedNode as LLMWorkflowNode).config.systemPrompt"
              @input="updateSelectedNodeField('systemPrompt', ($event.target as HTMLTextAreaElement).value)"
            />

            <label class="field-label">用户提示词模板</label>
            <textarea
              class="field-textarea"
              rows="6"
              :value="(selectedNode as LLMWorkflowNode).config.prompt"
              @input="updateSelectedNodeField('prompt', ($event.target as HTMLTextAreaElement).value)"
            />

            <label class="field-label">温度</label>
            <input
              type="number"
              min="0"
              max="2"
              step="0.1"
              class="field-input"
              :value="(selectedNode as LLMWorkflowNode).config.temperature ?? 0.7"
              @input="updateSelectedNodeField('temperature', Number(($event.target as HTMLInputElement).value))"
            />

            <label class="field-label">最大输出 Token 数</label>
            <input
              type="number"
              min="1"
              max="32000"
              step="1"
              class="field-input"
              :value="(selectedNode as LLMWorkflowNode).config.maxTokens ?? 2000"
              @input="updateSelectedNodeField('maxTokens', Number(($event.target as HTMLInputElement).value))"
            />
          </template>

          <template v-else-if="selectedNode.type === 'end'">
            <p class="hint-text">
              结束节点会读取工作流上下文中 <code>answer</code> 字段作为最终返回给用户的回答。
            </p>
          </template>
        </div>
        <div v-else class="config-empty">请选择左侧的一个节点进行配置</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workflow-editor {
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

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary:not(:disabled):hover {
  background: #1d4ed8;
}

.editor-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1px;
  background: #e5e7eb;
  overflow: hidden;
}

.canvas-column,
.config-column {
  background: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.column-header {
  padding: 14px 18px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.column-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.node-buttons {
  display: flex;
  gap: 8px;
}

.btn-chip {
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background: white;
  font-size: 12px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-chip:hover {
  background: #eff6ff;
  border-color: #2563eb;
  color: #2563eb;
}

.canvas-body {
  flex: 1;
  padding: 16px 20px;
  overflow-y: auto;
}

.loading {
  color: #9ca3af;
  font-size: 14px;
}

.node-flow {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.node-card {
  min-width: 120px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.node-card:hover {
  border-color: #2563eb;
  background: #eff6ff;
}

.node-card.selected {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25);
  background: #eff6ff;
}

.node-type-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 8px;
  border-radius: 999px;
  background: #e5e7eb;
  font-size: 11px;
  color: #4b5563;
}

.node-name {
  font-size: 13px;
  font-weight: 500;
  color: #111827;
}

.config-body {
  flex: 1;
  padding: 16px 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.config-empty {
  flex: 1;
  padding: 24px 20px;
  color: #9ca3af;
  font-size: 14px;
}

.hint-text {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
  margin-bottom: 8px;
}

.hint-text code {
  background: #f3f4f6;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 12px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-top: 6px;
}

.field-input {
  margin-top: 4px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}

.field-textarea {
  margin-top: 4px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  font-size: 13px;
  width: 100%;
  box-sizing: border-box;
  font-family: 'SF Mono', 'Menlo', 'Monaco', monospace;
}
</style>


