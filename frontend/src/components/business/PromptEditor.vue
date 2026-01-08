<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  systemPrompt: string
  userPromptTemplate: string
}>()

const emit = defineEmits<{
  (e: 'update:systemPrompt', value: string): void
  (e: 'update:userPromptTemplate', value: string): void
}>()

const systemPromptValue = ref(props.systemPrompt)
const userPromptTemplateValue = ref(props.userPromptTemplate)

watch(() => props.systemPrompt, (val) => {
  systemPromptValue.value = val
})

watch(() => props.userPromptTemplate, (val) => {
  userPromptTemplateValue.value = val
})

const updateSystemPrompt = (value: string) => {
  systemPromptValue.value = value
  emit('update:systemPrompt', value)
}

const updateUserPromptTemplate = (value: string) => {
  userPromptTemplateValue.value = value
  emit('update:userPromptTemplate', value)
}
</script>

<template>
  <div class="prompt-editor">
    <div class="editor-section">
      <label class="section-label required">系统提示词</label>
      <textarea
        :value="systemPromptValue"
        @input="updateSystemPrompt(($event.target as HTMLTextAreaElement).value)"
        class="editor-textarea"
        placeholder="输入系统提示词，定义智能体的角色和行为..."
        rows="12"
      />
    </div>
    <div class="editor-section">
      <label class="section-label">用户提示模板</label>
      <textarea
        :value="userPromptTemplateValue"
        @input="updateUserPromptTemplate(($event.target as HTMLTextAreaElement).value)"
        class="editor-textarea"
        placeholder="输入用户提示模板..."
        rows="8"
      />
    </div>
  </div>
</template>

<style scoped>
.prompt-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 20px;
  overflow-y: auto;
}

.editor-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.section-label.required::after {
  content: ' *';
  color: #ef4444;
}

.editor-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 13px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.2s;
  background: #f9fafb;
  color: #1f2937;
}

.editor-textarea:focus {
  outline: none;
  border-color: #2563eb;
  background: white;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.editor-textarea::placeholder {
  color: #9ca3af;
}
</style>
