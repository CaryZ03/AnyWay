<template>
  <div class="chat-container">
    <!-- 头部导航 -->
    <div class="chat-header">
      <button class="back-btn" @click="handleBack">
        ← 返回
      </button>
      <div class="agent-info">
        <div class="agent-avatar">{{ agent?.name?.charAt(0) || '🤖' }}</div>
        <div class="agent-details">
          <h2 class="agent-name">{{ agent?.name || '加载中...' }}</h2>
          <p class="agent-desc">{{ agent?.description || '' }}</p>
        </div>
      </div>
      <div class="header-actions">
        <button 
          v-if="agent?.status === 'draft'" 
          class="publish-btn" 
          @click="handlePublish"
          :disabled="publishing"
        >
          {{ publishing ? '发布中...' : '📢 发布智能体' }}
        </button>
        <span v-else class="status-badge published">✓ 已发布</span>
        <button class="icon-btn" @click="handleSettings">⚙️</button>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-body" ref="chatBodyRef">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">💬</div>
        <h3>开始对话</h3>
        <p>向智能体发送消息开始聊天</p>
      </div>

      <div v-else class="messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message"
          :class="{ 'user-message': message.role === 'user' }"
        >
          <div class="message-avatar">
            {{ message.role === 'user' ? '👤' : agent?.name?.charAt(0) || '🤖' }}
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="message-sender">
                {{ message.role === 'user' ? '你' : agent?.name }}
              </span>
              <span class="message-time">{{ message.time }}</span>
            </div>
            <div class="message-text">{{ message.content }}</div>
          </div>
        </div>
      </div>

      <!-- 查询知识库指示器 -->
      <div v-if="queryingKnowledge" class="message">
        <div class="message-avatar">📚</div>
        <div class="message-content">
          <div class="message-header">
            <span class="message-sender">系统</span>
            <span class="message-time">{{ getCurrentTime() }}</span>
          </div>
          <div class="message-text typing">正在查询知识库...</div>
        </div>
      </div>

      <!-- 加载中指示器 -->
      <div v-if="loading" class="message">
        <div class="message-avatar">
          {{ agent?.name?.charAt(0) || '🤖' }}
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-footer">
      <div class="input-container">
        <textarea
          v-model="inputMessage"
          class="message-input"
          placeholder="输入消息..."
          rows="1"
          @keydown.enter.exact.prevent="handleSend"
          @input="adjustTextareaHeight"
          ref="textareaRef"
        ></textarea>
        <button
          class="send-btn"
          :disabled="!inputMessage.trim() || loading || queryingKnowledge"
          @click="handleSend"
        >
          <span v-if="!loading">发送</span>
          <span v-else>发送中...</span>
        </button>
      </div>
      <div class="input-hint">
        按 Enter 发送，Shift + Enter 换行
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { agentApi, knowledgeApi } from '@/api'
import type { Agent } from '@/types/agent'
import type { ConversationResponse } from '@/types/api'

interface Props {
  agentId: number
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  time: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'back'): void
}>()

const agent = ref<Agent | null>(null)
const messages = ref<Message[]>([])
const inputMessage = ref('')
const loading = ref(false)
const queryingKnowledge = ref(false)
const publishing = ref(false)
const chatBodyRef = ref<HTMLElement>()
const textareaRef = ref<HTMLTextAreaElement>()
const conversationHistory = ref<ConversationResponse[]>([])

// 加载智能体信息
const loadAgent = async () => {
  try {
    agent.value = await agentApi.getDetail(props.agentId)
  } catch (error) {
    console.error('加载智能体失败:', error)
    window.alert('加载智能体信息失败')
  }
}

// 获取当前时间字符串
const getCurrentTime = () => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

/**
 * 查询知识库并构建知识上下文
 */
const buildKnowledgeContext = async (query: string): Promise<string> => {
  if (!agent.value || !agent.value.knowledgeBaseIds) {
    return ''
  }

  // 处理 knowledgeBaseIds 可能是 string 或 number[] 的情况
  let kbIds: number[] = []
  if (typeof agent.value.knowledgeBaseIds === 'string') {
    try {
      const parsed = JSON.parse(agent.value.knowledgeBaseIds)
      kbIds = Array.isArray(parsed) ? parsed.map((id: any) => typeof id === 'string' ? parseInt(id, 10) : id).filter((id: any) => !isNaN(id)) : []
    } catch {
      console.warn('无法解析 knowledgeBaseIds')
      return ''
    }
  } else if (Array.isArray(agent.value.knowledgeBaseIds)) {
    kbIds = agent.value.knowledgeBaseIds.map((id: string | number) => typeof id === 'string' ? parseInt(id, 10) : id).filter((id: number) => !isNaN(id))
  }

  if (kbIds.length === 0) {
    return ''
  }

  // 设置查询状态
  queryingKnowledge.value = true
  await nextTick()
  scrollToBottom()

  const knowledgeContexts: string[] = []

  try {
    // 查询所有关联的知识库
    for (const kbId of kbIds) {
      try {
        const results = await knowledgeApi.query(kbId, query, 3)
        if (results && results.length > 0) {
          const kbContent = results
            .map((result, index) => `${index + 1}. ${result.content}`)
            .join('\n\n')
          knowledgeContexts.push(`知识库 #${kbId} 相关内容：\n${kbContent}`)
        }
      } catch (error) {
        console.warn(`查询知识库 ${kbId} 失败:`, error)
        // 继续查询其他知识库，不中断流程
      }
    }
  } finally {
    // 清除查询状态
    queryingKnowledge.value = false
  }

  return knowledgeContexts.join('\n\n---\n\n')
}

