<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { knowledgeApi } from '@/api'
import type { KnowledgeBase } from '@/types/knowledge-base'
import Sidebar, { type SidebarItem } from '@/components/common/Sidebar.vue'
import ContentList from '@/components/common/ContentList.vue'

const router = useRouter()

// 处理侧边栏切换
const handleSidebarChange = (item: SidebarItem) => {
  if (item === 'agent' || item === 'plugin') {
    // 切换到智能体或插件时，跳转回首页
    router.push('/')
  }
  // 如果是知识库，已经在知识库页面了，不需要处理
}

const knowledgeBases = ref<KnowledgeBase[]>([])
const loading = ref(false)
const searchQuery = ref('')
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const editingKB = ref<KnowledgeBase | null>(null)

// 表单数据
const formData = ref({
  name: '',
  description: '',
  embeddingModel: 'text-embedding-ada-002'
})

// 过滤后的列表
const filteredKnowledgeBases = computed(() => {
  let result = knowledgeBases.value

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter((item) =>
      item.name.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query))
    )
  }

  return result
})

// 获取知识库列表
const fetchKnowledgeBases = async () => {
  loading.value = true
  try {
    console.log('[知识库列表] 开始获取知识库列表...')
    const data = await knowledgeApi.getList()
    console.log('[知识库列表] 获取到的数据:', data)
    knowledgeBases.value = data || []
    console.log('[知识库列表] 设置后的列表:', knowledgeBases.value)
    console.log('[知识库列表] 列表长度:', knowledgeBases.value.length)
  } catch (error) {
    console.error('[知识库列表] 获取知识库列表失败:', error)
    alert('获取知识库列表失败: ' + (error instanceof Error ? error.message : String(error)))
    knowledgeBases.value = []
  } finally {
    loading.value = false
  }
}

// 打开创建对话框
const openCreateDialog = () => {
  formData.value = {
    name: '',
    description: '',
    embeddingModel: 'text-embedding-ada-002'
  }
  showCreateDialog.value = true
}

// 关闭创建对话框
const closeCreateDialog = () => {
  showCreateDialog.value = false
}

// 创建知识库
const handleCreate = async () => {
  if (!formData.value.name.trim()) {
    alert('请输入知识库名称')
    return
  }

  try {
    console.log('[知识库列表] 开始创建知识库:', formData.value)
    const createdKB = await knowledgeApi.create({
      name: formData.value.name,
      description: formData.value.description,
      embeddingModel: formData.value.embeddingModel
    })
    console.log('[知识库列表] 创建成功，返回的数据:', createdKB)
    
    // 关闭对话框
    closeCreateDialog()
    
    // 刷新列表
    console.log('[知识库列表] 刷新知识库列表...')
    await fetchKnowledgeBases()
    
    console.log('[知识库列表] 刷新后的列表:', knowledgeBases.value)
    alert('创建成功')
  } catch (error: any) {
    console.error('[知识库列表] 创建知识库失败:', error)
    alert('创建失败: ' + (error?.message || '未知错误'))
  }
}

// 点击知识库卡片 - 跳转到详情页面
const handleKBClick = (kb: KnowledgeBase) => {
  if (kb.id) {
    router.push(`/knowledge/${kb.id}`)
  }
}

// 打开编辑对话框
const handleKBEdit = (kb: KnowledgeBase) => {
  editingKB.value = kb
  formData.value = {
    name: kb.name,
    description: kb.description || '',
    embeddingModel: kb.embeddingModel
  }
  showEditDialog.value = true
}

// 关闭编辑对话框
const closeEditDialog = () => {
  showEditDialog.value = false
  editingKB.value = null
}

// 保存编辑
const handleEditSave = async () => {
  if (!editingKB.value?.id) return

  try {
    await knowledgeApi.update(editingKB.value.id, {
      name: formData.value.name,
      description: formData.value.description,
      embeddingModel: formData.value.embeddingModel
    })
    await fetchKnowledgeBases()
    closeEditDialog()
    alert('更新成功')
  } catch (error: any) {
    console.error('更新知识库失败:', error)
    alert('更新失败: ' + (error?.message || '未知错误'))
  }
}

// 删除知识库
const handleKBDelete = async (kb: KnowledgeBase) => {
  if (!kb.id) return
  
  if (!confirm(`确定要删除知识库"${kb.name}"吗？此操作不可恢复。`)) {
    return
  }

  try {
    await knowledgeApi.delete(kb.id)
    await fetchKnowledgeBases()
    alert('删除成功')
  } catch (error: any) {
    console.error('删除知识库失败:', error)
    alert('删除失败: ' + (error?.message || '未知错误'))
  }
}

onMounted(() => {
  fetchKnowledgeBases()
})
</script>

