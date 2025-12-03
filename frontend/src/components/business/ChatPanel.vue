<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { agentApi } from '@/api'
import type { ConversationResponse } from '@/types/api'

const props = defineProps<{
  agentId?: number
}>()

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  conversationId?: number
}

const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const sending = ref(false)
const chatBodyRef = ref<HTMLElement>()
const conversationHistory = ref<ConversationResponse[]>([])

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBodyRef.value) {
      chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
    }
  })
}

const formatTimestamp = (timestamp: string | undefined) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || sending.value || !props.agentId) return

  const userMessage = inputMessage.value.trim()
  const userTimestamp = new Date().toISOString()
  inputMessage.value = ''
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: userTimestamp
  })
  
  scrollToBottom()
  sending.value = true

  try {
    // 使用 chat API，支持未发布的智能体，支持插件调用
    const response = await agentApi.chat(props.agentId, userMessage)
    
    // 保存对话记录
    conversationHistory.value.push(response)
    
    // 添加助手回复
    messages.value.push({
      role: 'assistant',
      content: response.assistant_message || '收到回复',
      timestamp: response.created_at,
      conversationId: response.id
    })
  } catch (error: any) {
    console.error('发送消息失败:', error)
    messages.value.push({
      role: 'assistant',
      content: error?.message || '发送消息失败，请稍后重试',
      timestamp: new Date().toISOString()
    })
  } finally {
    sending.value = false
    scrollToBottom()
  }
}

// 加载历史消息
const loadHistory = async () => {
  if (!props.agentId) {
    messages.value = []
    conversationHistory.value = []
    return
  }

  try {
    const history = await agentApi.getConversations(props.agentId)
    conversationHistory.value = history
    
    // 将历史消息转换为消息列表格式
    messages.value = []
    history.forEach((conv) => {
      messages.value.push({
        role: 'user',
        content: conv.user_message,
        timestamp: conv.created_at,
        conversationId: conv.id
      })
      messages.value.push({
        role: 'assistant',
        content: conv.assistant_message,
        timestamp: conv.created_at,
        conversationId: conv.id
      })
    })
    
    scrollToBottom()
  } catch (error) {
    console.error('加载历史消息失败:', error)
  }
}

// 当 agentId 改变时，加载历史记录
watch(() => props.agentId, () => {
  loadHistory()
}, { immediate: true })

onMounted(() => {
  loadHistory()
  scrollToBottom()
})
</script>

<template>
  <div class="chat-panel">
    <div class="chat-body" ref="chatBodyRef">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">💬</div>
        <h3 class="empty-title">开始测试</h3>
        <p class="empty-desc">向智能体发送消息开始测试</p>
      </div>
      <div v-else class="messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message"
          :class="{ 'user-message': message.role === 'user' }"
        >
          <div class="message-avatar">
            {{ message.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-content">
            <div class="message-text">{{ message.content }}</div>
            <div v-if="message.timestamp" class="message-time">
              {{ formatTimestamp(message.timestamp) }}
            </div>
          </div>
        </div>
        <div v-if="sending" class="message assistant-message">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="message-text typing">正在输入...</div>
          </div>
        </div>
      </div>
    </div>
    <div class="chat-input-area">
      <textarea
        v-model="inputMessage"
        @keydown.enter.exact.prevent="sendMessage"
        class="chat-input"
        placeholder="输入消息..."
        rows="1"
      />
      <button
        class="send-btn"
        @click="sendMessage"
        :disabled="!inputMessage.trim() || sending"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M2 8l12-5-5 12-2-5-5-2z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  min-height: 0;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9ca3af;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.6;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 4px 0;
}

.empty-desc {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  background: #f3f4f6;
}

.user-message .message-avatar {
  background: #2563eb;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-text {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  background: #f3f4f6;
  color: #1f2937;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.user-message .message-text {
  background: #2563eb;
  color: white;
}

.message-text.typing {
  color: #9ca3af;
  font-style: italic;
}

.message-time {
  font-size: 11px;
  color: #9ca3af;
  padding: 0 4px;
  align-self: flex-end;
}

.user-message .message-time {
  align-self: flex-start;
}

.chat-input-area {
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 8px;
  align-items: flex-end;
  background: #f9fafb;
}

.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  max-height: 120px;
  transition: all 0.2s;
  background: white;
  color: #1f2937;
}

.chat-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.chat-input::placeholder {
  color: #9ca3af;
}

.send-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
