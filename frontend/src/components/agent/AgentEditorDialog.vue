<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Agent } from '@/types/agent'

const props = defineProps<{
  show: boolean
  agent?: Agent
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', agent: Partial<Agent>): void
}>()

const formData = ref({
  name: '',
  description: ''
})

watch(() => props.agent, (agent) => {
  if (agent) {
    formData.value = {
      name: agent.name || '',
      description: agent.description || ''
    }
  }
}, { immediate: true })

const handleClose = () => {
  emit('close')
}

const handleSave = () => {
  emit('save', formData.value)
  handleClose()
}
</script>

<template>
  <div v-if="show" class="dialog-overlay" @click.self="handleClose">
    <div class="dialog-container">
      <div class="dialog-header">
        <h2 class="dialog-title">{{ agent ? '编辑智能体' : '创建智能体' }}</h2>
        <button class="close-btn" @click="handleClose">×</button>
      </div>
      <div class="dialog-body">
        <div class="form-group">
          <label class="form-label required">智能体名称</label>
          <input
            v-model="formData.name"
            type="text"
            class="form-input"
            placeholder="给智能体起一个名字"
            maxlength="50"
            required
          />
          <div class="char-count">{{ formData.name.length }}/50</div>
        </div>
        <div class="form-group">
          <label class="form-label">描述</label>
          <textarea
            v-model="formData.description"
            class="form-textarea"
            placeholder="描述智能体的功能"
            rows="3"
            maxlength="500"
          />
          <div class="char-count">{{ formData.description.length }}/500</div>
        </div>
      </div>
      <div class="dialog-footer">
        <button type="button" class="btn btn-cancel" @click="handleClose">取消</button>
        <button type="button" class="btn btn-primary" @click="handleSave">保存</button>
      </div>
    </div>
  </div>
</template>

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
}

.dialog-container {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
  font-size: 24px;
  line-height: 1;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.dialog-body {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  box-sizing: border-box;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-textarea {
  resize: vertical;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-primary:disabled,
.btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

