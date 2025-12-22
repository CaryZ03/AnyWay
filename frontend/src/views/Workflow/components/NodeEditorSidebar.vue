<script setup lang="ts">
import { computed, ref, nextTick, watch } from 'vue'
import type { GraphNode, GraphEdge } from '@vue-flow/core'
import type { LLMNodeConfig, HTTPNodeConfig, KnowledgeNodeConfig, IntentNodeConfig, StringNodeConfig, StartNodeConfig, EndNodeConfig } from '@/types/workflow'
import { knowledgeApi } from '@/api'
import type { KnowledgeBase } from '@/types/knowledge-base'

interface Props {
  nodeId: string | null
  edgeId: string | null
  nodes: GraphNode[]
  edges: GraphEdge[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'update:nodes', nodes: GraphNode[]): void
  (e: 'update:edges', edges: GraphEdge[]): void
}>()

// 当前选中的节点或边
const currentNode = computed(() => {
  if (!props.nodeId) return null
  return props.nodes.find(n => n.id === props.nodeId) || null
})

const currentEdge = computed(() => {
  if (!props.edgeId) return null
  return props.edges.find(e => e.id === props.edgeId) || null
})

// 节点的数据
const nodeData = computed(() => {
  return currentNode.value?.data || {}
})

// 更新节点数据
function updateNodeData(field: string, value: any) {
  if (!currentNode.value) return
  
  const updatedNodes = props.nodes.map(node => {
    if (node.id === currentNode.value!.id) {
      return {
        ...node,
        data: {
          ...node.data,
          [field]: value
        }
      }
    }
    return node
  })
  
  emit('update:nodes', updatedNodes)
}

// 更新嵌套字段（如 input.key）
function updateNestedField(path: string[], value: any) {
  if (!currentNode.value || path.length === 0) return
  
  const updatedNodes = props.nodes.map(node => {
    if (node.id === currentNode.value!.id) {
      const newData = { ...node.data }
  let current: any = newData
      
      // 遍历路径，创建嵌套对象
  for (let i = 0; i < path.length - 1; i++) {
    const key = path[i]
        if (!key) continue
        if (!current[key] || typeof current[key] !== 'object' || Array.isArray(current[key])) {
        current[key] = {}
      }
      current = current[key]
  }
  
  // 设置最终值
  const finalKey = path[path.length - 1]
  if (finalKey) {
    current[finalKey] = value
  }
  
      return {
        ...node,
        data: newData
      }
    }
    return node
  })
  
  emit('update:nodes', updatedNodes)
}

// 侧边栏宽度调整相关
const sidebarWidth = ref(320)
const isResizing = ref(false)

// 知识库列表
const knowledgeBases = ref<KnowledgeBase[]>([])
const loadingKnowledgeBases = ref(false)

// 获取知识库列表
const fetchKnowledgeBases = async () => {
  if (knowledgeBases.value.length > 0) return // 如果已加载，不再重复加载
  
  loadingKnowledgeBases.value = true
  try {
    const data = await knowledgeApi.getList()
    knowledgeBases.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('获取知识库列表失败:', error)
    knowledgeBases.value = []
  } finally {
    loadingKnowledgeBases.value = false
  }
}


// 意图编辑状态：存储每个意图的描述和示例框的显示状态
// 格式：{ 'intent-index': { showDescription: boolean, showExamples: boolean } }
const intentEditStates = ref<Record<string, { showDescription: boolean; showExamples: boolean }>>({})

// 获取意图的编辑状态
function getIntentState(intentIndex: number) {
  const key = `intent-${intentIndex}`
  if (!intentEditStates.value[key]) {
    intentEditStates.value[key] = { showDescription: false, showExamples: false }
  }
  return intentEditStates.value[key]
}

// 切换描述框显示状态
function toggleDescription(intentIndex: number) {
  const key = `intent-${intentIndex}`
  if (!intentEditStates.value[key]) {
    intentEditStates.value[key] = { showDescription: false, showExamples: false }
  }
  intentEditStates.value[key].showDescription = !intentEditStates.value[key].showDescription
  // 触发响应式更新
  intentEditStates.value = { ...intentEditStates.value }
}

// 切换示例框显示状态
function toggleExamples(intentIndex: number) {
  const key = `intent-${intentIndex}`
  if (!intentEditStates.value[key]) {
    intentEditStates.value[key] = { showDescription: false, showExamples: false }
  }
  intentEditStates.value[key].showExamples = !intentEditStates.value[key].showExamples
  // 触发响应式更新
  intentEditStates.value = { ...intentEditStates.value }
}

// 开始调整宽度
function startResize(e: MouseEvent) {
  isResizing.value = true
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  e.preventDefault()
}

// 调整宽度
function handleResize(e: MouseEvent) {
  if (!isResizing.value) return
  const newWidth = window.innerWidth - e.clientX
  // 限制宽度范围
  if (newWidth >= 250 && newWidth <= 800) {
    sidebarWidth.value = newWidth
  }
}

