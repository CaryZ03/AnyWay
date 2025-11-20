/**
 * Agent 相关工具函数
 */
import type { Agent, AgentForm, ModelConfig } from '@/types/agent'

/**
 * 将后端实体转换为前端表单模型
 * 智能处理：如果后端返回的是对象，直接使用；如果是字符串，则解析
 */
export function agentToForm(agent: Agent): AgentForm {
  // 如果 modelConfig 已经是对象，直接使用；否则解析字符串
  const modelConfig: ModelConfig = typeof agent.modelConfig === 'string'
    ? JSON.parse(agent.modelConfig || '{}') as ModelConfig
    : agent.modelConfig

  // 如果 knowledgeBaseIds 已经是数组，直接使用；否则解析字符串
  const knowledgeBaseIds: number[] = Array.isArray(agent.knowledgeBaseIds)
    ? agent.knowledgeBaseIds
    : JSON.parse(agent.knowledgeBaseIds || '[]') as number[]

  // 如果 pluginIds 已经是数组，直接使用；否则解析字符串
  const pluginIds: number[] = Array.isArray(agent.pluginIds)
    ? agent.pluginIds
    : JSON.parse(agent.pluginIds || '[]') as number[]

  return {
    id: agent.id,
    name: agent.name,
    description: agent.description,
    systemPrompt: agent.systemPrompt,
    userPromptTemplate: agent.userPromptTemplate,
    modelConfig,
    workflowId: agent.workflowId,
    knowledgeBaseIds,
    pluginIds,
    status: agent.status
  }
}

/**
 * 将前端表单模型转换为后端实体
 */
export function formToAgent(form: AgentForm): Agent {
  return {
    id: form.id,
    name: form.name,
    description: form.description,
    systemPrompt: form.systemPrompt,
    userPromptTemplate: form.userPromptTemplate,
    modelConfig: JSON.stringify(form.modelConfig),
    workflowId: form.workflowId,
    knowledgeBaseIds: JSON.stringify(form.knowledgeBaseIds),
    pluginIds: JSON.stringify(form.pluginIds),
    status: form.status
  }
}

/**
 * 验证 Agent
 */
export function validateAgent(agent: AgentForm): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  if (!agent.name || agent.name.trim() === '') {
    errors.push('名称不能为空')
  }

  if (!agent.systemPrompt || agent.systemPrompt.trim() === '') {
    errors.push('系统提示词不能为空')
  }

  if (!agent.userPromptTemplate || agent.userPromptTemplate.trim() === '') {
    errors.push('用户提示词模板不能为空')
  }

  if (!agent.status || !['draft', 'published'].includes(agent.status)) {
    errors.push('状态必须是 draft 或 published')
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * 创建默认的模型配置
 */
export function createDefaultModelConfig(): ModelConfig {
  return {
    model: 'gpt-4',
    temperature: 0.7,
    maxTokens: 2000,
    topP: 1,
    frequencyPenalty: 0,
    presencePenalty: 0
  }
}

/**
 * 创建默认的 Agent 表单
 */
export function createDefaultAgentForm(): AgentForm {
  return {
    name: '',
    description: '',
    systemPrompt: '',
    userPromptTemplate: '',
    modelConfig: createDefaultModelConfig(),
    workflowId: undefined,
    knowledgeBaseIds: [],
    pluginIds: [],
    status: 'draft'
  }
}

