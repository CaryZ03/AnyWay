<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { pluginApi } from '@/api'
import type { Plugin, OpenAPISpec, Operation, PathItem } from '@/types/plugin'

const router = useRouter()
const route = useRoute()

const plugin = ref<Plugin | null>(null)
const loading = ref(false)
const openapiSpec = ref<OpenAPISpec | null>(null)

// 提取所有工具
interface ToolInfo {
  path: string
  method: string
  operation: Operation
  operationId: string
}

const tools = computed<ToolInfo[]>(() => {
  if (!openapiSpec.value || !openapiSpec.value.paths) return []
  
  const toolList: ToolInfo[] = []
  const methods = ['get', 'post'] as const
  
  for (const [path, pathItem] of Object.entries(openapiSpec.value.paths)) {
    for (const method of methods) {
      const operation = (pathItem as PathItem)[method]
      if (operation && operation.operationId) {
        toolList.push({
          path,
          method: method.toUpperCase(),
          operation,
          operationId: operation.operationId
        })
      }
    }
  }
  
  return toolList
})

// 加载插件详情
const loadPlugin = async () => {
  const id = Number(route.params.id)
  if (!id) {
    router.push('/')
    return
  }

  loading.value = true
  try {
    const data = await pluginApi.getDetail(id)
    plugin.value = data
    
    // 解析 openapiSpec
    if (data.openapiSpec) {
    if (typeof data.openapiSpec === 'string') {
      openapiSpec.value = JSON.parse(data.openapiSpec)
    } else {
      openapiSpec.value = data.openapiSpec
      }
    } else {
      openapiSpec.value = null
    }
  } catch (error) {
    console.error('加载插件详情失败:', error)
    alert('加载插件详情失败')
    router.push('/')
  } finally {
    loading.value = false
  }
}

// 返回主页
const handleBack = () => {
  router.push('/')
}

// 编辑插件
const handleEdit = () => {
  // 编辑功能暂时不实现，或者可以打开编辑对话框
  // 如果需要编辑，可以在这里打开编辑对话框
  console.log('编辑插件:', plugin.value)
}

// 获取方法的颜色
const getMethodColor = (method: string) => {
  const colors: Record<string, string> = {
    GET: '#10b981',
    POST: '#3b82f6'
  }
  return colors[method] || '#6b7280'
}

onMounted(() => {
  loadPlugin()
})
</script>

