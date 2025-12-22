<script setup lang="ts">
import { computed } from 'vue'
import type { NodeProps } from '@vue-flow/core'
import { Handle, Position } from '@vue-flow/core'
import type { NodeConfig } from '@/types/workflow'
import NodeCard from './NodeCard.vue'

interface CustomEvents {
}

const props = defineProps<NodeProps<NodeConfig, CustomEvents>>()

// 判断是否需要显示输入/输出 Handle
const showInputHandle = computed(() => props.type !== 'start')
const showOutputHandle = computed(() => props.type !== 'end')

// 获取节点样式类
const nodeClass = computed(() => {
  return `custom-node custom-node--${props.type || 'default'}`
})
</script>

<template>
  <div :class="nodeClass">
    <Handle 
      v-if="showInputHandle" 
      id="target" 
      type="target" 
      :position="Position.Left"
      :is-connectable="true"
    />

    <NodeCard :node="props" />

    <Handle 
      v-if="showOutputHandle" 
      id="source" 
      type="source" 
      :position="Position.Right"
      :is-connectable="true"
    />
  </div>
</template>

<style scoped>
.custom-node {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1.5px solid #e1e8ed;
  border-radius: 8px;
  padding: 10px;
  min-width: 140px;
  font-size: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
  /* 只过渡 box-shadow 和 border-color，完全避免 transform 导致的模糊 */
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}

.custom-node:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.08);
  border-color: #cbd5e0;
}


/* 不同节点类型的样式 */
.custom-node--start {
  border-color: #4caf50;
  background: linear-gradient(135deg, #f1f8f4 0%, #ffffff 100%);
  border-left: 3px solid #4caf50;
}

.custom-node--start:hover {
  border-color: #45a049;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15), 0 2px 4px rgba(0, 0, 0, 0.08);
}

.custom-node--end {
  border-color: #f44336;
  background: linear-gradient(135deg, #fef5f5 0%, #ffffff 100%);
  border-left: 3px solid #f44336;
}

.custom-node--end:hover {
  border-color: #e53935;
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.15), 0 2px 4px rgba(0, 0, 0, 0.08);
}

.custom-node--llm {
  border-color: #2196f3;
  background: linear-gradient(135deg, #f3f8ff 0%, #ffffff 100%);
  border-left: 3px solid #2196f3;
}

.custom-node--llm:hover {
  border-color: #1976d2;
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15), 0 2px 4px rgba(0, 0, 0, 0.08);
}

.custom-node--http {
  border-color: #ff9800;
  background: linear-gradient(135deg, #fff8f0 0%, #ffffff 100%);
  border-left: 3px solid #ff9800;
}

.custom-node--http:hover {
  border-color: #f57c00;
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.08);
}

.custom-node--knowledge {
  border-color: #9c27b0;
  background: linear-gradient(135deg, #faf5fc 0%, #ffffff 100%);
  border-left: 3px solid #9c27b0;
}

.custom-node--knowledge:hover {
  border-color: #7b1fa2;
  box-shadow: 0 4px 12px rgba(156, 39, 176, 0.15), 0 2px 4px rgba(0, 0, 0, 0.08);
}

.custom-node--intent {
  border-color: #00bcd4;
  background: linear-gradient(135deg, #f0fcfe 0%, #ffffff 100%);
  border-left: 3px solid #00bcd4;
}

.custom-node--intent:hover {
  border-color: #0097a7;
  box-shadow: 0 4px 12px rgba(0, 188, 212, 0.15), 0 2px 4px rgba(0, 0, 0, 0.08);
}

.custom-node--string {
  border-color: #607d8b;
  background: linear-gradient(135deg, #f5f7f8 0%, #ffffff 100%);
  border-left: 3px solid #607d8b;
}

.custom-node--string:hover {
  border-color: #455a64;
  box-shadow: 0 4px 12px rgba(96, 125, 139, 0.15), 0 2px 4px rgba(0, 0, 0, 0.08);
}
</style>