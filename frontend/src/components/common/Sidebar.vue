<script setup lang="ts">
import { ref } from 'vue'

export type SidebarItem = 'agent' | 'plugin' | 'knowledge' | 'workflow'

const props = defineProps<{
  activeItem?: SidebarItem
}>()

const emit = defineEmits<{
  (e: 'change', item: SidebarItem): void
}>()

const items: { key: SidebarItem; label: string; icon: string }[] = [
  { key: 'agent', label: '智能体', icon: '🤖' },
  { key: 'plugin', label: '插件', icon: '🔌' },
  { key: 'knowledge', label: '知识库', icon: '📚' },
  { key: 'workflow', label: '工作流', icon: '⚙️' }
]

const active = ref<SidebarItem>(props.activeItem || 'agent')

const handleClick = (item: SidebarItem) => {
  active.value = item
  emit('change', item)
}
</script>

<template>
  <aside class="sidebar">
    <nav class="sidebar-nav">
      <div
        v-for="item in items"
        :key="item.key"
        class="nav-item"
        :class="{ active: active === item.key }"
        @click="handleClick(item.key)"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
      </div>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  background: #f8f9fa;
  border-right: 1px solid #e5e7eb;
  height: 100%;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: white;
}

.sidebar-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  margin: 4px 0;
  cursor: pointer;
  transition: all 0.2s;
  color: #6b7280;
  border-radius: 8px;
  font-size: 14px;
}

.nav-item:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.nav-item.active {
  background: #eff6ff;
  color: #2563eb;
  font-weight: 500;
}

.nav-icon {
  font-size: 18px;
  width: 20px;
  text-align: center;
}

.nav-label {
  flex: 1;
}
</style>
