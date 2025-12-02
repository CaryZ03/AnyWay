<script setup lang="ts">
defineProps<{
  loading?: boolean
  empty?: boolean
  emptyText?: string
}>()

defineSlots<{
  default(): any
  empty(): any
}>()
</script>

<template>
  <div class="content-list">
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>
    <div v-else-if="empty && $slots.empty" class="empty-state">
      <slot name="empty" />
    </div>
    <div v-else class="content-grid">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.content-list {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
  color: #6b7280;
  font-size: 14px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
</style>
