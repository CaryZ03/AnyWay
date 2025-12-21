<script setup lang="ts">
import { ref, markRaw, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { VueFlow, useVueFlow, Panel } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { ControlButton, Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
// import { initialEdges, initialNodes } from './initial-elements'
import Icon from './components/Icon.vue'
// import NodeEditorSidebar from './components/NodeEditorSidebar.vue'
import CustomNode from './components/CustomNode.vue'
import { workflowApi } from '@/api'
import { graphNodeToNode, graphEdgeToWorkflowEdge } from '@/api/workflow'
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
  addNodes,
  setViewport,
  toObject,
  fromObject,
  dimensions,
  nodes,
  edges
} = useVueFlow()

onInit((vueFlowInstance) => {
  // instance is the same as the return of `useVueFlow`
  vueFlowInstance.fitView()
})

// 节点类型选项（除了 start 和 end）
const nodeTypeOptions = [
  { type: 'llm', label: 'LLM节点', icon: '🤖' },
  { type: 'http', label: 'HTTP请求', icon: '🌐' },
  { type: 'knowledge', label: '知识库检索', icon: '🔍' },
  { type: 'intent', label: '意图识别', icon: '🎯' },
  { type: 'string', label: '字符串处理', icon: '🔤' },
]

// 节点类型选择对话框显示状态
const showNodeTypeDialog = ref(false)

// 选中的节点ID（用于显示侧边栏）
const selectedNodeId = ref<string | null>(null)

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

// onInit 已经在上面定义了，这里不需要重复定义

// 使用 onConnect hook 处理连接
// 注意：onConnect 返回 false 可以阻止连接
onConnect((connection) => {
  console.log('onConnect 被调用，connection:', connection)
  
  // if (!connection) {
  //   console.warn('连接对象为空')
  //   return false
  // }
  
  // // 验证连接的有效性
  // if (!connection.source || !connection.target) {
  //   console.warn('连接缺少源节点或目标节点:', connection)
  //   return false
  // }
  
  // // 防止自己连接自己（检查节点ID）
  // if (connection.source === connection.target) {
  //   console.warn('不能连接到自己，节点ID:', connection.source)
  //   return false
  // }
  
  // // 检查 sourceHandle 和 targetHandle 是否相同（防止同一个 handle 连接自己）
  // if (connection.sourceHandle && connection.targetHandle && 
  //     connection.source === connection.target && 
  //     connection.sourceHandle === connection.targetHandle) {
  //   console.warn('不能将同一个 handle 连接到自己:', connection)
  //   return false
  // }
  
  // // 验证节点是否存在
  // const sourceNode = nodes.value.find(n => n.id === connection.source)
  // const targetNode = nodes.value.find(n => n.id === connection.target)
  
  // if (!sourceNode || !targetNode) {
  //   console.warn('源节点或目标节点不存在:', { 
  //     sourceNode: sourceNode?.id, 
  //     targetNode: targetNode?.id,
  //     sourceId: connection.source,
  //     targetId: connection.target
  //   })
  //   return false
  // }
  
  // // 检查是否已存在相同的边（包括相同的 sourceHandle 和 targetHandle）
  // const existingEdge = edges.value.find(
  //   e => e.source === connection.source && 
  //        e.target === connection.target &&
  //        (e.sourceHandle === connection.sourceHandle || !connection.sourceHandle) &&
  //        (e.targetHandle === connection.targetHandle || !connection.targetHandle)
  // )
  
  // if (existingEdge) {
  //   console.log('边已存在，阻止重复连接:', existingEdge)
  //   return false
  // }
  
  // console.log('连接验证通过，允许连接:', {
  //   source: connection.source,
  //   target: connection.target,
  //   sourceHandle: connection.sourceHandle,
  //   targetHandle: connection.targetHandle
  // })
  
  // // 返回 true 或 undefined 允许连接
  return true
})


function handleNodeClick({ node }: { node: any }) {
  // 显示侧边栏编辑节点
  selectedNodeId.value = node.id
  console.log('节点被点击:', node)
}

// 点击画布空白处关闭侧边栏
function handlePaneClick() {
  selectedNodeId.value = null
}

function restoreFromStorage() {
  const savedData = localStorage.getItem(FLOW_STORAGE_KEY)
  if (savedData) {
    const flowData = JSON.parse(savedData)

    fromObject(flowData)
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
  const centerX = dimensions.value?.width ? dimensions.value.width / 2 : 400
  const centerY = dimensions.value?.height ? dimensions.value.height / 2 : 300

  // 根据节点类型创建对应的默认数据
  let nodeData: any = {
    name: nodeTypeOptions.find(opt => opt.type === nodeType)?.label || '新节点',
    output: {}
  }

  // 根据不同类型设置不同的默认数据
  switch (nodeType) {
    case 'llm':
      nodeData = {
        name: 'LLM节点',
        agent_uuid: 'agent-' + Date.now(),
        input: {},
        prompt: '请输入提示词',
        temperature: 0.7,
        max_tokens: 2000,
        output: {
          answer: 'str',
          reasoning: 'str'
        }
      }
      break
    case 'http':
      nodeData = {
        name: 'HTTP请求',
        url: 'https://api.example.com/data',
        method: 'GET',
        headers: {},
        body: {},
        output: {
          code: 'int',
          msg: 'str',
          data: 'obj'
        }
      }
      break
    case 'knowledge':
      nodeData = {
        name: '知识库检索',
        knowledge_base_id: 1,
        query: '请输入查询内容',
        top_k: 5,
        similarity_threshold: 0.7,
        output: {
          documents: 'arr',
          scores: 'arr'
        }
      }
      break
    case 'intent':
      nodeData = {
        name: '意图识别',
        input: '用户输入的文本',
        intent_categories: ['查询', '投诉', '建议', '其他'],
        recognition_method: 'llm',
        agent_uuid: 'agent-' + Date.now(),
        output: {
          intent: 'str',
          confidence: 'num'
        }
      }
      break
    case 'string':
      nodeData = {
        name: '字符串处理',
        operation: 'concat',
        input_string: 'Hello',
        parameters: {},
        output: {
          result: 'str'
        }
      }
      break
  }

  // 创建新节点对象
  const newNode = {
    id: newNodeId,
    type: nodeType as any,
    position: {
      x: centerX + (Math.random() - 0.5) * 200,
      y: centerY + (Math.random() - 0.5) * 200
    },
    data: nodeData
  }

  addNodes([newNode])
  closeNodeTypeDialog()
  console.log('已创建新节点:', newNodeId, '类型:', nodeType, '节点数据:', newNode)
  console.log('当前节点总数:', nodes.value.length)
}

function saveToStorage() {
  const flowData = toObject()
  console.log('保存数据:', flowData)
  localStorage.setItem(FLOW_STORAGE_KEY, JSON.stringify(flowData))
  console.log('已保存到 localStorage，节点数:', flowData.nodes?.length || 0, '边数:', flowData.edges?.length || 0)
}

function clearStorage() {
  localStorage.removeItem(FLOW_STORAGE_KEY)
  alert('已清除本地保存')
}

/**
 * toObject transforms your current graph data to an easily persist-able object
 */
function logToObject() {
  console.log(toObject())
}

/**
 * Resets the current viewport transformation (zoom & pan)
 */
function resetTransform() {
  setViewport({ x: 0, y: 0, zoom: 1 })
}


// function closeSidebar() {
//   selectedNodeId.value = null
// }

// 加载工作流详情
const loadWorkflow = async () => {
  if (!workflowId.value) return
  
  loading.value = true
  // try {
  //   workflow.value = await workflowApi.getDetail(workflowId.value as string)
  //   console.log('workflow.value', workflow.value)
  //   workflowName.value = workflow.value.name
    
  //   // 将工作流数据转换为 VueFlow 的 nodes  and edges
  //   // 使用 nextTick 确保在 VueFlow 初始化后再设置数据
  //   await nextTick()
  //   if (workflow.value.nodes && workflow.value.edges) {
  //     nodes.value = (workflow.value.nodes as any[]).map(nodeToGraphNode) as any[]
  //     edges.value = (workflow.value.edges as any[]).map(workflowEdgeToGraphEdge) as any[]
  //   }
  // } catch (error) {
  //   console.error('加载工作流详情失败:', error)
  //   alert('加载工作流详情失败')
  // } finally {
  //   loading.value = false
  // }
}

// 保存工作流（包括节点和边的数据）
const saveWorkflow = async () => {
  if (!workflowId.value) return
  
  try {
    // 将 VueFlow 的 nodes 和 edges 转换为业务层格式
    const workflowNodes = nodes.value.map(graphNodeToNode)
    const workflowEdges = edges.value.map(graphEdgeToWorkflowEdge)
    
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

// 执行工作流
const executeWorkflow = async () => {
  if (!workflowId.value) return
  
  try {
    const result = await workflowApi.execute(workflowId.value as string, {})
    console.log('工作流执行结果:', result)
    alert('工作流执行成功！查看控制台查看结果。')
  } catch (error: any) {
    console.error('执行工作流失败:', error)
    alert('执行失败: ' + (error?.message || '未知错误'))
  }
}

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
        :nodeTypes="nodeTypes" 
        class="basic-flow"
        :default-viewport="{ zoom: 1.5 }" 
        :min-zoom="0.2" 
        :max-zoom="4" 
        @node-click="handleNodeClick"
        @pane-click="handlePaneClick"
        :class="{ 'with-sidebar': selectedNodeId }"
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

    <!-- 节点编辑侧边栏 -->
    <!-- <NodeEditorSidebar 
      v-if="selectedNodeId" 
      :nodeId="selectedNodeId" 
      @close="closeSidebar" 
    /> -->
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
  margin-right: 400px;
  transition: margin-right 0.3s ease;
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