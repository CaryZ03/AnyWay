<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { knowledgeApi } from '@/api'
import type { KnowledgeBase } from '@/types/knowledge-base'
import type { BackendDocument } from '@/types/api'

const router = useRouter()
const route = useRoute()

const knowledgeBaseId = computed(() => Number(route.params.id))
const knowledgeBase = ref<KnowledgeBase | null>(null)
const documents = ref<BackendDocument[]>([])
const loading = ref(false)
const refreshing = ref(false)
const uploading = ref(false)
const showUploadDialog = ref(false)
let refreshInterval: number | null = null

// 加载知识库详情
const loadKnowledgeBase = async () => {
  if (!knowledgeBaseId.value) return

  loading.value = true
  try {
    knowledgeBase.value = await knowledgeApi.getDetail(knowledgeBaseId.value)
  } catch (error) {
    console.error('加载知识库详情失败:', error)
    alert('加载知识库详情失败')
  } finally {
    loading.value = false
  }
}

// 加载文档列表
const loadDocuments = async (showLoading = true) => {
  if (!knowledgeBaseId.value) return

  if (showLoading) {
    loading.value = true
  }
  try {
    documents.value = await knowledgeApi.getDocuments(knowledgeBaseId.value)
    
    // 检查是否有文档在处理中
    const hasProcessingDocs = documents.value.some(doc => 
      doc.status === 'pending' || doc.status === 'processing'
    )
    
    // 如果有文档在处理中，启动自动刷新
    if (hasProcessingDocs && !refreshInterval) {
      startAutoRefresh()
    } else if (!hasProcessingDocs && refreshInterval) {
      stopAutoRefresh()
    }
  } catch (error) {
    console.error('加载文档列表失败:', error)
    if (showLoading) {
      alert('加载文档列表失败')
    }
  } finally {
    if (showLoading) {
      loading.value = false
    }
  }
}

// 手动刷新
const handleRefresh = async () => {
  refreshing.value = true
  try {
    await loadDocuments(false)
    await loadKnowledgeBase()
  } finally {
    refreshing.value = false
  }
}

// 启动自动刷新（每5秒刷新一次）
const startAutoRefresh = () => {
  if (refreshInterval) return
  
  refreshInterval = window.setInterval(() => {
    loadDocuments(false)
    loadKnowledgeBase()
  }, 5000) // 每5秒刷新一次
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// 打开上传对话框
const openUploadDialog = () => {
  showUploadDialog.value = true
}

// 关闭上传对话框
const closeUploadDialog = () => {
  showUploadDialog.value = false
}

// 上传文档
const handleUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !knowledgeBaseId.value) return

  uploading.value = true
  try {
    await knowledgeApi.uploadDocument(knowledgeBaseId.value, file)
    await loadDocuments()
    await loadKnowledgeBase() // 刷新知识库信息（文档数量）
    closeUploadDialog()
    alert('上传成功')
    // 重置文件输入
    if (input) input.value = ''
  } catch (error: any) {
    console.error('上传文档失败:', error)
    alert('上传失败: ' + (error?.message || '未知错误'))
  } finally {
    uploading.value = false
  }
}

// 删除文档
const handleDeleteDocument = async (documentId: number) => {
  if (!confirm('确定要删除这个文档吗？')) return

  try {
    await knowledgeApi.deleteDocument(documentId)
    await loadDocuments()
    await loadKnowledgeBase() // 刷新知识库信息
    alert('删除成功')
  } catch (error: any) {
    console.error('删除文档失败:', error)
    alert('删除失败: ' + (error?.message || '未知错误'))
  }
}

// 返回列表
const handleBack = () => {
  router.push('/')
}

onMounted(() => {
  loadKnowledgeBase()
  loadDocuments()
})