<template>
  <div class="plugin-detail-page">
    <!-- 顶部导航栏 -->
    <header class="page-header">
      <button class="back-btn" @click="handleBack">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回
      </button>
      <div class="header-content">
        <h1 class="page-title">{{ plugin?.name || '插件详情' }}</h1>
        <p v-if="plugin?.description" class="page-subtitle">{{ plugin.description }}</p>
      </div>
      <button class="edit-btn" @click="handleEdit" v-if="plugin">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M11.333 2a1.414 1.414 0 0 1 2 2L4.667 13l-3.334 1L2.333 10.667L11.333 2Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        编辑
      </button>
    </header>

    <!-- 内容区域 -->
    <div class="page-content">
      <div v-if="loading" class="loading-state">
        <div class="loading-text">加载中...</div>
      </div>

      <div v-else-if="!plugin" class="empty-state">
        <div class="empty-icon">🔌</div>
        <h3 class="empty-title">插件不存在</h3>
        <button class="empty-action-btn" @click="handleBack">返回列表</button>
      </div>

      <div v-else class="detail-content">
        <!-- 插件基本信息 -->
        <div class="info-section">
          <div class="info-item">
            <span class="info-label">状态：</span>
            <span class="status-badge" :class="plugin.status">
              {{ plugin.status === 'enabled' ? '已启用' : '已禁用' }}
            </span>
          </div>
          <div class="info-item" v-if="openapiSpec?.info?.version">
            <span class="info-label">版本：</span>
            <span class="info-value">{{ openapiSpec.info.version }}</span>
          </div>
          <div class="info-item" v-if="openapiSpec?.servers?.[0]?.url">
            <span class="info-label">服务器地址：</span>
            <span class="info-value">{{ openapiSpec.servers[0].url }}</span>
          </div>
        </div>

        <!-- 工具列表 -->
        <div class="tools-section">
          <div class="section-header">
            <h2 class="section-title">工具列表</h2>
            <span class="tool-count">{{ tools.length }} 个工具</span>
          </div>

          <div v-if="tools.length === 0" class="empty-tools">
            <p>该插件暂无可用工具</p>
          </div>

          <div v-else class="tools-list">
            <div
              v-for="(tool, index) in tools"
              :key="`${tool.path}-${tool.method}-${index}`"
              class="tool-item"
            >
              <div class="tool-header">
                <div class="tool-method" :style="{ backgroundColor: getMethodColor(tool.method) }">
                  {{ tool.method }}
                </div>
                <div class="tool-info">
                  <div class="tool-name">{{ tool.operationId }}</div>
                  <div class="tool-path">{{ tool.path }}</div>
                </div>
              </div>
              <div v-if="tool.operation.summary || tool.operation.description" class="tool-description">
                <div v-if="tool.operation.summary" class="tool-summary">
                  <strong>摘要：</strong>{{ tool.operation.summary }}
                </div>
                <div v-if="tool.operation.description" class="tool-desc">
                  {{ tool.operation.description }}
                </div>
              </div>
              <div v-if="tool.operation.parameters && tool.operation.parameters.length > 0" class="tool-parameters">
                <div class="params-title">参数：</div>
                <div class="params-list">
                  <div
                    v-for="param in tool.operation.parameters"
                    :key="param.name"
                    class="param-item"
                  >
                    <span class="param-name">{{ param.name }}</span>
                    <span class="param-in">{{ param.in }}</span>
                    <span class="param-type">{{ param.schema?.type || 'string' }}</span>
                    <span v-if="param.required" class="param-required">必填</span>
                    <span v-else class="param-optional">可选</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.plugin-detail-page {
  min-height: 100vh;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
}

.page-header {
  background: white;
  padding: 24px 32px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 24px;
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
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.edit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
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

.edit-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.page-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.loading-text {
  color: #9ca3af;
  font-size: 14px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 24px 0;
}

.empty-action-btn {
  padding: 10px 20px;
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.empty-action-btn:hover {
  background: #1d4ed8;
}

.detail-content {
  max-width: 1200px;
  margin: 0 auto;
}

.info-section {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 24px;
  border: 1px solid #e5e7eb;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #1f2937;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.enabled {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.disabled {
  background: #fee2e2;
  color: #991b1b;
}

.tools-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e5e7eb;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.tool-count {
  font-size: 14px;
  color: #6b7280;
}

.empty-tools {
  padding: 40px 20px;
  text-align: center;
  color: #9ca3af;
}

.tools-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tool-item {
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
}

.tool-item:hover {
  border-color: #2563eb;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
}

.tool-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.tool-method {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  min-width: 50px;
  text-align: center;
  flex-shrink: 0;
}

.tool-info {
  flex: 1;
  min-width: 0;
}

.tool-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
  word-break: break-word;
}

.tool-path {
  font-size: 13px;
  color: #6b7280;
  font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  word-break: break-all;
}

.tool-description {
  margin-bottom: 12px;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.tool-summary {
  font-size: 14px;
  color: #374151;
  margin-bottom: 8px;
  line-height: 1.6;
}

.tool-summary strong {
  color: #1f2937;
  font-weight: 600;
}

.tool-desc {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
}

.tool-parameters {
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.params-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.params-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: #f9fafb;
  border-radius: 6px;
  font-size: 13px;
}

.param-name {
  font-weight: 500;
  color: #1f2937;
  font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.param-in {
  padding: 2px 6px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.param-type {
  padding: 2px 6px;
  background: #e5e7eb;
  border-radius: 4px;
  color: #6b7280;
  font-size: 11px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.param-required {
  padding: 2px 6px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.param-optional {
  padding: 2px 6px;
  background: #d1fae5;
  color: #065f46;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}
</style>

