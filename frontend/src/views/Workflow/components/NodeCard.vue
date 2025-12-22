<script setup lang="ts">
import { computed } from 'vue'
import type { NodeProps } from '@vue-flow/core'
import type { NodeConfig } from '@/types/workflow'

interface CustomEvents {
}

// 接收从 CustomNode 传入的 node props
const props = defineProps<{
  node: NodeProps<NodeConfig, CustomEvents>
}>()

const isOperationNode = computed(() => props.node.type !== 'start' && props.node.type !== 'end')

const nodeIcon = computed(() => {
  const iconMap: Record<string, string> = {
    start: '🏁',
    end: '🏁',
    llm: '🤖',
    http: '🌐',
    knowledge: '🔍',
    intent: '🎯',
    string: '🔤',
  }
  return iconMap[props.node.type || 'custom'] || '💀'
})

// 根据节点类型获取显示标签
const nodeLabel = computed(() => {
  // const typeMap: Record<string, string> = {
  //   start: '开始',
  //   end: '结束',
  //   llm: 'LLM',
  //   http: 'HTTP',
  //   knowledge: '知识库',
  //   intent: '意图识别',
  //   string: '字符串处理',
  // }
  // return typeMap[props.node.type || 'custom'] || '节点'
  return props.node.data.name || '节点'
})

// 根据节点类型获取显示内容
const nodeInputLabels = computed(() => {
  const data = props.node.data
  if (!data) return []

  switch (props.node.type) {
    case 'start':
      return [{ name: "input_text", type: "str", required: true }]
    case 'end':
      return []
    case 'llm':
      return [{ name: "input", type: "obj", required: true }]
    case 'http':
      return [
        { name: "url", type: "str", required: true },
        { name: "method", type: "str", required: true },
        { name: "headers", type: "obj", required: false },
        { name: "body", type: "obj", required: false }
      ]
    case 'knowledge':
      return [
        { name: "query", type: "str", required: true },
        { name: "top_k", type: "int", required: false },
        { name: "similarity_threshold", type: "num", required: false }
      ]
    case 'intent':
      return [{ name: "input", type: "str", required: true }]
    case 'string':
      return [
        { name: "operation", type: "str", required: true },
        { name: "input_string", type: "str", required: true },
        { name: "parameters", type: "obj", required: false }
      ]
    default:
      return []
  }
})

// 根据节点类型获取显示内容
const nodeOutputLabels = computed(() => {
  const nodeType = props.node.type
  if (!nodeType) return []
  
  // 使用固定的输出字段定义
  const outputFields = {
    start: ['input_text'],
    llm: ['response'],
    http: ['status', 'data'],
    knowledge: ['documents'],
    intent: ['intent', 'confidence'],
    string: ['result'],
    end: ['output_text'],
  } as Record<string, string[]>
  
  const fields = outputFields[nodeType] || []
  return fields.map(field => ({ name: field, type: 'any' }))
})

/**
 * 格式化配置值显示
 */
function formatConfigValue(value: any): string {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'string' && value.includes('{') && value.includes('}')) {
    // 如果包含变量替换格式，显示为变量
    return value
  }
  if (typeof value === 'object') {
    if (Array.isArray(value)) {
      return `[${value.length}]`
    }
    return '{...}'
  }
  return String(value)
}

/**
 * 获取节点的额外配置信息
 */
