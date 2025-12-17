<script setup lang="ts">
import { computed, defineComponent, h } from 'vue'
import { useVueFlow } from '@vue-flow/core'

interface Props {
  nodeId: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const { nodes, updateNodeData } = useVueFlow()

// 当前选中的节点
const currentNode = computed(() => {
  if (!props.nodeId) return null
  return nodes.value.find(n => n.id === props.nodeId) || null
})

// 节点的数据
const nodeData = computed(() => {
  return currentNode.value?.data || {}
})

// 更新节点数据的函数
function updateField(path: string[], value: any) {
  if (!props.nodeId) return
  
  // 深拷贝当前数据
  const newData = JSON.parse(JSON.stringify(nodeData.value))
  
  // 根据路径更新嵌套对象
  let current: any = newData
  for (let i = 0; i < path.length - 1; i++) {
    const key = path[i]
    if (!key || !(key in current) || typeof current[key] !== 'object' || current[key] === null || Array.isArray(current[key])) {
      if (key) {
        current[key] = {}
      }
    }
    if (key) {
      current = current[key]
    }
  }
  
  // 设置最终值
  const finalKey = path[path.length - 1]
  if (finalKey) {
    current[finalKey] = value
  }
  
  // 更新节点数据
  updateNodeData(props.nodeId, newData)
}

// 获取字段的显示名称
function getFieldLabel(key: string): string {
  const labelMap: Record<string, string> = {
    name: '名称',
    agent_uuid: '智能体UUID',
    input: '输入',
    prompt: '提示词',
    temperature: '温度',
    max_tokens: '最大Token数',
    url: 'URL',
    method: '请求方法',
    headers: '请求头',
    body: '请求体',
    knowledge_base_id: '知识库ID',
    query: '查询内容',
    top_k: 'Top K',
    similarity_threshold: '相似度阈值',
    intent_categories: '意图类别',
    recognition_method: '识别方法',
    operation: '操作',
    input_string: '输入字符串',
    parameters: '参数',
    output: '输出',
    input_text: '输入文本',
    output_text: '输出文本'
  }
  return labelMap[key] || key
}

// 字段行组件（递归）
const FieldRow: any = defineComponent({
  name: 'FieldRow',
  props: {
    label: { type: String, required: true },
    value: { type: null, required: true },
    path: { type: Array as () => string[], required: true },
    updateField: { type: Function, required: true }
  },
  setup(props: any) {
    function isObject(value: any): boolean {
      return value !== null && typeof value === 'object' && !Array.isArray(value)
    }
    
    function isArray(value: any): boolean {
      return Array.isArray(value)
    }
    
    function isSimpleType(value: any): boolean {
      const type = typeof value
      return type === 'string' || type === 'number' || type === 'boolean' || value === null || value === undefined
    }
    
    function getInputType(value: any): string {
      if (typeof value === 'number') return 'number'
      if (typeof value === 'boolean') return 'checkbox'
      return 'text'
    }
    
    function handleInput(event: Event) {
      const target = event.target as HTMLInputElement
      let value: any = target.value
      
      if (typeof props.value === 'number') {
        value = parseFloat(value) || 0
      } else if (typeof props.value === 'boolean') {
        value = target.checked
      }
      
      props.updateField(props.path, value)
    }
    
    return () => {
      // 简单类型：直接显示输入框
      if (isSimpleType(props.value)) {
        return h('div', { class: 'field-row' }, [
          h('div', { class: 'field-label' }, props.label),
          h('div', { class: 'field-value' }, [
            h('input', {
              type: getInputType(props.value),
              value: props.value,
              checked: props.value === true,
              class: 'field-input',
              onInput: handleInput,
              onChange: handleInput
            })
          ])
        ])
      }
      
      // 对象类型：递归渲染
      if (isObject(props.value)) {
        return h('div', { class: 'field-row nested' }, [
          h('div', { class: 'field-label' }, props.label),
          h('div', { class: 'field-value nested-object' }, 
            Object.entries(props.value).map(([key, val]) => 
              h(FieldRow, {
                key,
                label: key,
                value: val,
                path: [...props.path, key],
                updateField: props.updateField
              })
            )
          )
        ])
      }
      
      // 数组类型：显示数组项
      if (isArray(props.value)) {
        return h('div', { class: 'field-row nested' }, [
          h('div', { class: 'field-label' }, props.label),
          h('div', { class: 'field-value nested-array' },
            (props.value as any[]).map((item: any, index: number) =>
              h('div', { key: index, class: 'array-item' }, [
                h(FieldRow, {
                  label: `[${index}]`,
                  value: item,
                  path: [...props.path, String(index)],
                  updateField: props.updateField
                })
              ])
            )
          )
        ])
      }
      
      return null
    }
  }
})
</script>

<template>
  <div v-if="currentNode" class="node-editor-sidebar">
    <div class="sidebar-header">
      <h3>编辑节点: {{ nodeData.name || currentNode.id }}</h3>
      <button class="close-btn" @click="emit('close')">×</button>
    </div>
    
    <div class="sidebar-content">
      <!-- 递归渲染字段 -->
      <FieldRow
        v-for="(value, key) in nodeData"
        :key="String(key)"
        :label="getFieldLabel(String(key))"
        :value="value"
        :path="[String(key)]"
        :updateField="updateField"
      />
    </div>
  </div>
</template>

<style scoped>
.node-editor-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e1e8ed;
  flex-shrink: 0;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.close-btn {
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

.close-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.field-row {
  margin-bottom: 16px;
}

.field-row.nested {
  margin-left: 16px;
  padding-left: 16px;
  border-left: 2px solid #e1e8ed;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: #666;
  margin-bottom: 8px;
}

.field-value {
  margin-left: 0;
}

.field-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d0d7de;
  border-radius: 4px;
  font-size: 14px;
  color: #1a1a1a;
  transition: border-color 0.2s;
}

.field-input:focus {
  outline: none;
  border-color: #0969da;
  box-shadow: 0 0 0 3px rgba(9, 105, 218, 0.1);
}

.nested-object {
  margin-top: 8px;
}

.nested-array {
  margin-top: 8px;
}

.array-item {
  margin-bottom: 12px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>