// 停止调整宽度
function stopResize() {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

// 用于跟踪键值对的唯一ID（解决输入框跳出问题）
const keyValueIdCounter = ref(0)
const keyValueIdMap = ref<Map<string, number>>(new Map())

// 获取或创建键值对的唯一ID
function getKeyValueId(prefix: string, key: string): number {
  const mapKey = `${prefix}-${key}`
  if (!keyValueIdMap.value.has(mapKey)) {
    keyValueIdMap.value.set(mapKey, keyValueIdCounter.value++)
  }
  return keyValueIdMap.value.get(mapKey)!
}

// 更新键值对的key时，保持ID稳定
function updateKeyValueKey(
  obj: Record<string, any>,
  oldKey: string,
  newKey: string,
  fieldName: string,
  prefix: string
) {
  if (oldKey === newKey) return
  
  // 保存旧的ID映射
  const oldMapKey = `${prefix}-${oldKey}`
  const id = keyValueIdMap.value.get(oldMapKey)
  
  // 更新对象
  const newObj = { ...obj }
  const value = newObj[oldKey]
  delete newObj[oldKey]
  newObj[newKey] = value
  
  // 更新ID映射
  if (id !== undefined) {
    keyValueIdMap.value.delete(oldMapKey)
    keyValueIdMap.value.set(`${prefix}-${newKey}`, id)
  }
  
  updateNodeData(fieldName, newObj)
  
  // 使用 nextTick 确保 DOM 更新后恢复焦点
  nextTick(() => {
    const inputs = document.querySelectorAll(`.key-value-editor input.key-input`)
    inputs.forEach((input) => {
      if ((input as HTMLInputElement).value === newKey) {
        (input as HTMLInputElement).focus()
        // 将光标移到末尾
        const len = newKey.length
        ;(input as HTMLInputElement).setSelectionRange(len, len)
      }
    })
  })
}

// 删除边
function deleteEdge() {
  if (!currentEdge.value) return
  if (!confirm('确定要删除这条连接吗？')) return
  const updatedEdges = props.edges.filter(e => e.id !== currentEdge.value!.id)
  emit('update:edges', updatedEdges)
  emit('close')
}

// 删除节点
function deleteNode() {
  if (!currentNode.value) return
  if (!confirm('确定要删除这个节点吗？删除节点会同时删除所有相关的连接。')) return
  const nodeId = currentNode.value.id
  // 删除节点
  const updatedNodes = props.nodes.filter(n => n.id !== nodeId)
  // 删除相关的边
  const updatedEdges = props.edges.filter(e => 
    e.source !== nodeId && e.target !== nodeId
  )
  emit('update:nodes', updatedNodes)
  emit('update:edges', updatedEdges)
  emit('close')
}

// 获取源节点和目标节点名称
const sourceNodeName = computed(() => {
  if (!currentEdge.value) return ''
  const sourceNode = props.nodes.find(n => n.id === currentEdge.value!.source)
  return sourceNode?.data?.name || sourceNode?.id || currentEdge.value.source
})

const targetNodeName = computed(() => {
  if (!currentEdge.value) return ''
  const targetNode = props.nodes.find(n => n.id === currentEdge.value!.target)
  return targetNode?.data?.name || targetNode?.id || currentEdge.value.target
})

// 根据节点类型渲染不同的编辑表单
const nodeType = computed(() => currentNode.value?.type || null)

// 当节点类型为knowledge时，自动加载知识库列表
watch(nodeType, (newType) => {
  if (newType === 'knowledge') {
    fetchKnowledgeBases()
  }
}, { immediate: true })

// 节点类型标签
const nodeTypeLabels: Record<string, string> = {
  start: '开始',
  end: '结束',
  llm: 'LLM',
  http: 'HTTP请求',
  knowledge: '知识库检索',
  intent: '意图识别',
  string: '字符串处理',
}

// 更新边条件
function updateEdgeCondition(value: string) {
  if (!currentEdge.value) return
  const updatedEdges = props.edges.map(edge => {
    if (edge.id === currentEdge.value!.id) {
      return {
        ...edge,
        data: {
          ...(edge.data || {}),
          condition: value
        }
      }
    }
    return edge
  })
  emit('update:edges', updatedEdges)
}

// ========== 变量替换功能 ==========

// 变量选择器相关状态
const showVarSelector = ref(false)
const availableVars = ref<Array<{
  name: string
  type: string
  label: string
  desc: string
  nodeId: string
  nodeLabel: string
  reference: string
}>>([])
const currentVarTarget = ref<{ object: any, field: string } | null>(null)

// 获取某个节点的输出定义
function getNodeOutputs(node: GraphNode) {
  const type = node.type
  const outputs: Array<{ name: string, type: string, label: string, desc: string }> = []
  
  switch (type) {
    case 'start':
      // Start 节点输出 input_text（显示为"用户输入"）
      outputs.push({
        name: 'input_text',
        type: 'string',
        label: '用户输入',
        desc: '开始节点的用户输入，实际字段名为 input_text'
      })
      break
    case 'llm':
      // LLM 节点输出 response
      outputs.push({
        name: 'response',
        type: 'string',
        label: 'LLM回复',
        desc: 'AI生成的文本回复'
      })
      break
    case 'http':
      // HTTP 节点输出 status 和 data
      outputs.push({
        name: 'status',
        type: 'number',
        label: '状态码',
        desc: 'HTTP响应状态码'
      })
      outputs.push({
        name: 'data',
        type: 'any',
        label: '响应数据',
        desc: 'HTTP响应体数据'
      })
      break
    case 'knowledge':
      // 知识库节点输出 documents
      outputs.push({
        name: 'documents',
        type: 'array',
        label: '检索结果',
        desc: '知识库检索到的文档列表'
      })
      break
    case 'intent':
      // 意图识别节点输出 intent 和 confidence
      outputs.push({
        name: 'intent',
        type: 'string',
        label: '意图类别',
        desc: '识别出的意图类别'
      })
      outputs.push({
        name: 'confidence',
        type: 'number',
        label: '置信度',
        desc: '识别置信度(0-1)'
      })
      break
    case 'string':
      // 字符串处理节点输出 result
      outputs.push({
        name: 'result',
        type: 'string',
        label: '处理结果',
        desc: '字符串操作后的结果'
      })
      break
    case 'end':
      // 结束节点输出 output_text（显示为"工作流输出"）
      outputs.push({
        name: 'output_text',
        type: 'string',
        label: '工作流输出',
        desc: '结束节点的输出文本'
      })
      break
  }
  
  return outputs
}

// 获取当前节点可用的所有上游变量
function getAvailableVariables(currentNodeId: string) {
  if (!currentNodeId) return []
  
  const predecessors = new Set<string>()
  const queue = [currentNodeId]
  const visited = new Set<string>()
  
  // 构建反向图：target -> [source1, source2...]
  const reverseEdgeMap = new Map<string, string[]>()
  props.edges.forEach(e => {
    if (!reverseEdgeMap.has(e.target)) {
      reverseEdgeMap.set(e.target, [])
    }
    reverseEdgeMap.get(e.target)!.push(e.source)
  })
  
  // BFS 查找所有上游节点
  while (queue.length > 0) {
    const current = queue.shift()!
    if (visited.has(current)) continue
    visited.add(current)
    
    const parents = reverseEdgeMap.get(current) || []
    parents.forEach(p => {
      if (!visited.has(p)) {
        predecessors.add(p)
        queue.push(p)
      }
    })
  }
  
  // 收集变量
  const variables: Array<{
    name: string
    type: string
    label: string
    desc: string
    nodeId: string
    nodeLabel: string
    reference: string
  }> = []
  
  predecessors.forEach(nodeId => {
    const node = props.nodes.find(n => n.id === nodeId)
    if (node) {
      const nodeOutputs = getNodeOutputs(node)
      nodeOutputs.forEach(out => {
        variables.push({
          ...out,
          nodeId: node.id,
          nodeLabel: node.data?.name || node.id,
          // 构造引用字符串，如 {node-1.response}
          reference: `{${node.id}.${out.name}}`
        })
      })
    }
  })
  
  return variables
}

// 打开变量选择器
function openVarSelector(targetObj: any, fieldName: string) {
  if (!props.nodeId) return
  
  // 计算可用变量
  availableVars.value = getAvailableVariables(props.nodeId)
  
  if (availableVars.value.length === 0) {
    alert('当前节点没有前序节点，或前序节点无可用输出')
    return
  }
  
  currentVarTarget.value = { object: targetObj, field: fieldName }
  showVarSelector.value = true
}

// 选择变量
function selectVariable(variable: typeof availableVars.value[0]) {
  if (currentVarTarget.value) {
    const { object, field } = currentVarTarget.value
    // 简单追加到末尾
    const currentVal = object[field] || ''
    object[field] = currentVal + variable.reference
    
    // 触发更新
    if (props.nodeId) {
      // 如果 object 是 nodeData 本身，直接更新字段
      if (object === nodeData.value) {
        updateNodeData(field, object[field])
      } else {
        // 如果是嵌套对象（如 headers, body, input），更新整个父对象
        // 判断 object 是哪个父字段
        const data = nodeData.value as any
        if (data.input === object) {
          updateNodeData('input', { ...object })
        } else if (data.headers === object) {
          updateNodeData('headers', { ...object })
        } else if (data.body === object) {
          updateNodeData('body', { ...object })
        } else if (data.parameters === object) {
          updateNodeData('parameters', { ...object })
        }
      }
    }
  }
  showVarSelector.value = false
  currentVarTarget.value = null
}

</script>

<template>
  <div v-if="currentNode || currentEdge" class="node-editor-sidebar" :style="{ width: sidebarWidth + 'px' }">
    <!-- 拖拽调整器 -->
    <div class="sidebar-resizer" @mousedown="startResize" title="拖拽调整宽度">
      <div class="resizer-handle"></div>
    </div>
    <!-- 节点编辑 -->
    <div v-if="currentNode" class="sidebar-content-wrapper">
    <div class="sidebar-header">
        <div class="header-title">
          <span v-if="nodeType" class="node-type-badge" :class="`node-type-${nodeType}`">
            {{ nodeTypeLabels[nodeType] || nodeType }}
          </span>
          <h3>{{ nodeData.name || currentNode.id }}</h3>
        </div>
        <div class="header-actions">
          <button 
            class="delete-node-btn" 
            @click="deleteNode" 
            title="删除节点"
            v-if="nodeType && nodeType !== 'start' && nodeType !== 'end'"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M2 4h12M6 4V2.667A1.333 1.333 0 0 1 7.333 2h1.334A1.333 1.333 0 0 1 10 2.667V4m2 0v9.333A1.333 1.333 0 0 1 10.667 14.667H5.333A1.333 1.333 0 0 1 4 13.333V4h8z" stroke="currentColor" stroke-width="1.5"/>
            </svg>
          </button>
          <button class="close-btn" @click="emit('close')" title="关闭">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
    </div>
    
    <div class="sidebar-content">
        <div class="form-container">
          <!-- LLM 节点表单 -->
          <template v-if="nodeType === 'llm'">
            <div class="form-section">
              <div class="form-item">
                <label class="form-label">名称</label>
                <input
                  type="text"
                  class="form-input"
                  :value="(nodeData as LLMNodeConfig).name || ''"
                  @input="(e: any) => updateNodeData('name', e.target.value)"
                />
              </div>
              <div class="form-item">
                <label class="form-label">模型名称</label>
                <input
                  type="text"
                  class="form-input"
                  :value="(nodeData as LLMNodeConfig).model || 'doubao-seed-1-6-251015'"
                  placeholder="doubao-seed-1-6-251015"
                  @input="(e: any) => updateNodeData('model', e.target.value)"
                />
              </div>
              <div class="form-item">
                <label class="form-label">提示词（必需，支持变量替换，格式：{'{nodeId.fieldName}'}）</label>
                <div class="input-with-var">
                  <textarea
                    class="form-textarea"
                    :value="(nodeData as LLMNodeConfig).prompt || ''"
                    @input="(e: any) => updateNodeData('prompt', e.target.value)"
                    rows="4"
                  />
                  <button
                    class="var-trigger"
                    type="button"
                    @click="openVarSelector(nodeData, 'prompt')"
                    title="插入变量"
                  >
                    {x}
                  </button>
                </div>
              </div>
              <div class="form-item">
                <label class="form-label">系统提示词（可选）</label>
                <div class="input-with-var">
                  <textarea
                    class="form-textarea"
                    :value="(nodeData as LLMNodeConfig).systemPrompt || ''"
                    @input="(e: any) => updateNodeData('systemPrompt', e.target.value)"
                    rows="3"
                  />
                  <button
                    class="var-trigger"
                    type="button"
                    @click="openVarSelector(nodeData, 'systemPrompt')"
                    title="插入变量"
                  >
                    {x}
                  </button>
                </div>
              </div>
              <div class="form-item">
                <label class="form-label">温度（0-2，默认0.7）</label>
                <input
                  type="number"
                  class="form-input"
                  :value="(nodeData as LLMNodeConfig).temperature ?? 0.7"
                  min="0"
                  max="2"
                  step="0.1"
                  @input="(e: any) => updateNodeData('temperature', parseFloat(e.target.value) || 0.7)"
                />
              </div>
            </div>
          </template>

          <!-- HTTP 节点表单 -->
          <template v-else-if="nodeType === 'http'">
            <div class="form-section">
              <div class="form-item">
                <label class="form-label">名称</label>
                <input
                  type="text"
                  class="form-input"
                  :value="(nodeData as HTTPNodeConfig).name || ''"
                  @input="(e: any) => updateNodeData('name', e.target.value)"
                />
              </div>
              <div class="form-item">
                <label class="form-label">URL（支持变量替换）</label>
                <div class="input-with-var">
                  <input
                    type="text"
                    class="form-input"
                    :value="(nodeData as HTTPNodeConfig).url || ''"
                    placeholder="https://api.example.com/data 或 {nodeId.fieldName}"
                    @input="(e: any) => updateNodeData('url', e.target.value)"
                  />
                  <button
                    class="var-trigger"
                    type="button"
                    @click="openVarSelector(nodeData, 'url')"
                    title="插入变量"
                  >
                    {x}
                  </button>
                </div>
              </div>
              <div class="form-item">
                <label class="form-label">请求方法</label>
                <select
                  class="form-select"
                  :value="(nodeData as HTTPNodeConfig).method || 'GET'"
                  @change="(e: any) => updateNodeData('method', e.target.value)"
                >
                  <option value="GET">GET</option>
                  <option value="POST">POST</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">请求头（支持变量替换）</label>
                <div class="key-value-editor">
                  <div
                    v-for="(value, key) in (nodeData as HTTPNodeConfig).headers || {}"
                    :key="getKeyValueId('http-headers', key)"
                    class="key-value-item"
                  >
                    <div class="key-value-content">
                      <div class="key-section">
                        <input
                          type="text"
                          class="form-input key-input"
                          :value="key"
                          placeholder="Header名称"
                          @input="(e: any) => {
                            updateKeyValueKey(
                              (nodeData as HTTPNodeConfig).headers || {},
                              key,
                              e.target.value,
                              'headers',
                              'http-headers'
                            )
                          }"
                        />
                      </div>
                      <div class="value-section">
                        <div class="input-with-var">
                          <input
                            type="text"
                            class="form-input value-input"
                            :value="value"
                            placeholder="Header值或变量 {nodeId.fieldName}"
                            @input="(e: any) => updateNestedField(['headers', key], e.target.value)"
                          />
                          <button
                            class="var-trigger"
                            type="button"
                            @click="openVarSelector((nodeData as HTTPNodeConfig).headers || {}, key)"
                            title="插入变量"
                          >
                            {x}
                          </button>
                        </div>
                      </div>
                    </div>
                    <button
                      class="btn-delete-item"
                      @click="() => {
                        const newHeaders = { ...(nodeData as HTTPNodeConfig).headers || {} }
                        delete newHeaders[key]
                        updateNodeData('headers', newHeaders)
                      }"
                      title="删除此项"
                    >
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M2 4h12M6 4V2.667A1.333 1.333 0 0 1 7.333 2h1.334A1.333 1.333 0 0 1 10 2.667V4m2 0v9.333A1.333 1.333 0 0 1 10.667 14.667H5.333A1.333 1.333 0 0 1 4 13.333V4h8z" stroke="currentColor" stroke-width="1.5"/>
                      </svg>
                    </button>
                  </div>
                  <button
                    class="btn-add"
                    @click="() => {
                      const newHeaders = { ...(nodeData as HTTPNodeConfig).headers || {}, '': '' }
                      updateNodeData('headers', newHeaders)
                    }"
                  >
                    + 添加Header
                  </button>
                </div>
              </div>
              <div v-if="(nodeData as HTTPNodeConfig).method === 'POST'" class="form-item">
                <label class="form-label">请求体（支持变量替换）</label>
                <div class="key-value-editor">
                  <div
                    v-for="(value, key) in (nodeData as HTTPNodeConfig).body || {}"
                    :key="getKeyValueId('http-body', key)"
                    class="key-value-item"
                  >
                    <div class="key-value-content">
                      <div class="key-section">
                        <input
                          type="text"
                          class="form-input key-input"
                          :value="key"
                          placeholder="字段名"
                          @input="(e: any) => {
                            updateKeyValueKey(
                              (nodeData as HTTPNodeConfig).body || {},
                              key,
                              e.target.value,
                              'body',
                              'http-body'
                            )
                          }"
                        />
                      </div>
                      <div class="value-section">
                        <div class="input-with-var">
                          <input
                            type="text"
                            class="form-input value-input"
                            :value="value"
                            placeholder="值或变量 {nodeId.fieldName}"
                            @input="(e: any) => updateNestedField(['body', key], e.target.value)"
                          />
                          <button
                            class="var-trigger"
                            type="button"
                            @click="openVarSelector((nodeData as HTTPNodeConfig).body || {}, key)"
                            title="插入变量"
                          >
                            {x}
                          </button>
                        </div>
                      </div>
                    </div>
                    <button
                      class="btn-delete-item"
                      @click="() => {
                        const newBody = { ...(nodeData as HTTPNodeConfig).body || {} }
                        delete newBody[key]
                        updateNodeData('body', newBody)
                      }"
                      title="删除此项"
                    >
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M2 4h12M6 4V2.667A1.333 1.333 0 0 1 7.333 2h1.334A1.333 1.333 0 0 1 10 2.667V4m2 0v9.333A1.333 1.333 0 0 1 10.667 14.667H5.333A1.333 1.333 0 0 1 4 13.333V4h8z" stroke="currentColor" stroke-width="1.5"/>
                      </svg>
                    </button>
                  </div>
                  <button
                    class="btn-add"
                    @click="() => {
                      const newBody = { ...(nodeData as HTTPNodeConfig).body || {}, '': '' }
                      updateNodeData('body', newBody)
                    }"
                  >
                    + 添加字段
                  </button>
                </div>
              </div>
            </div>
          </template>

          <!-- 知识库节点表单 -->
          <template v-else-if="nodeType === 'knowledge'">
            <div class="form-section">
              <div class="form-item">
                <label class="form-label">名称</label>
                <input
                  type="text"
                  class="form-input"
                  :value="(nodeData as KnowledgeNodeConfig).name || ''"
                  @input="(e: any) => updateNodeData('name', e.target.value)"
                />
              </div>
              <div class="form-item">
                <label class="form-label">知识库</label>
                <div class="knowledge-base-selector">
                  <select
                    class="form-select"
                    :value="(nodeData as KnowledgeNodeConfig).knowledge_base_id || ''"
                    @change="(e: any) => updateNodeData('knowledge_base_id', parseInt(e.target.value) || 1)"
                  >
                    <option
                      v-for="kb in knowledgeBases"
                      :key="kb.id"
                      :value="kb.id"
                    >
                      {{ kb.name }} (ID: {{ kb.id }})
                    </option>
                  </select>
                  <button
                    v-if="loadingKnowledgeBases"
                    class="btn-refresh"
                    disabled
                    title="加载中..."
                  >
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="spinning">
                      <path d="M13.333 2.667v4h-4M2.667 13.333v-4h4M11.515 4.485A5.333 5.333 0 1 0 4.485 11.515" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                  <button
                    v-else
                    class="btn-refresh"
                    @click="fetchKnowledgeBases"
                    title="刷新知识库列表"
                  >
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                      <path d="M13.333 2.667v4h-4M2.667 13.333v-4h4M11.515 4.485A5.333 5.333 0 1 0 4.485 11.515" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="form-item">
                <label class="form-label">查询文本（支持变量替换）</label>
                <div class="input-with-var">
                  <textarea
                    class="form-textarea"
                    :value="(nodeData as KnowledgeNodeConfig).query || ''"
                    placeholder="请输入查询内容或 {nodeId.fieldName}"
                    @input="(e: any) => updateNodeData('query', e.target.value)"
                    rows="3"
                  />
                  <button
                    class="var-trigger"
                    type="button"
                    @click="openVarSelector(nodeData, 'query')"
                    title="插入变量"
                  >
                    {x}
                  </button>
                </div>
              </div>
              <div class="form-item">
                <label class="form-label">Top K</label>
                <input
                  type="number"
                  class="form-input"
                  :value="(nodeData as KnowledgeNodeConfig).top_k ?? 5"
                  min="1"
                  max="10"
                  @input="(e: any) => updateNodeData('top_k', parseInt(e.target.value) || 5)"
                />
              </div>
              <div class="form-item">
                <label class="form-label">相似度阈值</label>
                <input
                  type="number"
                  class="form-input"
                  :value="(nodeData as KnowledgeNodeConfig).similarity_threshold ?? 0.7"
                  min="0"
                  max="1"
                  step="0.1"
                  @input="(e: any) => updateNodeData('similarity_threshold', parseFloat(e.target.value) || 0.7)"
                />
              </div>
            </div>
          </template>

          <!-- 意图识别节点表单 -->
          <template v-else-if="nodeType === 'intent'">
            <div class="form-section">
              <div class="form-item">
                <label class="form-label">名称</label>
                <input
                  type="text"
                  class="form-input"
                  :value="(nodeData as IntentNodeConfig).name || ''"
                  @input="(e: any) => updateNodeData('name', e.target.value)"
                />
              </div>
              <div class="form-item">
                <label class="form-label">意图列表（必需）</label>
                <div class="intents-editor">
                  <div
                    v-for="(intent, index) in (nodeData as IntentNodeConfig).intents || []"
                    :key="index"
                    class="intent-item"
                  >
                    <!-- 意图头部：ID、名称、操作按钮 -->
                    <div class="intent-item-header-new">
                      <div class="intent-id-name-row">
                        <input
                          type="text"
                          class="form-input intent-id-input"
                          :value="intent.id || ''"
                          placeholder="意图ID（如：faq）"
                          @input="(e: any) => {
                            const newIntents = [...(nodeData as IntentNodeConfig).intents || []]
                            newIntents[index] = { ...newIntents[index], id: e.target.value || '', name: newIntents[index]?.name || '' }
                            updateNodeData('intents', newIntents)
                          }"
                        />
                        <input
                          type="text"
                          class="form-input intent-name-input"
                          :value="intent.name || ''"
                          placeholder="意图名称（如：常规问答）"
                          @input="(e: any) => {
                            const newIntents = [...(nodeData as IntentNodeConfig).intents || []]
                            newIntents[index] = { ...newIntents[index], id: newIntents[index]?.id || '', name: e.target.value || '' }
                            updateNodeData('intents', newIntents)
                          }"
                        />
                      </div>
                      <div class="intent-actions">
                        <button
                          class="btn-toggle"
                          :class="{ 
                            'has-content': intent.description !== undefined && intent.description !== '' && intent.description.trim() !== '',
                            'is-expanded': getIntentState(index).showDescription
                          }"
                          @click="toggleDescription(index)"
                          title="显示/隐藏描述"
                        >
                          描述
                        </button>
                        <button
                          class="btn-toggle"
                          :class="{ 
                            'has-content': intent.examples && intent.examples.length > 0 && intent.examples.some((e: string) => e && e.trim() !== ''),
                            'is-expanded': getIntentState(index).showExamples
                          }"
                          @click="toggleExamples(index)"
                          title="显示/隐藏示例"
                        >
                          示例
                        </button>
                        <button
                          class="btn-icon btn-delete-icon"
                          @click="() => {
                            const newIntents = [...(nodeData as IntentNodeConfig).intents || []]
                            newIntents.splice(index, 1)
                            updateNodeData('intents', newIntents)
                          }"
                          title="删除意图"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                    <!-- 描述输入框（条件显示） -->
                    <div v-if="getIntentState(index).showDescription" class="intent-description-section">
                      <textarea
                        class="form-textarea"
                        :value="intent.description || ''"
                        placeholder="意图描述（可选）"
                        rows="2"
                        @input="(e: any) => {
                          const newIntents = [...(nodeData as IntentNodeConfig).intents || []]
                          const currentIntent = newIntents[index]
                          if (currentIntent) {
                            newIntents[index] = { ...currentIntent, description: e.target.value }
                            updateNodeData('intents', newIntents)
                          }
                        }"
                      />
                    </div>
                    <!-- 示例列表（条件显示） -->
                    <div v-if="getIntentState(index).showExamples" class="intent-examples-section">
                      <div
                        v-for="(example, exIndex) in (intent.examples && intent.examples.length > 0 ? intent.examples : [''])"
                        :key="`${index}-${exIndex}`"
                        class="example-item"
                      >
                        <input
                          type="text"
                          class="form-input"
                          :value="example"
                          placeholder="输入示例"
                          @input="(e: any) => {
                            const newIntents = [...(nodeData as IntentNodeConfig).intents || []]
                            const currentIntent = newIntents[index]
                            if (currentIntent) {
                              // 如果examples不存在，创建数组
                              const currentExamples = currentIntent.examples || []
                              const newExamples = [...currentExamples]
                              // 如果当前索引超出数组长度，扩展数组
                              while (newExamples.length <= exIndex) {
                                newExamples.push('')
                              }
                              newExamples[exIndex] = e.target.value
                              // 移除末尾的空字符串（但保留至少一个元素）
                              while (newExamples.length > 1 && newExamples[newExamples.length - 1] === '') {
                                newExamples.pop()
                              }
                              newIntents[index] = { ...currentIntent, examples: newExamples }
                              updateNodeData('intents', newIntents)
                            }
                          }"
                        />
                        <button
                          class="btn-delete-small"
                          @click="() => {
                            const newIntents = [...(nodeData as IntentNodeConfig).intents || []]
                            const currentIntent = newIntents[index]
                            if (currentIntent) {
                              const currentExamples = currentIntent.examples || []
                              if (currentExamples.length > 0) {
                                const newExamples = [...currentExamples]
                                newExamples.splice(exIndex, 1)
                                if (newExamples.length === 0 || (newExamples.length === 1 && newExamples[0] === '')) {
                                  // 如果删除后为空或只有一个空字符串，删除examples字段
                                  const { examples, ...rest } = currentIntent
                                  newIntents[index] = rest
                                } else {
                                  newIntents[index] = { ...currentIntent, examples: newExamples }
                                }
                              } else {
                                // 如果examples不存在，删除整个examples字段
                                const { examples, ...rest } = currentIntent
                                newIntents[index] = rest
                              }
                              updateNodeData('intents', newIntents)
                            }
                          }"
                        >
                          ×
                        </button>
                      </div>
                      <button
                        class="btn-add-small"
                        @click="() => {
                          const newIntents = [...(nodeData as IntentNodeConfig).intents || []]
                          const currentIntent = newIntents[index]
                          if (currentIntent) {
                            const currentExamples = currentIntent.examples || []
                            const newExamples = [...currentExamples, '']
                            newIntents[index] = { ...currentIntent, examples: newExamples }
                            updateNodeData('intents', newIntents)
                          }
                        }"
                      >
                        + 添加示例
                      </button>
                    </div>
                  </div>
                  <button
                    class="btn-add"
                    @click="() => {
                      const newIntents = [...(nodeData as IntentNodeConfig).intents || [], { id: '', name: '' }]
                      updateNodeData('intents', newIntents)
                    }"
                  >
                    + 添加意图
                  </button>
                </div>
              </div>
              <div class="form-item">
                <label class="form-label">模型名称（可选，默认 doubao-seed-1-6-251015）</label>
                <input
                  type="text"
                  class="form-input"
                  :value="(nodeData as IntentNodeConfig).model || 'doubao-seed-1-6-251015'"
                  @input="(e: any) => updateNodeData('model', e.target.value)"
                />
              </div>
              <div class="form-item">
                <label class="form-label">温度（可选，默认0.2）</label>
                <input
                  type="number"
                  class="form-input"
                  :value="(nodeData as IntentNodeConfig).temperature ?? 0.2"
                  min="0"
                  max="2"
                  step="0.1"
                  @input="(e: any) => updateNodeData('temperature', parseFloat(e.target.value) || 0.2)"
                />
              </div>
            </div>
          </template>

          <!-- 字符串处理节点表单 -->
          <template v-else-if="nodeType === 'string'">
            <div class="form-section">
              <div class="form-item">
                <label class="form-label">名称</label>
                <input
                  type="text"
                  class="form-input"
                  :value="(nodeData as StringNodeConfig).name || ''"
                  @input="(e: any) => updateNodeData('name', e.target.value)"
                />
              </div>
              <div class="form-item">
                <label class="form-label">操作类型</label>
                <select
                  class="form-select"
                  :value="(nodeData as StringNodeConfig).operation || 'concat'"
                  @change="(e: any) => updateNodeData('operation', e.target.value)"
                >
                  <option value="concat">拼接</option>
                  <option value="replace">替换</option>
                  <option value="substring">截取</option>
                  <option value="format">格式化</option>
                  <option value="trim">去除空格</option>
                  <option value="upper">转大写</option>
                  <option value="lower">转小写</option>
                </select>
              </div>
              <div class="form-item">
                <label class="form-label">输入字符串（支持变量替换）</label>
                <div class="input-with-var">
                  <textarea
                    class="form-textarea"
                    :value="(nodeData as StringNodeConfig).input_string || ''"
                    placeholder="Hello 或 {nodeId.fieldName}"
                    @input="(e: any) => updateNodeData('input_string', e.target.value)"
                    rows="3"
                  />
                  <button
                    class="var-trigger"
                    type="button"
                    @click="openVarSelector(nodeData, 'input_string')"
                    title="插入变量"
                  >
                    {x}
                  </button>
                </div>
              </div>
              <div class="form-item">
                <label class="form-label">处理参数</label>
                <div class="key-value-editor">
                  <div
                    v-for="(value, key) in (nodeData as StringNodeConfig).parameters || {}"
                    :key="getKeyValueId('string-parameters', key)"
                    class="key-value-row"
                  >
                    <input
                      type="text"
                      class="form-input key-input"
                      :value="key"
                      placeholder="参数名"
                      @input="(e: any) => {
                        updateKeyValueKey(
                          (nodeData as StringNodeConfig).parameters || {},
                          key,
                          e.target.value,
                          'parameters',
                          'string-parameters'
                        )
                      }"
                    />
                    <input
                      type="text"
                      class="form-input value-input"
                      :value="String(value)"
                      placeholder="参数值"
                      @input="(e: any) => updateNestedField(['parameters', key], e.target.value)"
                    />
                    <button
                      class="btn-delete"
                      @click="() => {
                        const newParams = { ...(nodeData as StringNodeConfig).parameters || {} }
                        delete newParams[key]
                        updateNodeData('parameters', newParams)
                      }"
                    >
                      删除
                    </button>
                  </div>
                  <button
                    class="btn-add"
                    @click="() => {
                      const newParams = { ...(nodeData as StringNodeConfig).parameters || {}, '': '' }
                      updateNodeData('parameters', newParams)
                    }"
                  >
                    + 添加参数
                  </button>
                </div>
              </div>
            </div>
          </template>

          <!-- 开始节点表单 -->
          <template v-else-if="nodeType === 'start'">
            <div class="form-section">
              <div class="form-item">
                <label class="form-label">名称</label>
                <input
                  type="text"
                  class="form-input"
                  :value="(nodeData as StartNodeConfig).name || ''"
                  @input="(e: any) => updateNodeData('name', e.target.value)"
                />
              </div>
              <div class="form-item">
                <label class="form-label">用户输入</label>
                <input
                  type="text"
                  class="form-input"
                  :value="(nodeData as any).input_text || ''"
                  placeholder="用户输入文本"
                  @input="(e: any) => updateNodeData('input_text', e.target.value)"
                />
              </div>
            </div>
          </template>

          <!-- 结束节点表单 -->
          <template v-else-if="nodeType === 'end'">
            <div class="form-section">
              <div class="form-item">
                <label class="form-label">名称</label>
                <input
                  type="text"
                  class="form-input"
                  :value="(nodeData as EndNodeConfig).name || ''"
                  @input="(e: any) => updateNodeData('name', e.target.value)"
                />
              </div>
              <div class="form-item">
                <label class="form-label">工作流输出（支持变量替换）</label>
                <div class="input-with-var">
                  <input
                    type="text"
                    class="form-input"
                    :value="(nodeData as EndNodeConfig).output_text || ''"
                    placeholder="最终结果或 {nodeId.fieldName}"
                    @input="(e: any) => updateNodeData('output_text', e.target.value)"
                  />
                  <button
                    class="var-trigger"
                    type="button"
                    @click="openVarSelector(nodeData, 'output_text')"
                    title="插入变量"
                  >
                    {x}
                  </button>
                </div>
              </div>
            </div>
          </template>

          <!-- 默认表单 -->
          <template v-else>
            <div class="form-section">
              <div class="form-item">
                <label class="form-label">名称</label>
                <input
                  type="text"
                  class="form-input"
                  :value="nodeData.name || ''"
                  @input="(e: any) => updateNodeData('name', e.target.value)"
                />
              </div>
              <div class="form-placeholder">
                <p>该节点类型暂不支持编辑</p>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 边编辑 -->
    <div v-if="currentEdge" class="sidebar-content-wrapper">
      <div class="sidebar-header">
        <div class="header-title">
          <span class="edge-type-badge">连接</span>
          <h3>编辑连接</h3>
        </div>
        <button class="close-btn" @click="emit('close')" title="关闭">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
      
      <div class="sidebar-content">
        <div class="form-container">
          <div class="form-section">
            <div class="form-item">
              <label class="form-label">源节点</label>
              <div class="form-readonly">{{ sourceNodeName }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">目标节点</label>
              <div class="form-readonly">{{ targetNodeName }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">连接ID</label>
              <div class="form-readonly">{{ currentEdge.id }}</div>
            </div>
            <div class="form-item">
              <label class="form-label">条件（可选）</label>
              <input
                type="text"
                class="form-input"
                :value="(currentEdge.data as any)?.condition || ''"
                placeholder="条件表达式"
                @input="(e: any) => updateEdgeCondition(e.target.value)"
              />
            </div>
            <div class="form-actions">
              <button class="btn-danger btn-full" @click="deleteEdge">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M2 4h12M6 4V2.667A1.333 1.333 0 0 1 7.333 2h1.334A1.333 1.333 0 0 1 10 2.667V4m2 0v9.333A1.333 1.333 0 0 1 10.667 14.667H5.333A1.333 1.333 0 0 1 4 13.333V4h8z" stroke="currentColor" stroke-width="1.5"/>
                </svg>
                删除连接
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 变量选择器弹窗 -->
    <div v-if="showVarSelector" class="var-selector-overlay" @click="showVarSelector = false">
      <div class="var-selector-dialog" @click.stop>
        <div class="var-selector-header">
          <h3>插入变量</h3>
          <button class="close-btn" @click="showVarSelector = false" title="关闭">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="var-selector-content">
          <div v-if="availableVars.length === 0" class="var-empty">
            <p>当前节点没有前序节点，或前序节点无可用输出</p>
          </div>
          <div v-else class="var-list">
            <div
              v-for="variable in availableVars"
              :key="variable.reference"
              class="var-item"
              @click="selectVariable(variable)"
            >
              <div class="var-info">
                <div class="var-header">
                  <span class="var-type-badge">{{ variable.type }}</span>
                  <span class="var-name">{{ variable.label }}</span>
                </div>
                <div class="var-desc">{{ variable.desc }}</div>
                <div class="var-reference">{{ variable.reference }}</div>
              </div>
              <div class="var-source">
                来自: {{ variable.nodeLabel }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.node-editor-sidebar {
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  background: white;
  box-shadow: -2px 0 12px rgba(0, 0, 0, 0.15);
  z-index: 10;
  display: flex;
  flex-direction: row;
  animation: slideIn 0.3s ease;
  overflow: hidden;
}

.sidebar-resizer {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  cursor: ew-resize;
  background: transparent;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.sidebar-resizer:hover {
  background: rgba(9, 105, 218, 0.1);
}

.sidebar-resizer:active {
  background: rgba(9, 105, 218, 0.2);
}

.resizer-handle {
  width: 2px;
  height: 40px;
  background: #0969da;
  border-radius: 1px;
  opacity: 0;
  transition: opacity 0.2s;
}

.sidebar-resizer:hover .resizer-handle {
  opacity: 1;
}

.sidebar-content-wrapper {
  width: 100%;
  margin-left: 4px;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.sidebar-content-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e1e8ed;
  flex-shrink: 0;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.header-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.delete-node-btn {
  background: transparent;
  border: 1.5px solid #dc2626;
  color: #dc2626;
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.delete-node-btn:hover {
  background: #dc2626;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.2);
}

.node-type-badge,
.edge-type-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.node-type-start {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: white;
}

.node-type-end {
  background: linear-gradient(135deg, #f44336 0%, #e53935 100%);
  color: white;
}

.node-type-llm {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
  color: white;
}

.node-type-http {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  color: white;
}

.node-type-knowledge {
  background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%);
  color: white;
}

.node-type-intent {
  background: linear-gradient(135deg, #00bcd4 0%, #0097a7 100%);
  color: white;
}

.node-type-string {
  background: linear-gradient(135deg, #607d8b 0%, #455a64 100%);
  color: white;
}

.edge-type-badge {
  background: linear-gradient(135deg, #757575 0%, #616161 100%);
  color: white;
}

.close-btn {
  background: transparent;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #fafbfc;
}

.form-container {
  max-width: 100%;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #24292f;
  margin: 0;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #d0d7de;
  border-radius: 6px;
  font-size: 14px;
  color: #1a1a1a;
  background: white;
  transition: all 0.2s;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #0969da;
  box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  line-height: 1.5;
}

.form-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath d='M6 9L1 4h10z' fill='%23666'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.knowledge-base-selector {
  display: flex;
  gap: 8px;
  align-items: center;
}

.knowledge-base-selector .form-select {
  flex: 1;
}

.btn-refresh {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f8fa;
  border: 1.5px solid #d0d7de;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #656d76;
}

.btn-refresh:hover:not(:disabled) {
  background: #0969da;
  border-color: #0969da;
  color: white;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-refresh .spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.form-readonly {
  padding: 10px 12px;
  background: #f6f8fa;
  border: 1.5px solid #d0d7de;
  border-radius: 6px;
  font-size: 14px;
  color: #656d76;
}

.key-value-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #f6f8fa;
  border: 1.5px solid #e1e8ed;
  border-radius: 8px;
}

.key-value-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px;
  background: white;
  border: 1.5px solid #e1e8ed;
  border-radius: 6px;
  transition: all 0.2s;
}

.key-value-item:hover {
  border-color: #0969da;
  box-shadow: 0 2px 4px rgba(9, 105, 218, 0.1);
}

.key-value-content {
  flex: 1;
  display: flex;
  flex-direction: row;
  gap: 12px;
  align-items: center;
}

.key-section {
  flex: 0 0 35%;
  min-width: 0;
}

.value-section {
  flex: 1;
  min-width: 0;
}

.key-input {
  width: 100%;
}

.value-input {
  width: 100%;
}

.key-value-item .form-input {
  width: 100%;
}

.key-value-row {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: white;
  border: 1.5px solid #e1e8ed;
  border-radius: 6px;
  transition: all 0.2s;
}

.key-value-row:hover {
  border-color: #0969da;
  box-shadow: 0 2px 4px rgba(9, 105, 218, 0.1);
}

.key-value-row .key-input {
  flex: 0 0 35%;
  min-width: 0;
}

.key-value-row .value-input {
  flex: 1;
  min-width: 0;
}

.btn-delete-item {
  padding: 8px;
  background: transparent;
  color: #dc2626;
  border: 1.5px solid #dc2626;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 36px;
  height: 36px;
}

.btn-delete-item:hover {
  background: #dc2626;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.2);
}

.btn-delete,
.btn-delete-small {
  padding: 8px 12px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-delete-small {
  padding: 4px;
  background: #dc2626;
  border: 1px solid #dc2626;
  color: white;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s;
  height: 28px;
  min-width: 28px;
  width: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-delete:hover {
  background: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.2);
}

.btn-delete-small:hover {
  background: #b91c1c;
  border-color: #b91c1c;
}

.btn-add,
.btn-add-small {
  padding: 8px 16px;
  background: #0969da;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-add-small {
  padding: 4px 8px;
  background: white;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  color: #24292f;
  cursor: pointer;
  transition: all 0.2s;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: flex-start;
}

.btn-add:hover {
  background: #0860ca;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(9, 105, 218, 0.2);
}

.btn-add-small:hover {
  background: #f6f8fa;
  border-color: #0969da;
  color: #0969da;
}

.array-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: white;
  border: 1.5px solid #e1e8ed;
  border-radius: 6px;
}

.array-item-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.array-item-row .form-input {
  flex: 1;
}

.keyword-group {
  padding: 12px;
  background: white;
  border: 1.5px solid #e1e8ed;
  border-radius: 6px;
  margin-bottom: 8px;
}

.keyword-group-header {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

.keyword-group-header .form-input {
  flex: 1;
}

.keyword-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-left: 12px;
}

.keyword-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.keyword-item .form-input {
  flex: 1;
}

.form-actions {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e1e8ed;
}

.btn-danger {
  padding: 12px 24px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
}

.btn-danger:hover {
  background: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(220, 38, 38, 0.2);
}

.btn-full {
  width: 100%;
}

.form-placeholder {
  padding: 40px 20px;
  text-align: center;
  color: #656d76;
  font-size: 14px;
}

/* 滚动条样式 */
.sidebar-content::-webkit-scrollbar {
  width: 8px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: #f1f3f5;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: #d0d7de;
  border-radius: 4px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: #8c959f;
}

/* ========== 变量替换相关样式 ========== */
.input-with-var {
  position: relative;
  display: block;
}

.input-with-var .form-input,
.input-with-var .form-textarea {
  width: 100%;
  padding-right: 40px; /* 为右上角按钮留出空间 */
}

.var-trigger {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  background: #0969da;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 1;
  line-height: 1;
  min-width: 28px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.var-trigger:hover {
  background: #0860ca;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(9, 105, 218, 0.2);
}

/* textarea 的变量按钮需要稍微调整位置 */
.input-with-var .form-textarea + .var-trigger {
  top: 10px;
  right: 10px;
}

/* 变量替换按钮居中 */
.var-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ========== 意图识别节点样式 ========== */
.form-hint {
  margin: 6px 0 0 0;
  font-size: 12px;
  color: #656d76;
  line-height: 1.4;
}

.keyword-mapping-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: #f6f8fa;
  border: 1.5px solid #e1e8ed;
  border-radius: 8px;
}

.keyword-mapping-item {
  padding: 16px;
  background: white;
  border: 1.5px solid #e1e8ed;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.keyword-mapping-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e1e8ed;
}

.intent-name-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.intent-label {
  font-size: 12px;
  font-weight: 600;
  color: #656d76;
}

.intent-name-input {
  width: 100%;
}

/* ========== 新的意图识别节点样式 ========== */
.intents-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.intent-item {
  padding: 12px;
  background: #f6f8fa;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.intent-item-header-new {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.intent-id-name-row {
  display: flex;
  gap: 8px;
  flex: 1;
}

.intent-id-input {
  flex: 0 0 60px;
  padding: 4px 6px;
  font-size: 12px;
  height: 28px;
  line-height: 1.2;
}

.intent-name-input {
  flex: 1;
  padding: 4px 8px;
  font-size: 12px;
  height: 28px;
  line-height: 1.2;
}

.intent-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  align-items: center;
}

.btn-icon {
  padding: 4px 4px;
  background: white;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  color: #24292f;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
}

.btn-icon:hover {
  background: #f6f8fa;
  border-color: #0969da;
  color: #0969da;
}

.btn-icon.active {
  background: #0969da;
  border-color: #0969da;
  color: white;
}

/* 描述和示例切换按钮样式 */
.btn-toggle {
  padding: 4px 4px;
  background: white;
  border: 1.5px solid #d0d7de;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 500;
  color: #24292f;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-toggle:hover {
  background: #f6f8fa;
  border-color: #0969da;
  color: #0969da;
  box-shadow: 0 2px 4px rgba(9, 105, 218, 0.1);
  transform: translateY(-1px);
}

/* 按钮有内容时的样式（浅蓝色背景） */
.btn-toggle.has-content {
  background: #e3f2fd;
  border-color: #90caf9;
  color: #1976d2;
}

.btn-toggle.has-content:hover {
  background: #bbdefb;
  border-color: #64b5f6;
  color: #1565c0;
}

/* 按钮展开时的样式（深蓝色背景） */
.btn-toggle.is-expanded {
  background: #0969da;
  border-color: #0969da;
  color: white;
  box-shadow: 0 2px 4px rgba(9, 105, 218, 0.2);
}

.btn-toggle.is-expanded:hover {
  background: #0860ca;
  border-color: #0860ca;
  color: white;
}

/* 按钮既有内容又展开时的样式 */
.btn-toggle.has-content.is-expanded {
  background: #0969da;
  border-color: #0969da;
  color: white;
}

.btn-delete-icon {
  background: #dc2626;
  border-color: #dc2626;
  color: white;
  padding: 4px 8px;
  font-size: 16px;
  line-height: 1;
  height: 28px;
  min-width: 28px;
  width: 28px;
}

.btn-delete-icon:hover {
  background: #b91c1c;
  border-color: #b91c1c;
}

.intent-description-section {
  margin-top: 8px;
}

.intent-examples-section {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.intent-examples-section .form-label-small {
  margin: 0;
  font-size: 11px;
  font-weight: 500;
  color: #656d76;
}

.example-item {
  display: flex;
  gap: 6px;
  align-items: center;
  height: 28px;
}

.example-item .form-input {
  flex: 1;
  padding: 4px 8px;
  font-size: 12px;
  height: 28px;
  line-height: 1.2;
}

.btn-delete-small {
  padding: 4px;
  background: #dc2626;
  border: 1px solid #dc2626;
  color: white;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s;
  height: 28px;
  min-width: 28px;
  width: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-delete-small:hover {
  background: #b91c1c;
  border-color: #b91c1c;
}

.btn-add-small {
  padding: 4px 8px;
  background: white;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  color: #24292f;
  cursor: pointer;
  transition: all 0.2s;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: flex-start;
}

.btn-add-small:hover {
  background: #f6f8fa;
  border-color: #0969da;
  color: #0969da;
}

.keyword-list-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.keyword-list-label {
  font-size: 12px;
  font-weight: 600;
  color: #656d76;
}

.keyword-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.keyword-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.keyword-item .form-input {
  flex: 1;
}

.var-selector-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.var-selector-dialog {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.var-selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e1e8ed;
  flex-shrink: 0;
}

.var-selector-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.var-selector-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
}

.var-empty {
  padding: 40px 20px;
  text-align: center;
  color: #656d76;
  font-size: 14px;
}

.var-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.var-item {
  padding: 16px;
  background: #f6f8fa;
  border: 1.5px solid #e1e8ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.var-item:hover {
  background: #f0f3f6;
  border-color: #0969da;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(9, 105, 218, 0.1);
}

.var-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.var-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.var-type-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  background: #0969da;
  color: white;
  text-transform: uppercase;
}

.var-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.var-desc {
  font-size: 13px;
  color: #656d76;
}

.var-reference {
  font-size: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  color: #0969da;
  background: #e8f4fd;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.var-source {
  margin-top: 8px;
  font-size: 12px;
  color: #8c959f;
  padding-top: 8px;
  border-top: 1px solid #e1e8ed;
}
</style>
