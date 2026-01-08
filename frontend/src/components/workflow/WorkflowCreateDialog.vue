<script setup lang="ts">
import { ref, watch } from 'vue'
import type { WorkflowForm } from '@/types/workflow'
import { workflowApi } from '@/api'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const saving = ref(false)
const form = ref({
  name: '',
  description: ''
})

watch(
  () => props.show,
  (isShow) => {
    if (isShow) {
      // 重置表单
      form.value = {
        name: '',
        description: ''
      }
    }
  }
)

const close = () => emit('close')

const handleSubmit = async () => {
  if (!form.value.name.trim()) {
    alert('请填写工作流名称')
    return
  }

  saving.value = true
  try {
    const newWorkflow: WorkflowForm = {
      name: form.value.name.trim(),
      description: form.value.description.trim() || undefined,
      nodes: [{
        id: 'node-start',
        type: 'start',
        data: {
          name: '开始'
        },
        position: { x: 250, y: 0 }
      },
      {
        id: 'node-end',
        type: 'end',
        data: {
          name: '结束',
          output_text: '最终结果',
        },
        position: { x: 300, y: 400 }
      }],
      edges: [],
      config: {},
    }

    await workflowApi.create(newWorkflow)
    emit('saved')
  } catch (error: any) {
    alert(error?.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div v-if="show" class="dialog-backdrop">
    <div class="dialog">
      <div class="dialog-header">
        <h3>新建工作流</h3>
        <button class="close-btn" @click="close">×</button>
      </div>
      <div class="dialog-body">
        <label class="form-item">
          <span>名称</span>
          <input v-model="form.name" type="text" placeholder="请输入名称" />
        </label>
        <label class="form-item">
          <span>描述</span>
          <textarea v-model="form.description" rows="3" placeholder="可填写工作流简介" />
        </label>
      </div>
      <div class="dialog-footer">
        <button class="btn-secondary" @click="close">取消</button>
        <button class="btn-primary" :disabled="saving" @click="handleSubmit">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.dialog {
  width: 480px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.dialog-header h3 {
  margin: 0;
  font-size: 16px;
  color: #111827;
}

.close-btn {
  border: none;
  background: none;
  font-size: 20px;
  cursor: pointer;
  color: #6b7280;
}

.dialog-body {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-item span {
  font-size: 13px;
  color: #374151;
}

.form-item input,
.form-item textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #111827;
  resize: none;
}

.form-item input:focus,
.form-item textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.dialog-footer {
  padding: 12px 20px 16px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid #e5e7eb;
}

.btn-primary,
.btn-secondary {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}
</style>