const nodeConfigs = computed(() => {
  const data = props.node.data
  if (!data) return []

  const configs: Array<{ label: string; value: string }> = []

  switch (props.node.type) {
    case 'llm': {
      const llmData = data as any
      if (llmData.agent_uuid) {
        configs.push({ label: '智能体', value: llmData.agent_uuid.slice(0, 8) + '...' })
      }
      if (llmData.prompt) {
        const prompt = typeof llmData.prompt === 'string' 
          ? (llmData.prompt.length > 20 ? llmData.prompt.substring(0, 20) + '...' : llmData.prompt)
          : formatConfigValue(llmData.prompt)
        configs.push({ label: '提示词', value: prompt })
      }
      // 显示输入字段（可能包含变量替换）
      if (llmData.input && typeof llmData.input === 'object') {
        const inputKeys = Object.keys(llmData.input)
        if (inputKeys.length > 0) {
          configs.push({ label: '输入字段', value: `${inputKeys.length}个` })
        }
      }
      if (llmData.temperature !== undefined) {
        configs.push({ label: '温度', value: String(llmData.temperature) })
      }
      if (llmData.max_tokens !== undefined) {
        configs.push({ label: '最大Token', value: String(llmData.max_tokens) })
      }
      break
    }
    case 'http': {
      const httpData = data as any
      if (httpData.url) {
        const url = typeof httpData.url === 'string'
          ? (httpData.url.length > 30 ? httpData.url.substring(0, 30) + '...' : httpData.url)
          : formatConfigValue(httpData.url)
        configs.push({ label: 'URL', value: url })
      }
      // 显示请求体（可能包含变量替换）
      if (httpData.body && typeof httpData.body === 'object') {
        const bodyKeys = Object.keys(httpData.body)
        if (bodyKeys.length > 0) {
          configs.push({ label: '请求体', value: `${bodyKeys.length}个字段` })
        }
      }
      if (httpData.method) {
        configs.push({ label: '方法', value: httpData.method })
      }
      break
    }
    case 'knowledge': {
      const kbData = data as any
      if (kbData.knowledge_base_id !== undefined) {
        configs.push({ label: '知识库ID', value: String(kbData.knowledge_base_id) })
      }
      if (kbData.query) {
        const query = typeof kbData.query === 'string'
          ? (kbData.query.length > 20 ? kbData.query.substring(0, 20) + '...' : kbData.query)
          : formatConfigValue(kbData.query)
        configs.push({ label: '查询', value: query })
      }
      if (kbData.top_k !== undefined) {
        configs.push({ label: 'Top K', value: String(kbData.top_k) })
      }
      if (kbData.similarity_threshold !== undefined) {
        configs.push({ label: '相似度阈值', value: String(kbData.similarity_threshold) })
      }
      break
    }
    case 'intent': {
      const intentData = data as any
      if (intentData.recognition_method) {
        configs.push({ label: '识别方式', value: intentData.recognition_method === 'llm' ? 'LLM' : '关键词' })
      }
      if (intentData.agent_uuid && intentData.recognition_method === 'llm') {
        configs.push({ label: '智能体', value: intentData.agent_uuid.slice(0, 8) + '...' })
      }
      if (intentData.intent_categories && intentData.intent_categories.length > 0) {
        configs.push({ label: '意图类别', value: `${intentData.intent_categories.length}个` })
      }
      if (intentData.keywords && intentData.recognition_method === 'keyword') {
        const keywordCount = Object.keys(intentData.keywords).length
        configs.push({ label: '关键词组', value: `${keywordCount}组` })
      }
      if (intentData.input) {
        const input = typeof intentData.input === 'string'
          ? (intentData.input.length > 20 ? intentData.input.substring(0, 20) + '...' : intentData.input)
          : formatConfigValue(intentData.input)
        configs.push({ label: '输入', value: input })
      }
      break
    }
    case 'string': {
      const stringData = data as any
      if (stringData.operation) {
        const operationMap: Record<string, string> = {
          concat: '拼接',
          replace: '替换',
          substring: '截取',
          format: '格式化',
          trim: '去除空格',
          upper: '转大写',
          lower: '转小写'
        }
        configs.push({ label: '操作', value: operationMap[stringData.operation] || stringData.operation })
      }
      if (stringData.input_string) {
        const inputString = typeof stringData.input_string === 'string'
          ? (stringData.input_string.length > 20 ? stringData.input_string.substring(0, 20) + '...' : stringData.input_string)
          : formatConfigValue(stringData.input_string)
        configs.push({ label: '输入字符串', value: inputString })
      }
      break
    }
    case 'start': {
      // Start 节点通常不需要额外配置
      break
    }
    case 'end': {
      // End 节点通常不需要额外配置
      break
    }
  }

  return configs
})

