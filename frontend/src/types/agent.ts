/**
 * Agent 相关类型定义
 */

/**
 * 模型配置
 */
export interface ModelConfig {
  model?: string
  temperature?: number
  maxTokens?: number
  topP?: number
  frequencyPenalty?: number
  presencePenalty?: number
}

/**
 * Agent 实体（后端返回格式）
 */
export interface Agent {
  id?: number
  name: string
  description?: string
  systemPrompt: string
  userPromptTemplate: string
  modelConfig: string | ModelConfig  // 可能是 JSON 字符串，也可能是已解析的对象
  workflowId?: number
  knowledgeBaseIds: string | number[]  // 可能是 JSON 字符串，也可能是已解析的数组
  pluginIds: string | number[]  // 可能是 JSON 字符串，也可能是已解析的数组
  status: 'draft' | 'published'
  createdAt?: string
  updatedAt?: string
}

/**
 * Agent 表单（前端编辑格式）
 */
export interface AgentForm {
  id?: number
  name: string
  description?: string
  systemPrompt: string
  userPromptTemplate: string
  modelConfig: ModelConfig
  workflowId?: number
  knowledgeBaseIds: number[]
  pluginIds: number[]
  status: 'draft' | 'published'
}

