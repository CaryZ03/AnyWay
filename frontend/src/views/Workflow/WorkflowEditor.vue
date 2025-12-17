<script setup lang="ts">
import { ref, markRaw } from 'vue'
import { VueFlow, useVueFlow, Panel } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { ControlButton, Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { initialEdges, initialNodes } from './initial-elements'
import Icon from './components/Icon.vue'
// import NodeEditorSidebar from './components/NodeEditorSidebar.vue'
import type { Connection } from '@vue-flow/core'
import { CustomNode } from './nodes'

// 导入 Vue Flow 的样式
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

interface Props {
  id: string
}

const props = defineProps<Props>()


// localStorage 的 key
const FLOW_STORAGE_KEY = 'workflow-editor-flow'

const {
  onInit,
  addNodes,
  setViewport,
  toObject,
  fromObject,
  dimensions,
  nodes,
  edges
} = useVueFlow()

nodes.value = initialNodes

console.log('initialNodes', initialNodes)
console.log('initialEdges', initialEdges)
edges.value = initialEdges

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

onInit((vueFlowInstance) => {
  // instance is the same as the return of `useVueFlow`
  vueFlowInstance.fitView()
})


function handleNodeClick({ node }: { node: any }) {
  // 显示侧边栏编辑节点
  selectedNodeId.value = node.id
  console.log('节点被点击:', node)
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

function handleConnect(connection: Connection) {
  console.log('连接:', connection)
}

// function closeSidebar() {
//   selectedNodeId.value = null
// }

</script>

<template>
  <div class="workflow-editor">
    <VueFlow v-model:nodes="nodes" v-model:edges="edges" :nodeTypes="nodeTypes" class="basic-flow"
      :default-viewport="{ zoom: 1.5 }" :min-zoom="0.2" :max-zoom="4" @node-click="handleNodeClick"
      @connect="handleConnect">
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
    <!-- <NodeEditorSidebar :nodeId="selectedNodeId" @close="closeSidebar" /> -->
  </div>
</template>

<!-- 组件特定样式 -->
<style scoped>
.basic-flow {
  width: 100%;
  height: 100vh;
  min-height: 600px;
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