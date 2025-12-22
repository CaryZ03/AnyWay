<script setup lang="ts">
import { ref, markRaw, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VueFlow, useVueFlow, Panel } from '@vue-flow/core'
import type { GraphNode, GraphEdge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { ControlButton, Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import Icon from './components/Icon.vue'
import NodeEditorSidebar from './components/NodeEditorSidebar.vue'
import CustomNode from './components/CustomNode.vue'
import { workflowApi } from '@/api'
import { graphNodeToNode, graphEdgeToWorkflowEdge, nodeToGraphNode, workflowEdgeToGraphEdge } from '@/api/workflow'
import type { WorkflowForm } from '@/types/workflow'

// , nodeToGraphNode, workflowEdgeToGraphEdge

// 导入 Vue Flow 的样式
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const router = useRouter()
const route = useRoute()

const workflowId = computed(() => route.params.id)
const workflow = ref<WorkflowForm | null>(null)
const loading = ref(false)
const workflowName = ref('')
const isEditingName = ref(false)


// localStorage 的 key
const FLOW_STORAGE_KEY = 'workflow-editor-flow'

const {
  onInit,
  onConnect,
  setViewport,
  toObject
} = useVueFlow()

const nodes = ref<GraphNode[]>([])
const edges = ref<GraphEdge[]>([])

onInit((vueFlowInstance) => {
  vueFlowInstance.fitView()
})

// 节点类型选项（除了 start 和 end）
const nodeTypeOptions = [
  { type: 'llm', label: 'LLM', icon: '🤖' },
  { type: 'http', label: 'HTTP请求', icon: '🌐' },
  { type: 'knowledge', label: '知识库检索', icon: '🔍' },
  { type: 'intent', label: '意图识别', icon: '🎯' },
  { type: 'string', label: '字符串处理', icon: '🔤' },
]

// 节点类型选择对话框显示状态
const showNodeTypeDialog = ref(false)

// 选中的节点ID（用于显示侧边栏）
const selectedNodeId = ref<string | null>(null)
// 选中的边ID（用于显示侧边栏）
const selectedEdgeId = ref<string | null>(null)

const nodeTypes = {
  custom: markRaw(CustomNode),
  start: markRaw(CustomNode),
  end: markRaw(CustomNode),
  string: markRaw(CustomNode),
  llm: markRaw(CustomNode),
  http: markRaw(CustomNode),
  intent: markRaw(CustomNode),
  knowledge: markRaw(CustomNode),
}

// 使用 onConnect hook 处理连接
// 注意：onConnect 返回 false 可以阻止连接
onConnect((connection) => {
  console.log('onConnect 被调用，connection:', connection)
  
  if (connection) {
    // 手动添加边到 edges
    // 只提供基础属性，Vue Flow 会在运行时自动计算其他属性（如 sourceNode, targetNode 等）
    const newEdge: GraphEdge = {
      id: `edge-${connection.source}-${connection.target}-${Date.now()}`,
      source: connection.source,
      target: connection.target,
      sourceHandle: connection.sourceHandle || undefined,
      targetHandle: connection.targetHandle || undefined,
      type: 'default',
      data: {},
    } as GraphEdge
    edges.value = [...edges.value, newEdge]
  }
  
  return true
})


function handleNodeClick({ node }: { node: any }) {
  // 显示侧边栏编辑节点
  selectedNodeId.value = node.id
  selectedEdgeId.value = null // 取消边选择
  console.log('节点被点击:', node)
}

// 处理边点击
function handleEdgeClick({ edge }: { edge: any }) {
  // 显示侧边栏编辑边
  selectedEdgeId.value = edge.id
  selectedNodeId.value = null // 取消节点选择
  console.log('边被点击:', edge)
}

// 点击画布空白处关闭侧边栏
function handlePaneClick() {
  selectedNodeId.value = null
  selectedEdgeId.value = null
}

function restoreFromStorage() {
  const savedData = localStorage.getItem(FLOW_STORAGE_KEY)
  if (savedData) {
    const flowData = JSON.parse(savedData)
    
    // 手动恢复 nodes 和 edges
    if (flowData.nodes) {
      nodes.value = flowData.nodes
    }
    if (flowData.edges) {
      edges.value = flowData.edges
    }
    if (flowData.viewport) {
      setViewport(flowData.viewport)
    }
    
    console.log('已恢复数据，节点数:', nodes.value.length, '边数:', edges.value.length)
  }
}

function openNodeTypeDialog() {
  showNodeTypeDialog.value = true
}

function closeNodeTypeDialog() {
  showNodeTypeDialog.value = false
}

function createNodeByType(nodeType: string) {
  const newNodeId = `node-${Date.now()}`
  // 获取视口中心位置，如果 dimensions 不可用，使用默认值
  const centerX = 400
  const centerY = 300

  // 根据节点类型创建对应的默认数据
  // 注意：不再设置output字段，因为每个节点的输出字段是固定的
  let nodeData: any = {
    name: nodeTypeOptions.find(opt => opt.type === nodeType)?.label || '新节点',
  }

  // 根据不同类型设置不同的默认数据
  // 注意：不再设置output字段，因为每个节点的输出字段是固定的
  switch (nodeType) {
    case 'llm':
      nodeData = {
        name: 'LLM',
        agent_uuid: 'agent-' + Date.now(),
        input: {},
        prompt: '请输入提示词',
        system_prompt: '你是一个有用的AI助手',
        temperature: 0.7,
        max_tokens: 2000,
      }
      break
    case 'http':
      nodeData = {
        name: 'HTTP请求',
        url: 'https://api.example.com/data',
        method: 'GET',
        headers: {},
        body: {},
      }
      break
    case 'knowledge':
      nodeData = {
        name: '知识库检索',
        knowledge_base_id: 1,
        query: '请输入查询内容',
        top_k: 5,
        similarity_threshold: 0.7,
      }
      break
    case 'intent':
      nodeData = {
        name: '意图识别',
        input: '用户输入的文本',
        intent_categories: ['查询', '投诉', '建议', '其他'],
        recognition_method: 'llm',
        agent_uuid: 'agent-' + Date.now(),
      }
      break
    case 'string':
      nodeData = {
        name: '字符串处理',
        operation: 'concat',
        input_string: 'Hello',
        parameters: {},
      }
      break
  }

  // 创建新节点对象
  // 只提供基础属性，Vue Flow 会在运行时自动计算其他属性（如 dimensions 等）
  const newNode: GraphNode = {
    id: newNodeId,
    type: nodeType as any,
    position: {
      x: centerX + (Math.random() - 0.5) * 200,
      y: centerY + (Math.random() - 0.5) * 200
    },
    data: nodeData,
  } as GraphNode

  // 直接添加到 nodes.value，因为我们现在使用独立的 ref
  nodes.value = [...nodes.value, newNode]
  closeNodeTypeDialog()
  console.log('已创建新节点:', newNodeId, '类型:', nodeType, '节点数据:', newNode)
  console.log('当前节点总数:', nodes.value.length)
}

function saveToStorage() {
  // 手动保存 nodes 和 edges
  const flowData = {
    nodes: nodes.value || [],
    edges: edges.value || [],
    viewport: toObject().viewport || { x: 0, y: 0, zoom: 1 }
  }
  console.log('保存数据:', flowData)
  localStorage.setItem(FLOW_STORAGE_KEY, JSON.stringify(flowData))
  console.log('已保存到 localStorage，节点数:', flowData.nodes.length, '边数:', flowData.edges.length)
}

function clearStorage() {
  localStorage.removeItem(FLOW_STORAGE_KEY)
  alert('已清除本地保存')
}

/**
 * toObject transforms your current graph data to an easily persist-able object
 */
function logToObject() {
  const flowData = {
    nodes: nodes.value || [],
    edges: edges.value || [],
    viewport: toObject().viewport || { x: 0, y: 0, zoom: 1 }
  }
  console.log(flowData)
}

/**
 * Resets the current viewport transformation (zoom & pan)
 */
function resetTransform() {
  setViewport({ x: 0, y: 0, zoom: 1 })
}


function closeSidebar() {
  selectedNodeId.value = null
  selectedEdgeId.value = null
}

// 处理节点更新
function handleNodesUpdate(updatedNodes: GraphNode[]) {
  nodes.value = updatedNodes
}

// 处理边更新
function handleEdgesUpdate(updatedEdges: GraphEdge[]) {
  edges.value = updatedEdges
}

// 处理节点删除
function handleNodesDelete(nodesToDelete: GraphNode[]) {
  const nodeIds = new Set(nodesToDelete.map(n => n.id))
  // 删除节点时，同时删除相关的边
  edges.value = edges.value.filter(e => 
    !nodeIds.has(e.source) && !nodeIds.has(e.target)
  )
  // 如果删除的节点是当前选中的节点，关闭侧边栏
  if (selectedNodeId.value && nodeIds.has(selectedNodeId.value)) {
    selectedNodeId.value = null
  }
}

// 处理边删除
function handleEdgesDelete(edgesToDelete: GraphEdge[]) {
  const edgeIds = new Set(edgesToDelete.map(e => e.id))
  // 如果删除的边是当前选中的边，关闭侧边栏
  if (selectedEdgeId.value && edgeIds.has(selectedEdgeId.value)) {
    selectedEdgeId.value = null
  }
}

// 加载工作流详情
const loadWorkflow = async () => {
  if (!workflowId.value) return
  
  loading.value = true
  try {
    workflow.value = await workflowApi.getDetail(workflowId.value as string)
    console.log('workflow.value', workflow.value)
    workflowName.value = workflow.value.name

    // 将业务层的 Node 和 WorkflowEdge 转换为 GraphNode 和 GraphEdge
    if (workflow.value.nodes && Array.isArray(workflow.value.nodes)) {
      nodes.value = workflow.value.nodes.map(node => nodeToGraphNode(node))
    } else {
      nodes.value = []
    }
    
    if (workflow.value.edges && Array.isArray(workflow.value.edges)) {
      edges.value = workflow.value.edges.map(edge => workflowEdgeToGraphEdge(edge))
    } else {
      edges.value = []
    }
    
    console.log('已加载工作流，节点数:', nodes.value.length, '边数:', edges.value.length)
  } catch (error) {
    console.error('加载工作流详情失败:', error)
    alert('加载工作流详情失败')
  } finally {
    loading.value = false
  }
}

// 保存工作流（包括节点和边的数据）
const saveWorkflow = async () => {
  if (!workflowId.value) return
  
  try {
    // 将 VueFlow 的 nodes 和 edges 转换为业务层格式
    const workflowNodes = (nodes.value || []).map(graphNodeToNode)
    const workflowEdges = (edges.value || []).map(graphEdgeToWorkflowEdge)
    
    const workflowForm: WorkflowForm = {
      id: workflow.value?.id,
      name: workflowName.value,
      description: workflow.value?.description,
      nodes: workflowNodes,
      edges: workflowEdges,
      config: workflow.value?.config || {},
    }
    
    await workflowApi.update(workflowId.value as string, workflowForm)
    workflow.value = workflowForm
    alert('保存成功！')
  } catch (error: any) {
    console.error('保存工作流失败:', error)
    alert('保存失败: ' + (error?.message || '未知错误'))
  }
}

// 保存工作流名称
const saveWorkflowName = async () => {
  if (!workflow.value || !workflowId.value) return
  
  isEditingName.value = false
  try {
    await workflowApi.update(workflowId.value as string, {
      ...workflow.value,
      name: workflowName.value,
    })
    workflow.value.name = workflowName.value
  } catch (error) {
    console.error('保存工作流名称失败:', error)
    alert('保存失败')
  }
}

// 删除工作流
const deleteWorkflow = async () => {
  if (!workflowId.value) return

  if (!confirm('确定要删除这个工作流吗？')) return
  
  try {
    await workflowApi.delete(workflowId.value as string)
    alert('删除成功！')
    router.push('/')
  } catch (error: any) {
    console.error('删除工作流失败:', error)
    alert('删除失败: ' + (error?.message || '未知错误'))
  }
}

// ========== 工作流执行状态管理 ==========

// 执行状态相关
const executionStatus = ref<'idle' | 'running' | 'completed' | 'failed'>('idle')
const currentExecution = ref<any>(null)
const executionResult = ref<any>(null)
const showExecutionDialog = ref(false)
const pollingInterval = ref<number | null>(null)

// 执行工作流
const executeWorkflow = async () => {
  if (!workflowId.value) return
  
  try {
    executionStatus.value = 'running'
    showExecutionDialog.value = true
    executionResult.value = null
    
    // 启动执行
    const result = await workflowApi.execute(workflowId.value as string, {})
    currentExecution.value = result
    
    // 如果执行是异步的，开始轮询状态
    if (result.status === 'pending' || result.status === 'running') {
      startPolling(result.id)
    } else {
      // 如果立即完成或失败，直接显示结果
      executionStatus.value = result.status === 'completed' ? 'completed' : 'failed'
      executionResult.value = result
    }
  } catch (error: any) {
    console.error('执行工作流失败:', error)
    executionStatus.value = 'failed'
    executionResult.value = {
      error_message: error?.message || '未知错误',
      status: 'failed'
    }
    showExecutionDialog.value = true
  }
}

// 开始轮询执行状态
function startPolling(executionId: number) {
  if (!workflowId.value) return
  
  // 清除之前的轮询
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
  
  // 设置新的轮询（每2秒查询一次）
  pollingInterval.value = window.setInterval(async () => {
    try {
      const detail = await workflowApi.getExecutionDetail(workflowId.value as string, executionId)
      currentExecution.value = detail
      
      // 更新状态
      if (detail.status === 'completed' || detail.status === 'failed') {
        executionStatus.value = detail.status === 'completed' ? 'completed' : 'failed'
        executionResult.value = detail
        stopPolling()
      } else {
        executionStatus.value = 'running'
      }
    } catch (error) {
      console.error('查询执行状态失败:', error)
      stopPolling()
      executionStatus.value = 'failed'
    }
  }, 2000)
}

// 停止轮询
function stopPolling() {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
    pollingInterval.value = null
  }
}

// 关闭执行结果对话框
function closeExecutionDialog() {
  showExecutionDialog.value = false
  stopPolling()
  // 延迟重置状态，让用户看到最终结果
  setTimeout(() => {
    if (executionStatus.value !== 'running') {
      executionStatus.value = 'idle'
      currentExecution.value = null
      executionResult.value = null
    }
  }, 500)
}

// 组件卸载时清理轮询
onUnmounted(() => {
  stopPolling()
})

// 返回
const handleBack = () => {
  router.push('/')
}

onMounted(() => {
  console.log('workflowId', workflowId.value)
  if (workflowId.value) {
    loadWorkflow()
  }
})

</script>

<template>
  <div class="workflow-editor">
    <!-- 顶部导航栏 -->
    <header class="detail-header">
      <button class="back-btn" @click="handleBack">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回
      </button>
      <div class="header-center">
        <div v-if="isEditingName" class="name-editor">
          <input
            v-model="workflowName"
            class="name-input"
            @blur="saveWorkflowName"
            @keyup.enter="saveWorkflowName"
            @keyup.esc="isEditingName = false; workflowName = workflow?.name || ''"
            autofocus
          />
        </div>
        <h1 v-else class="detail-title" @click="isEditingName = true">
          {{ workflowName || workflow?.name || '加载中...' }}
        </h1>
        <p v-if="workflow?.description" class="detail-description">{{ workflow.description }}</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="saveWorkflow" title="保存工作流">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M2 12v2h12v-2M4 6l4 4 4-4M8 2v8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          保存
        </button>
        <button class="btn-primary" @click="executeWorkflow" title="执行工作流">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M4 2v12l8-6-8-6z" fill="currentColor"/>
          </svg>
          执行
        </button>
        <button class="btn-danger" @click="deleteWorkflow" title="删除工作流">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M2 4h12M6 4V2.667A1.333 1.333 0 0 1 7.333 2h1.334A1.333 1.333 0 0 1 10 2.667V4m2 0v9.333A1.333 1.333 0 0 1 10.667 14.667H5.333A1.333 1.333 0 0 1 4 13.333V4h8z" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          删除
        </button>
      </div>
    </header>

    <!-- 内容区域 -->
    <div class="editor-content">
      <VueFlow 
        v-model:nodes="nodes"
        v-model:edges="edges"
        :nodeTypes="nodeTypes" 
        class="basic-flow"
        :default-viewport="{ zoom: 1.5 }" 
        :min-zoom="0.2" 
        :max-zoom="4" 
        @node-click="handleNodeClick"
        @edge-click="handleEdgeClick"
        @pane-click="handlePaneClick"
        @nodes-delete="handleNodesDelete"
        @edges-delete="handleEdgesDelete"
        :class="{ 'with-sidebar': selectedNodeId || selectedEdgeId }"
        :delete-key-code="'Delete'"
        :multi-selection-key-code="'Meta'"
      >
      <Background pattern-color="#aaa" :gap="16" />

      <MiniMap />

      <Controls position="bottom-center">
        <ControlButton title="Reset Transform" @click="resetTransform">
          <Icon name="reset" />
        </ControlButton>

        <ControlButton title="Log `toObject`" @click="logToObject">
          <Icon name="log" />
        </ControlButton>
      </Controls>

      <!-- 功能面板 -->
      <Panel position="top-right" class="workflow-panel">
        <div class="panel-buttons">
          <button class="panel-button" title="创建新节点" @click="openNodeTypeDialog">
            ➕ 创建节点
          </button>
          <button class="panel-button" title="保存到本地" @click="saveToStorage">
            💾 保存
          </button>
          <button class="panel-button" title="恢复上次保存" @click="restoreFromStorage">
            ↩️ 恢复
          </button>
          <button class="panel-button" title="清除本地保存" @click="clearStorage">
            ↩️ 清除
          </button>
        </div>
      </Panel>

      <!-- 节点类型选择对话框 -->
      <div v-if="showNodeTypeDialog" class="node-type-dialog-overlay" @click="closeNodeTypeDialog">
        <div class="node-type-dialog" @click.stop>
          <div class="dialog-header">
            <h3>选择节点类型</h3>
            <button class="close-button" @click="closeNodeTypeDialog">×</button>
          </div>
          <div class="dialog-content">
            <div v-for="option in nodeTypeOptions" :key="option.type" class="node-type-option"
              @click="createNodeByType(option.type)">
              <span class="node-type-icon">{{ option.icon }}</span>
              <span class="node-type-label">{{ option.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </VueFlow>

    <!-- 节点/边编辑侧边栏 -->
    <NodeEditorSidebar 
      v-if="selectedNodeId || selectedEdgeId" 
      :nodeId="selectedNodeId" 
      :edgeId="selectedEdgeId"
      :nodes="nodes"
      :edges="edges"
      @close="closeSidebar"
      @update:nodes="handleNodesUpdate"
      @update:edges="handleEdgesUpdate"
    />

    <!-- 工作流执行结果对话框 -->
    <div v-if="showExecutionDialog" class="execution-dialog-overlay" @click="closeExecutionDialog">
      <div class="execution-dialog" @click.stop>
        <div class="execution-dialog-header">
          <h3>工作流执行结果</h3>
          <button class="close-btn" @click="closeExecutionDialog" title="关闭">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        
        <div class="execution-dialog-content">
          <!-- 状态显示 -->
          <div class="execution-status-section">
            <div class="status-badge" :class="`status-${executionStatus}`">
              <span class="status-icon">
                <span v-if="executionStatus === 'running'">⏳</span>
                <span v-else-if="executionStatus === 'completed'">✅</span>
                <span v-else-if="executionStatus === 'failed'">❌</span>
                <span v-else>⏸️</span>
              </span>
              <span class="status-text">
                {{ executionStatus === 'running' ? '执行中...' : 
                   executionStatus === 'completed' ? '执行成功' : 
                   executionStatus === 'failed' ? '执行失败' : '等待中' }}
              </span>
            </div>
            
            <!-- 进度条（执行中时显示） -->
            <div v-if="executionStatus === 'running'" class="progress-bar">
              <div class="progress-bar-fill"></div>
            </div>
          </div>

          <!-- 执行结果 -->
          <div v-if="executionResult || currentExecution" class="execution-result-section">
            <div class="result-section">
              <h4>执行信息</h4>
              <div class="result-info">
                <div class="info-row">
                  <span class="info-label">执行ID:</span>
                  <span class="info-value">{{ (executionResult || currentExecution)?.id || '-' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">状态:</span>
                  <span class="info-value status-text-inline" :class="`status-${(executionResult || currentExecution)?.status}`">
                    {{ (executionResult || currentExecution)?.status || '-' }}
                  </span>
                </div>
                <div v-if="(executionResult || currentExecution)?.started_at" class="info-row">
                  <span class="info-label">开始时间:</span>
                  <span class="info-value">{{ new Date((executionResult || currentExecution).started_at).toLocaleString() }}</span>
                </div>
                <div v-if="(executionResult || currentExecution)?.completed_at" class="info-row">
                  <span class="info-label">完成时间:</span>
                  <span class="info-value">{{ new Date((executionResult || currentExecution).completed_at).toLocaleString() }}</span>
                </div>
              </div>
            </div>

            <!-- 错误信息 -->
            <div v-if="executionResult?.error_message" class="result-section error-section">
              <h4>错误信息</h4>
              <div class="error-message">{{ executionResult.error_message }}</div>
            </div>

            <!-- 输出数据 -->
            <div v-if="executionResult?.output_data" class="result-section">
              <h4>输出数据</h4>
              <pre class="output-data">{{ JSON.stringify(executionResult.output_data, null, 2) }}</pre>
            </div>

            <!-- 节点状态 -->
            <div v-if="(executionResult || currentExecution)?.node_status" class="result-section">
              <h4>节点执行状态</h4>
              <div class="node-status-list">
                <div 
                  v-for="(status, nodeId) in (executionResult || currentExecution).node_status" 
                  :key="nodeId"
                  class="node-status-item"
                >
                  <span class="node-status-id">{{ nodeId }}</span>
                  <span class="node-status-value" :class="`status-${status}`">
                    {{ status }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="execution-dialog-footer">
          <button class="btn-primary" @click="closeExecutionDialog">关闭</button>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<!-- 组件特定样式 -->
<style scoped>
.workflow-editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

/* Header 样式 */
.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e1e8ed;
  flex-shrink: 0;
  z-index: 100;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  color: #24292f;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f6f8fa;
  border-color: #0969da;
}

.header-center {
  flex: 1;
  margin: 0 24px;
  min-width: 0;
}

.detail-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.detail-title:hover {
  background: #f6f8fa;
}

.name-editor {
  display: flex;
  align-items: center;
}

.name-input {
  width: 100%;
  padding: 4px 8px;
  font-size: 20px;
  font-weight: 600;
  border: 2px solid #0969da;
  border-radius: 4px;
  outline: none;
}

.detail-description {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #656d76;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: #0969da;
  color: white;
}

.btn-primary:hover {
  background: #0860ca;
}

.btn-danger {
  background: #dc2626;
  color: white;
}

.btn-danger:hover {
  background: #b91c1c;
}

.btn-secondary {
  background: #f6f8fa;
  color: #24292f;
  border: 1px solid #d0d7de;
}

.btn-secondary:hover {
  background: #f3f4f6;
  border-color: #8c959f;
}

/* 内容区域 */
.editor-content {
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
}

.basic-flow {
  flex: 1;
  height: 100%;
  min-height: 0;
}

.basic-flow.with-sidebar {
  margin-right: 320px;
  transition: margin-right 0.3s ease;
}

/* ========== 工作流执行结果对话框样式 ========== */
.execution-dialog-overlay {
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

.execution-dialog {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 700px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

.execution-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e1e8ed;
  flex-shrink: 0;
}

.execution-dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.close-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: #656d76;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f6f8fa;
  color: #1a1a1a;
}

.execution-dialog-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.execution-status-section {
  margin-bottom: 24px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.status-running {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1976d2;
}

.status-completed {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  color: #388e3c;
}

.status-failed {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  color: #d32f2f;
}

.status-idle {
  background: #f5f5f5;
  color: #757575;
}

.status-icon {
  font-size: 16px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e1e8ed;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 12px;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #0969da 0%, #0860ca 100%);
  animation: progress 1.5s ease-in-out infinite;
  width: 60%;
}

@keyframes progress {
  0%, 100% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(300%);
  }
}

.execution-result-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-section {
  padding: 16px;
  background: #f6f8fa;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
}

.result-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  font-size: 13px;
  font-weight: 600;
  color: #656d76;
  min-width: 80px;
}

.info-value {
  font-size: 13px;
  color: #1a1a1a;
}

.status-text-inline {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.error-section {
  background: #fff5f5;
  border-color: #ffcdd2;
}

.error-message {
  padding: 12px;
  background: white;
  border-radius: 6px;
  color: #d32f2f;
  font-size: 13px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  white-space: pre-wrap;
  word-break: break-word;
}

.output-data {
  margin: 0;
  padding: 12px;
  background: white;
  border-radius: 6px;
  font-size: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  color: #1a1a1a;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.node-status-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.node-status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e1e8ed;
}

.node-status-id {
  font-size: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  color: #656d76;
}

.node-status-value {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.execution-dialog-footer {
  padding: 16px 24px;
  border-top: 1px solid #e1e8ed;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.vue-flow__minimap {
  transform: scale(75%);
  transform-origin: bottom right;
}

.basic-flow .vue-flow__controls {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.basic-flow .vue-flow__controls .vue-flow__controls-button {
  border: none;
  border-right: 1px solid #eee;
}

.basic-flow .vue-flow__controls .vue-flow__controls-button svg {
  height: 100%;
  width: 100%;
}

/* 功能面板样式 */
.workflow-panel {
  z-index: 10;
}

.panel-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.panel-button {
  padding: 8px 16px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
  white-space: nowrap;
}

.panel-button:hover {
  background: #e0e0e0;
  border-color: #bbb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.panel-button:active {
  transform: translateY(0);
}

/* 节点类型选择对话框样式 */
.node-type-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
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

.node-type-dialog {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  min-width: 320px;
  max-width: 500px;
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

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e1e8ed;
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.close-button {
  background: transparent;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-button:hover {
  background: #f0f0f0;
  color: #333;
}

.dialog-content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.node-type-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.node-type-option:hover {
  background: #f5f7fa;
  border-color: #e1e8ed;
  transform: translateX(4px);
}

.node-type-icon {
  font-size: 24px;
  line-height: 1;
}

.node-type-label {
  font-size: 15px;
  font-weight: 500;
  color: #1a1a1a;
}
</style>