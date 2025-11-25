import request from '@/utils/request'
import type { LLMChatRequest, LLMChatResponse } from '@/types/api'

/**
 * LLM API
 */

export const llmApi = {
  /**
   * LLM 聊天
   */
  chat: async (
    messages: LLMChatRequest['messages'],
    model: string = 'gpt-3.5-turbo',
    temperature: number = 0.7
  ): Promise<string> => {
    const requestData: LLMChatRequest = {
      messages,
      model,
      temperature,
    }
    const data = await request.post<LLMChatResponse>('/llm/chat/', requestData)
    return data.reply
  },
}

