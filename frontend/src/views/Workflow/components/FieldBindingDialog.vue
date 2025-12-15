<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Node, WorkflowEdge, FieldBinding } from '@/types/workflow'
import { getNodeInputFields, getNodeOutputFields, bindingToVariable } from '@/utils/workflow.utils'

interface Props {
  node: Node
  allNodes: Node[]
  edges: WorkflowEdge[]
  visible: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'update:bindings', bindings: FieldBinding[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 当前节点的输入字段
const inputFields = computed(() => getNodeInputFields(props.node.type))

// 获取上游节点（通过 edges 连接到当前节点的节点）
const upstreamNodes = computed(() => {
  const upstreamNodeIds = props.edges
    .filter(edge => edge.target === props.node.id)
    .map(edge => edge.source)
  
  return props.allNodes.filter(node => upstreamNodeIds.includes(node.id))
})

// 字段绑定配置：每个输入字段对应的绑定
const fieldBindings = ref<Record<string, { sourceNodeId: string; sourceField: string } | null>>({})

// 初始化绑定配置：从 edges 中查找已有的绑定
watch(() => [props.node, props.edges], ([node, edges]) => {
  if (!node) return
  
  const bindings: Record<string, { sourceNodeId: string; sourceField: string } | null> = {}
  
  // 初始化所有字段为 null
  inputFields.value.forEach(field => {
    bindings[field.name] = null
  })
  
  // 从连接到当前节点的 edges 中查找绑定
  edges
    .filter(edge => edge.target === node.id && edge.bindings)
    .forEach(edge => {
      edge.bindings?.forEach(binding => {
        if (binding.targetField) {
          bindings[binding.targetField] = {
            sourceNodeId: binding.sourceNodeId,
            sourceField: binding.sourceField,
          }
        }
      })
    })
  
  fieldBindings.value = bindings
}, { immediate: true, deep: true })

// 获取指定节点的输出字段
const getOutputFields = (nodeId: string) => {
  const node = props.allNodes.find(n => n.id === nodeId)
  if (!node) return []
  return getNodeOutputFields(node.type)
}

// 获取可用的上游节点选项（包含输出字段的节点）
const getAvailableSources = (fieldName: string) => {
  return upstreamNodes.value.map(node => ({
    node,
    outputFields: getNodeOutputFields(node.type),
  })).filter(item => item.outputFields.length > 0)
}

// 应用绑定
const applyBindings = () => {
  const bindings: FieldBinding[] = []
  
  Object.entries(fieldBindings.value).forEach(([targetField, binding]) => {
    if (binding) {
      bindings.push({
        sourceNodeId: binding.sourceNodeId,
        sourceField: binding.sourceField,
        targetField,
      })
    }
  })
  
  emit('update:bindings', bindings)
  emit('update:visible', false)
}

// 取消
const cancel = () => {
  emit('update:visible', false)
}
</script>

<template>
  <div v-if="visible" class="field-binding-dialog-overlay" @click.self="cancel">
    <div class="field-binding-dialog">
      <div class="dialog-header">
        <h3>配置字段绑定 - {{ node.id }}</h3>
        <button class="close-btn" @click="cancel">×</button>
      </div>
      
      <div class="dialog-content">
        <div v-if="inputFields.length === 0" class="no-fields">
          该节点没有可绑定的输入字段
        </div>
        
        <div v-else class="fields-list">
          <div
            v-for="field in inputFields"
            :key="field.name"
            class="field-item"
          >
            <div class="field-label">
              <span class="field-name">{{ field.label }}</span>
              <span v-if="field.required" class="required">*</span>
              <span v-if="field.description" class="field-desc">{{ field.description }}</span>
            </div>
            
            <div class="binding-config">
              <select
                :value="fieldBindings[field.name] ? JSON.stringify(fieldBindings[field.name]) : ''"
                class="binding-select"
                @change="(e) => {
                  const value = (e.target as HTMLSelectElement).value
                  fieldBindings[field.name] = value ? JSON.parse(value) : null
                }"
              >
                <option :value="null">不使用绑定（手动输入）</option>
                <optgroup
                  v-for="source in getAvailableSources(field.name)"
                  :key="source.node.id"
                  :label="`节点 ${source.node.id}`"
                >
                  <option
                    v-for="outputField in source.outputFields"
                    :key="outputField.name"
                    :value="JSON.stringify({ sourceNodeId: source.node.id, sourceField: outputField.name })"
                  >
                    {{ outputField.label }} ({{ outputField.name }})
                  </option>
                </optgroup>
              </select>
              
              <div v-if="fieldBindings[field.name]" class="binding-preview">
                将绑定到: {{ bindingToVariable(fieldBindings[field.name]!) }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="dialog-footer">
        <button class="btn btn-secondary" @click="cancel">取消</button>
        <button class="btn btn-primary" @click="applyBindings">应用</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.field-binding-dialog-overlay {
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
}

.field-binding-dialog {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dialog-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.dialog-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.no-fields {
  text-align: center;
  color: #6b7280;
  padding: 40px 20px;
}

.fields-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-name {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.required {
  color: #ef4444;
  font-size: 14px;
}

.field-desc {
  color: #6b7280;
  font-size: 12px;
}

.binding-config {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.binding-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  color: #1f2937;
  cursor: pointer;
}

.binding-select:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.binding-preview {
  font-size: 12px;
  color: #059669;
  padding: 4px 8px;
  background: #d1fae5;
  border-radius: 4px;
}

.dialog-footer {
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
}
</style>

