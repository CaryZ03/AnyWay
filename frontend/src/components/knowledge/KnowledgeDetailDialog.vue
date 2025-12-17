<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { KnowledgeBase } from '@/types/knowledge-base'
import type { BackendDocument, SearchResult } from '@/types/api'
import { knowledgeApi } from '@/api'

const props = defineProps<{
  show: boolean
  knowledgeBase?: KnowledgeBase
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'updated'): void
}>()

const documents = ref<BackendDocument[]>([])
const loading = ref(false)
const uploading = ref(false)
const searchLoading = ref(false)
const searchQuery = ref('')
const searchResults = ref<SearchResult[]>([])

const kbTitle = computed(() => props.knowledgeBase?.name || '知识库')

const close = () => emit('close')

const loadDocuments = async () => {
  if (!props.knowledgeBase?.id) return
  loading.value = true
  try {
    documents.value = await knowledgeApi.getDocuments(props.knowledgeBase.id)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleUpload = async (event: Event) => {
  if (!props.knowledgeBase?.id) return
  const files = (event.target as HTMLInputElement).files
  if (!files || files.length === 0) return

  const file = files.item(0)
  if (!file) return
  uploading.value = true
  try {
    await knowledgeApi.uploadDocument(props.knowledgeBase.id, file)
    await loadDocuments()
    emit('updated')
    alert('上传成功，后台处理中')
  } catch (error: any) {
    alert(error?.message || '上传失败')
  } finally {
    uploading.value = false
    ;(event.target as HTMLInputElement).value = ''
  }
}

const handleDelete = async (doc: BackendDocument) => {
  if (!props.knowledgeBase?.id || !doc.id) return
  if (!confirm(`确定删除文档 ${doc.filename} 吗？`)) return

  try {
    await knowledgeApi.deleteDocument(props.knowledgeBase.id, doc.id)
    await loadDocuments()
    emit('updated')
  } catch (error: any) {
    alert(error?.message || '删除失败')
  }
}

const handleSearch = async () => {
  if (!props.knowledgeBase?.id) return
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }

  searchLoading.value = true
  try {
    searchResults.value = await knowledgeApi.search(props.knowledgeBase.id, searchQuery.value, 5)
  } catch (error: any) {
    alert(error?.message || '搜索失败')
  } finally {
    searchLoading.value = false
  }
}

watch(
  () => props.show,
  (visible) => {
    if (visible) {
      loadDocuments()
      searchResults.value = []
      searchQuery.value = ''
    }
  }
)

watch(
  () => props.knowledgeBase?.id,
  () => {
    if (props.show) {
      loadDocuments()
      searchResults.value = []
      searchQuery.value = ''
    }
  }
)
</script>

<template>
  <div v-if="show" class="drawer-backdrop">
    <div class="drawer">
      <div class="drawer-header">
        <div>
          <h3>{{ kbTitle }}</h3>
          <p>管理文档并执行搜索</p>
        </div>
        <button class="close-btn" @click="close">×</button>
      </div>

      <div class="drawer-body">
        <div class="section">
          <div class="section-header">
            <h4>文档列表</h4>
            <label class="upload-btn">
              <input type="file" @change="handleUpload" :disabled="uploading" />
              {{ uploading ? '上传中...' : '上传文档' }}
            </label>
          </div>
          <div v-if="loading" class="hint">加载中...</div>
          <div v-else-if="documents.length === 0" class="hint">暂无文档</div>
          <ul v-else class="doc-list">
            <li v-for="doc in documents" :key="doc.id" class="doc-item">
              <div class="doc-info">
                <div class="doc-name">{{ doc.filename }}</div>
                <div class="doc-meta">{{ doc.file_size }} bytes · 状态：{{ doc.status }}</div>
              </div>
              <button class="link-btn" @click="handleDelete(doc)">删除</button>
            </li>
          </ul>
        </div>

        <div class="section">
          <div class="section-header">
            <h4>知识库搜索</h4>
            <div class="search-box">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="输入问题，如：什么是RAG？"
                @keyup.enter="handleSearch"
              />
              <button class="btn-primary" :disabled="searchLoading" @click="handleSearch">
                {{ searchLoading ? '搜索中...' : '搜索' }}
              </button>
            </div>
          </div>
          <div v-if="searchLoading" class="hint">搜索中...</div>
          <div v-else-if="searchResults.length === 0" class="hint">暂无搜索结果</div>
          <div v-else class="result-list">
            <div v-for="item in searchResults" :key="item.id" class="result-item">
              <div class="result-score">{{ item.score?.toFixed(2) ?? '0.00' }}</div>
              <div class="result-content">{{ item.content }}</div>
              <div class="result-meta">文档ID: {{ item.metadata?.document_id }} · 分块: {{ item.metadata?.chunk_index }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  justify-content: flex-end;
  z-index: 2000;
}

.drawer {
  width: 520px;
  max-width: 90%;
  height: 100%;
  background: #fff;
  box-shadow: -8px 0 24px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
}

.drawer-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drawer-header h3 {
  margin: 0;
  font-size: 18px;
  color: #111827;
}

.drawer-header p {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.close-btn {
  border: none;
  background: none;
  font-size: 22px;
  cursor: pointer;
  color: #6b7280;
}

.drawer-body {
  flex: 1;
  overflow: auto;
  padding: 16px 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 12px 14px;
  background: #f9fafb;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.section-header h4 {
  margin: 0;
  font-size: 15px;
  color: #111827;
}

.upload-btn {
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background: #2563eb;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
}

.upload-btn input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.hint {
  color: #9ca3af;
  font-size: 13px;
  padding: 6px 2px;
}

.doc-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.doc-item {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.doc-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.doc-name {
  font-size: 14px;
  color: #111827;
}

.doc-meta {
  font-size: 12px;
  color: #6b7280;
}

.link-btn {
  border: none;
  background: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 13px;
}

.search-box {
  display: flex;
  gap: 8px;
  align-items: center;
  flex: 1;
}

.search-box input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.search-box input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.btn-primary {
  padding: 8px 14px;
  border: none;
  background: #2563eb;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-score {
  font-size: 12px;
  color: #2563eb;
  font-weight: 600;
}

.result-content {
  font-size: 14px;
  color: #111827;
  line-height: 1.6;
}

.result-meta {
  font-size: 12px;
  color: #6b7280;
}
</style>