/**
 * 替换提示词模板中的变量
 */
const replacePromptVariables = (template: string, variables: Record<string, string>): string => {
  let result = template
  for (const [key, value] of Object.entries(variables)) {
    const regex = new RegExp(`\\{${key}\\}`, 'g')
    result = result.replace(regex, value)
  }
  return result
}

// 发送消息
const handleSend = async () => {
  const message = inputMessage.value.trim()
  if (!message || loading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    time: getCurrentTime()
  })

  inputMessage.value = ''
  loading.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 如果有知识库，先查询知识库
    let knowledgeContext = ''
    if (agent.value && agent.value.knowledgeBaseIds && agent.value.knowledgeBaseIds.length > 0) {
      knowledgeContext = await buildKnowledgeContext(message)
    }

    // 构建对话历史
    const conversationHistoryText = conversationHistory.value
      .slice(-5) // 只取最近5轮对话
      .map((conv: ConversationResponse) => `用户: ${conv.user_message}\n助手: ${conv.assistant_message}`)
      .join('\n\n')

    // 如果有userPromptTemplate，替换变量
    let finalMessage = message
    if (agent.value && agent.value.userPromptTemplate) {
      const variables: Record<string, string> = {
        user_message: message,
        conversation_history: conversationHistoryText || '无',
        knowledge_context: knowledgeContext || '无相关知识',
        plugin_response: '' // 插件响应由后端处理
      }
      finalMessage = replacePromptVariables(agent.value.userPromptTemplate, variables)
    } else if (knowledgeContext) {
      // 如果没有模板但有知识库内容，直接拼接
      finalMessage = `用户问题：${message}\n\n相关知识：\n${knowledgeContext}\n\n请基于以上信息回答用户问题。`
    }

    // 调用后端API
    const response = await agentApi.chat(props.agentId, finalMessage)
    
    // 保存对话记录
    conversationHistory.value.push(response)
    
    // 添加AI回复
    messages.value.push({
      role: 'assistant',
      content: response.assistant_message || '抱歉，我没有回复',
      time: getCurrentTime()
    })
  } catch (error: any) {
    console.error('发送消息失败:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了错误: ' + (error.message || '未知错误'),
      time: getCurrentTime()
    })
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}

// 自动调整文本框高度
const adjustTextareaHeight = () => {
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
  }
}

// 返回列表
const handleBack = () => {
  emit('back')
}

// 发布智能体
const handlePublish = async () => {
  if (!agent.value?.id) return
  
  if (!confirm('确定要发布这个智能体吗？发布后可以正常对话。')) return
  
  publishing.value = true
  try {
    const published = await agentApi.publish(agent.value.id)
    agent.value = published
    window.alert('智能体发布成功！现在可以开始对话了。')
  } catch (error: any) {
    console.error('发布失败:', error)
    window.alert('发布失败: ' + (error.message || '未知错误'))
  } finally {
    publishing.value = false
  }
}

// 设置
const handleSettings = () => {
  window.alert('设置功能开发中...')
}

// 监听agentId变化
watch(() => props.agentId, () => {
  loadAgent()
  messages.value = []
}, { immediate: true })

onMounted(() => {
  loadAgent()
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f8f8;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e5e5e5;
  gap: 16px;
}

.back-btn {
  padding: 8px 16px;
  border: none;
  background: #f5f5f5;
  border-radius: 6px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #c41e3a;
  color: white;
}

.agent-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.agent-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #c41e3a 0%, #8b1528 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
}

.agent-details {
  flex: 1;
}

.agent-name {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 4px 0;
}

.agent-desc {
  font-size: 13px;
  color: #666;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: #c41e3a;
  transform: scale(1.05);
}

.publish-btn {
  padding: 8px 16px;
  border: none;
  background: linear-gradient(135deg, #c41e3a 0%, #a01830 100%);
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.publish-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.4);
}

.publish-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
}

.status-badge.published {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 18px;
  margin: 0 0 8px 0;
  color: #666;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 12px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #c41e3a 0%, #8b1528 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #666 0%, #444 100%);
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.user-message .message-content {
  text-align: right;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 13px;
}

.user-message .message-header {
  flex-direction: row-reverse;
}

.message-sender {
  font-weight: 500;
  color: #333;
}

.message-time {
  color: #999;
}

.message-text {
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  white-space: pre-wrap;
  word-break: break-word;
}

.user-message .message-text {
  background: linear-gradient(135deg, #c41e3a 0%, #a01830 100%);
  color: white;
}

.message-text.typing {
  color: #999;
  font-style: italic;
  background: #f5f5f5;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: white;
  border-radius: 12px;
  width: fit-content;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c41e3a;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-footer {
  padding: 16px 24px;
  background: white;
  border-top: 1px solid #e5e5e5;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  transition: all 0.2s;
  max-height: 120px;
  overflow-y: auto;
}

.message-input:focus {
  outline: none;
  border-color: #c41e3a;
  box-shadow: 0 0 0 3px rgba(196, 30, 58, 0.1);
}

.send-btn {
  padding: 12px 32px;
  border: none;
  background: linear-gradient(135deg, #c41e3a 0%, #a01830 100%);
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-hint {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
  text-align: center;
}

/* 滚动条样式 */
.chat-body::-webkit-scrollbar {
  width: 8px;
}

.chat-body::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-body::-webkit-scrollbar-thumb {
  background: #c41e3a;
  border-radius: 4px;
}

.chat-body::-webkit-scrollbar-thumb:hover {
  background: #a01830;
}
</style>