</script>

<template>
  <div class="node-card">
    <!-- Header -->
    <div class="header">
      <div class="title">
        <span class="icon">{{ nodeIcon }}</span>
        <span>{{ nodeLabel }}</span>
      </div>

      <div v-if="isOperationNode" class="actions">
        <button class="play">▶</button>
        <button class="more">⋯</button>
      </div>
    </div>

    <!-- Body -->
    <div class="section">
      <div v-if="nodeInputLabels.length > 0" class="section-row">
        <span class="row-label">输入</span>
        <span v-for="(v, k) in nodeInputLabels" :key="k" class="field-tag">
          <span class="field-type">{{ v.type == 'obj' ? '{ }' : v.type + '.' }}</span>
          <span class="field-name">{{ v.name }}{{ v.required ? '' : '?' }}</span>
        </span>
      </div>

      <div v-if="nodeOutputLabels.length > 0" class="section-row">
        <span class="row-label">输出</span>
        <span v-for="(v, k) in nodeOutputLabels" :key="k" class="field-tag">
          <span class="field-type">{{ typeof v.type === 'object' ? '{ }' : v.type + '.' }}</span>
          <span class="field-name">{{ v.name }}</span>
        </span>
      </div>

      <!-- 额外配置信息 -->
      <template v-for="(config, index) in nodeConfigs" :key="index">
        <div class="section-row">
          <span class="row-label">{{ config.label }}</span>
          <span class="config-value">{{ config.value }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* NodeCard 容器 */
.node-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

/* Header 样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0;
  margin: 0;
  background: transparent;
}

.title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #1a1a1a;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.icon {
  font-size: 16px;
  line-height: 1;
  filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.1));
}

.actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.actions button {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 12px;
  color: #666;
  border-radius: 4px;
  transition: all 0.2s ease;
  line-height: 1;
}

.actions button:hover {
  background: rgba(0, 0, 0, 0.08);
  color: #1a1a1a;
  transform: scale(1.05);
}

.actions .play {
  font-size: 10px;
}

.actions .more {
  font-size: 16px;
  line-height: 1;
  padding: 0 4px;
}

/* 其他样式 */
.node-header {
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
  padding-bottom: 4px;
  border-bottom: 1px solid #eee;
}

.node-type {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.node-content {
  color: #666;
  font-size: 11px;
  word-break: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

/* Section 样式 */
.section {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 3px;
  padding-top: 10px;
}

.section-row {
  display: flex;
  align-items: center;
  gap: 5px;
  width: 100%;
  flex-wrap: wrap;
}

.row-label {
  display: inline-block;
  font-size: 11px;
  color: #999;
  flex-shrink: 0;
  font-weight: 500;
}

/* 配置值样式 - 简单展示，无背景 */
.config-value {
  display: inline-block;
  font-size: 11px;
  color: #1a1a1a;
  font-weight: 400;
  white-space: nowrap;
}

/* Field Tag 样式 */
.field-tag {
  display: inline-flex;
  align-items: center;
  padding: 0px 2px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border: 1px solid #e1e8ed;
  border-radius: 4px;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.field-tag:hover {
  background: linear-gradient(135deg, #e8ecf1 0%, #dde4ea 100%);
  border-color: #cbd5e0;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.field-type {
  color: #888;
  font-weight: 500;
  font-size: 9px;
  letter-spacing: 0.3px;
}

.field-separator {
  color: #bbb;
  font-weight: 400;
}

.field-name {
  color: #1a1a1a;
  font-weight: 500;
}
</style>