<template>
  <div class="knowledge-base-list-container">
    <!-- 顶部标题栏 -->
    <header class="title-header">
      <div class="title-content">
        <h1 class="title">知识库</h1>
        <span class="subtitle">{{ filteredKnowledgeBases.length }} 个知识库</span>
      </div>
    </header>
    
    <!-- 内容区域 -->
    <div class="content-wrapper">
      <!-- 左侧边栏 -->
      <Sidebar active-item="knowledge" @change="handleSidebarChange" />
      
      <!-- 主内容区 -->
      <div class="main-content">
        <!-- 操作栏 -->
        <div class="action-bar">
          <div class="search-box">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M7.333 12.667A5.333 5.333 0 1 0 7.333 2a5.333 5.333 0 0 0 0 10.667ZM14 14l-2.9-2.9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索知识库..."
              class="search-input"
            />
          </div>
          <button class="btn-primary" @click="openCreateDialog">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            新建知识库
          </button>
        </div>

        <!-- 内容列表 -->
        <ContentList :loading="loading" :empty="filteredKnowledgeBases.length === 0">
          <template #empty>
            <div class="empty-state">
              <div class="empty-icon">📚</div>
              <h3 class="empty-title">还没有知识库</h3>
              <p class="empty-desc">创建你的第一个知识库，开始管理文档</p>
              <button class="btn-primary" @click="openCreateDialog">创建知识库</button>
            </div>
          </template>
          <!-- 知识库卡片 -->
          <div
            v-for="(kb, index) in filteredKnowledgeBases"
            :key="kb.id || index"
            class="kb-card"
            @click="handleKBClick(kb)"
          >
            <div class="kb-card-header">
              <div class="kb-icon">📚</div>
              <div class="kb-info">
                <h3 class="kb-name">{{ kb.name }}</h3>
                <p v-if="kb.description" class="kb-description">{{ kb.description }}</p>
              </div>
              <div class="kb-actions" @click.stop>
                <button class="action-btn" @click.stop="handleKBEdit(kb)" title="编辑">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M11.333 2a2.121 2.121 0 0 1 3 3L5 14.667l-4 1.333L2.333 12l9.333-9.333z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
                <button class="action-btn delete" @click.stop="handleKBDelete(kb)" title="删除">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M2 4h12M6 4V2.667A1.333 1.333 0 0 1 7.333 2h1.334A1.333 1.333 0 0 1 10 2.667V4m2 0v9.333A1.333 1.333 0 0 1 10.667 14.667H5.333A1.333 1.333 0 0 1 4 13.333V4h8z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
            <div class="kb-card-footer">
              <span class="kb-meta">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                  <path d="M2 4h12M6 4V2.667A1.333 1.333 0 0 1 7.333 2h1.334A1.333 1.333 0 0 1 10 2.667V4m2 0v9.333A1.333 1.333 0 0 1 10.667 14.667H5.333A1.333 1.333 0 0 1 4 13.333V4h8z" stroke="currentColor" stroke-width="1.5"/>
                </svg>
                {{ kb.documentCount || 0 }} 个文档
              </span>
              <span v-if="kb.createdAt" class="kb-meta">
                {{ new Date(kb.createdAt).toLocaleDateString('zh-CN') }}
              </span>
            </div>
          </div>
        </ContentList>
      </div>
    </div>

    <!-- 创建对话框 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click="closeCreateDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h2>创建知识库</h2>
          <button class="dialog-close" @click="closeCreateDialog">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label>名称 *</label>
            <input v-model="formData.name" type="text" placeholder="输入知识库名称" />
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="formData.description" placeholder="输入知识库描述" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>嵌入模型</label>
            <select v-model="formData.embeddingModel">
              <option value="text-embedding-ada-002">text-embedding-ada-002</option>
            </select>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeCreateDialog">取消</button>
          <button class="btn-primary" @click="handleCreate">创建</button>
        </div>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <div v-if="showEditDialog" class="dialog-overlay" @click="closeEditDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h2>编辑知识库</h2>
          <button class="dialog-close" @click="closeEditDialog">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-item">
            <label>名称 *</label>
            <input v-model="formData.name" type="text" placeholder="输入知识库名称" />
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea v-model="formData.description" placeholder="输入知识库描述" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>嵌入模型</label>
            <select v-model="formData.embeddingModel">
              <option value="text-embedding-ada-002">text-embedding-ada-002</option>
            </select>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeEditDialog">取消</button>
          <button class="btn-primary" @click="handleEditSave">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.knowledge-base-list-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f9fafb;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.title-header {
  background: white;
  padding: 20px 32px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
  z-index: 10;
}

.title-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
}

.content-wrapper {
  flex: 1;
  display: flex;
  min-height: 0;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.action-bar {
  background: white;
  padding: 16px 32px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: #9ca3af;
  pointer-events: none;
}

.search-input {
  padding: 8px 12px 8px 36px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  width: 100%;
  transition: all 0.2s;
  background: #f9fafb;
  color: #1f2937;
}

.search-input:focus {
  outline: none;
  border-color: #2563eb;
  background: white;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
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

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.kb-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.kb-card:hover {
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
  transform: translateY(-2px);
}

.kb-card-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.kb-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.kb-info {
  flex: 1;
  min-width: 0;
}

.kb-name {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 6px 0;
}

.kb-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
  line-height: 1.5;
}

.kb-actions {
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

.kb-card-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.kb-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #9ca3af;
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

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-item input,
.form-item textarea,
.form-item select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s;
  background: white;
  color: #1f2937;
}

.form-item input:focus,
.form-item textarea:focus,
.form-item select:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.dialog-footer {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

