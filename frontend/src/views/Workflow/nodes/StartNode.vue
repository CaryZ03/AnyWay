<script setup lang="ts">
import type { NodeProps } from '@vue-flow/core'
import { Handle, Position } from '@vue-flow/core'
import type { StartNodeConfig } from '@/types/workflow'

const props = defineProps<NodeProps<StartNodeConfig, any>>()
</script>

<template>
  <div class="start-node">
    <Handle type="target" :position="Position.Left" />

    <div class="content">
      {{ props.data.input_text }}
    </div>

    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<style scoped>
.start-node {
  background: white;
  border: 1px solid #dcdcdc;
  border-radius: 6px;
  padding: 10px;
  min-width: 120px;
  text-align: center;
  font-size: 12px;
}
</style>