// 组件卸载时停止自动刷新
onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<template>
  <div class="knowledge-base-detail">
    <!-- 顶部导航栏 -->
    <header class="detail-header">
      <button class="back-btn" @click="handleBack">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12.5 15L7.5 10L12.5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回
      </button>
      <div class="header-center">
        <h1 class="detail-title">{{ knowledgeBase?.name || '加载中...' }}</h1>
        <p v-if="knowledgeBase?.description" class="detail-description">{{ knowledgeBase.description }}</p>
      </div>
      <div class="header-actions">
        <button 
          class="btn-secondary" 
          @click="handleRefresh"
          :disabled="refreshing"
          title="刷新"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" :class="{ spinning: refreshing }">
            <path d="M13.333 2.667v4h-4M2.667 13.333v-4h4M11.515 4.485A5.333 5.333 0 1 0 4.485 11.515" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ refreshing ? '刷新中...' : '刷新' }}
        </button>
        <button class="btn-primary" @click="openUploadDialog">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 2v8M5 7l3-3 3 3M2 12h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          上传文档
        </button>
      </div>
    </header>

    <!-- 内容区域 -->
    <div class="detail-content">
      <div v-if="loading && documents.length === 0" class="loading-state">
        <div class="loading-text">加载中...</div>
      </div>
      <div v-else-if="documents.length === 0" class="empty-state">
        <div class="empty-icon">📄</div>
        <h3 class="empty-title">还没有文档</h3>
        <p class="empty-desc">上传文档到知识库，开始构建你的知识体系</p>
        <button class="btn-primary" @click="openUploadDialog">上传文档</button>
      </div>
      <div v-else class="documents-list">
        <div
          v-for="doc in documents"
          :key="doc.id"
          class="document-card"
        >
          <div class="document-icon">📄</div>
          <div class="document-info">
            <h3 class="document-name">{{ doc.filename }}</h3>
            <div class="document-meta">
              <span class="meta-item">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                  <path d="M2 4h12M6 4V2.667A1.333 1.333 0 0 1 7.333 2h1.334A1.333 1.333 0 0 1 10 2.667V4m2 0v9.333A1.333 1.333 0 0 1 10.667 14.667H5.333A1.333 1.333 0 0 1 4 13.333V4h8z" stroke="currentColor" stroke-width="1.5"/>
                </svg>
                {{ doc.file_type?.toUpperCase() || 'FILE' }}
              </span>
              <span class="meta-item">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                  <path d="M8 2v8M5 7l3-3 3 3M2 12h12" stroke="currentColor" stroke-width="1.5"/>
                </svg>
                {{ doc.file_size ? (doc.file_size / 1024).toFixed(2) + ' KB' : '未知大小' }}
              </span>
              <span class="meta-item status" :class="doc.status || 'pending'">
                {{ (doc.status || 'pending') === 'completed' ? '已完成' : (doc.status || 'pending') === 'processing' ? '处理中' : (doc.status || 'pending') === 'failed' ? '失败' : '待处理' }}
              </span>
            </div>
            <div v-if="doc.uploaded_at || doc.created_at" class="document-time">
              上传于 {{ new Date(doc.uploaded_at || doc.created_at || '').toLocaleString('zh-CN') }}
            </div>
          </div>
          <div class="document-actions">
            <button
              class="action-btn delete"
              @click="handleDeleteDocument(doc.id!)"
              title="删除"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 4h12M6 4V2.667A1.333 1.333 0 0 1 7.333 2h1.334A1.333 1.333 0 0 1 10 2.667V4m2 0v9.333A1.333 1.333 0 0 1 10.667 14.667H5.333A1.333 1.333 0 0 1 4 13.333V4h8z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <div v-if="showUploadDialog" class="dialog-overlay" @click="closeUploadDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h2>上传文档</h2>
          <button class="dialog-close" @click="closeUploadDialog">×</button>
        </div>
        <div class="dialog-body">
          <div class="upload-area">
            <input
              type="file"
              id="file-input"
              @change="handleUpload"
              :disabled="uploading"
              style="display: none"
            />
            <label for="file-input" class="upload-label" :class="{ uploading }">
              <svg width="48" height="48" viewBox="0 0 16 16" fill="none">
                <path d="M8 2v8M5 7l3-3 3 3M2 12h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <p v-if="!uploading">点击选择文件或拖拽文件到此处</p>
              <p v-else>上传中...</p>
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeUploadDialog" :disabled="uploading">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.knowledge-base-detail {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f9fafb;
}

.detail-header {
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
  z-index: 10;
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
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.header-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.detail-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-primary:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary svg {
  transition: transform 0.3s;
}

.btn-secondary svg.spinning {
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

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
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
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.empty-desc {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 24px 0;
}

.documents-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.document-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: all 0.2s;
}

.document-card:hover {
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
}

.document-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.document-info {
  flex: 1;
  min-width: 0;
}

.document-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.document-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
}

.meta-item.status {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.meta-item.status.completed {
  background: #d1fae5;
  color: #065f46;
}

.meta-item.status.processing {
  background: #dbeafe;
  color: #1e40af;
}

.meta-item.status.failed {
  background: #fee2e2;
  color: #991b1b;
}

.meta-item.status.pending {
  background: #f3f4f6;
  color: #6b7280;
}

.document-time {
  font-size: 12px;
  color: #9ca3af;
}

.document-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #6b7280;
}

.action-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  color: #1f2937;
}

.action-btn.delete:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
}

.dialog-overlay {
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

.dialog-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dialog-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.dialog-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.dialog-close:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.dialog-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #2563eb;
  background: #eff6ff;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  color: #6b7280;
}

.upload-label.uploading {
  cursor: not-allowed;
  opacity: 0.6;
}

.upload-label svg {
  color: #2563eb;
}

.upload-label p {
  margin: 0;
  font-size: 14px;
}

.dialog-footer {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-secondary {
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

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>

