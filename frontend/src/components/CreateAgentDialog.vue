<template>
  <div v-if="show" class="dialog-overlay" @click.self="handleClose">
    <div class="dialog-container">
      <!-- 头部 -->
      <div class="dialog-header">
        <h2 class="dialog-title">创建智能体</h2>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <!-- 标签页 -->
      <div class="tabs">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'standard' }"
          @click="activeTab = 'standard'"
        >
          标准创建
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'ai' }"
          @click="activeTab = 'ai'"
        >
          AI创建
        </button>
      </div>

      <!-- 表单内容 -->
      <div class="dialog-body">
        <form @submit.prevent="handleSubmit">
          <!-- 智能体名称 -->
          <div class="form-group">
            <label class="form-label required">智能体名称</label>
            <input
              v-model="formData.name"
              type="text"
              class="form-input"
              placeholder="给智能体起一个独一无二的名字"
              maxlength="50"
              required
            />
            <div class="char-count">{{ formData.name.length }}/50</div>
          </div>

          <!-- 智能体功能介绍 -->
          <div class="form-group">
            <label class="form-label">智能体功能介绍</label>
            <textarea
              v-model="formData.description"
              class="form-textarea"
              placeholder="介绍智能体的功能，将会展示给智能体的用户"
              maxlength="500"
              rows="4"
            ></textarea>
            <div class="char-count">{{ formData.description.length }}/500</div>
          </div>

          <!-- 系统提示词 -->
          <div class="form-group">
            <label class="form-label required">系统提示词</label>
            <textarea
              v-model="formData.systemPrompt"
              class="form-textarea"
              placeholder="定义智能体的角色、能力和行为规范"
              maxlength="2000"
              rows="6"
              required
            ></textarea>
            <div class="char-count">{{ formData.systemPrompt.length }}/2000</div>
          </div>

          <!-- 模型配置 -->
          <div class="form-group">
            <label class="form-label">模型选择</label>
            <select v-model="formData.modelConfig.model" class="form-select">
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
            </select>
          </div>

          <!-- Temperature滑块 -->
          <div class="form-group">
            <label class="form-label">
              温度系数 (Temperature)
              <span class="param-value">{{ formData.modelConfig.temperature }}</span>
            </label>
            <input
              v-model.number="formData.modelConfig.temperature"
              type="range"
              min="0"
              max="2"
              step="0.1"
              class="form-slider"
            />
            <div class="slider-labels">
              <span>精确</span>
              <span>创造</span>
            </div>
          </div>

          <!-- 图标选择 -->
          <div class="form-group">
            <label class="form-label required">图标</label>
            <div class="icon-selector">
              <div
                v-for="icon in iconOptions"
                :key="icon"
                class="icon-option"
                :class="{ selected: formData.icon === icon }"
                @click="formData.icon = icon"
              >
                {{ icon }}
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="dialog-footer">
            <button type="button" class="btn btn-cancel" @click="handleClose">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '创建中...' : '确认' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { agentApi } from '@/api'

interface Props {
  show: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'success'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const activeTab = ref('standard')
const loading = ref(false)

const iconOptions = ['🤖', '📚', '🗣️', '🍳', '💡', '🎨', '🎵', '⚡', '🔥', '✨']

const formData = reactive({
  name: '',
  description: '',
  systemPrompt: '',
  icon: '🤖',
  modelConfig: {
    model: 'gpt-3.5-turbo',
    temperature: 0.7,
    maxTokens: 2000,
  },
})

const handleClose = () => {
  emit('close')
}

const handleSubmit = async () => {
  if (!formData.name.trim()) {
    window.alert('请输入智能体名称')
    return
  }
  
  if (!formData.systemPrompt.trim()) {
    window.alert('请输入系统提示词')
    return
  }

  loading.value = true
  
  try {
    await agentApi.create({
      name: formData.name,
      description: formData.description,
      systemPrompt: formData.systemPrompt,
      userPromptTemplate: '',
      modelConfig: formData.modelConfig,
      knowledgeBaseIds: [],
      pluginIds: [],
      status: 'draft'
    })
    
    window.alert('智能体创建成功！')
    emit('success')
    handleClose()
  } catch (error: any) {
    console.error('创建失败:', error)
    window.alert('创建失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
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

.dialog-container {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
  padding: 20px 24px;
  border-bottom: 1px solid #e5e5e5;
}

.dialog-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
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
  background: #f5f5f5;
  color: #c41e3a;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e5e5e5;
  padding: 0 24px;
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: none;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}

.tab-btn.active {
  color: #c41e3a;
  font-weight: 500;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #c41e3a;
}

.dialog-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.form-label.required::after {
  content: ' *';
  color: #c41e3a;
}

.param-value {
  float: right;
  color: #c41e3a;
  font-weight: 600;
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #c41e3a;
  box-shadow: 0 0 0 3px rgba(196, 30, 58, 0.1);
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: #c41e3a;
  box-shadow: 0 0 0 3px rgba(196, 30, 58, 0.1);
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.form-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e5e5e5;
  outline: none;
  -webkit-appearance: none;
}

.form-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #c41e3a;
  cursor: pointer;
}

.form-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #c41e3a;
  cursor: pointer;
  border: none;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.icon-selector {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.icon-option {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  border: 2px solid #e5e5e5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-option:hover {
  border-color: #c41e3a;
  background: rgba(196, 30, 58, 0.05);
}

.icon-option.selected {
  border-color: #c41e3a;
  background: rgba(196, 30, 58, 0.1);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e5e5e5;
}

.btn {
  padding: 10px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
  background: #e5e5e5;
}

.btn-primary {
  background: #c41e3a;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #a01830;
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

