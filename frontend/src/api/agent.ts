import request from '@/utils/request'
import type { Agent, AgentForm } from '@/types/agent'
import type {
  BackendAgent,
  BackendAgentRequest,
  ChatRequest,
  ConversationResponse,
} from '@/types/api'

/**
 * Agent API
 * 后端字段名：snake_case (system_prompt, user_prompt_template, model_config, workflow_id, knowledge_base_ids, plugin_ids, created_at, updated_at)
 * 前端字段名：camelCase (systemPrompt, userPromptTemplate, modelConfig, workflowId, knowledgeBaseIds, pluginIds, createdAt, updatedAt)
 */

/**
 * 转换后端 Agent 到前端 Agent
 */
function transformAgent(backend: BackendAgent): Agent {
  return {
    id: backend.id,
    name: backend.name,
    description: backend.description,
    systemPrompt: backend.system_prompt,
    userPromptTemplate: backend.user_prompt_template,
    modelConfig: typeof backend.model_config === 'string' 
      ? JSON.parse(backend.model_config) 
      : backend.model_config,
    workflowId: backend.workflow_id,
    knowledgeBaseIds: Array.isArray(backend.knowledge_base_ids)
      ? backend.knowledge_base_ids
      : typeof backend.knowledge_base_ids === 'string'
      ? JSON.parse(backend.knowledge_base_ids)
      : [],
    pluginIds: Array.isArray(backend.plugin_ids)
      ? backend.plugin_ids
      : typeof backend.plugin_ids === 'string'
      ? JSON.parse(backend.plugin_ids)
      : [],
    status: backend.status,
    createdAt: backend.created_at,
    updatedAt: backend.updated_at,
  }
}

/**
 * 转换前端 AgentForm 到后端请求格式
 * 注意：此函数暂未使用，保留供未来使用
 */
// function transformAgentRequest(form: AgentForm): BackendAgentRequest {
//   return {
//     name: form.name,
//     description: form.description,
//     system_prompt: form.systemPrompt,
//     user_prompt_template: form.userPromptTemplate,
//     model_config: form.modelConfig,
//     workflow_id: form.workflowId,
//     knowledge_base_ids: form.knowledgeBaseIds,
//     plugin_ids: form.pluginIds,
//     status: form.status,
//   }
// }

export const agentApi = {
  /**
   * 获取智能体列表
   */
  getList: async (): Promise<Agent[]> => {
    const data = await request.get<BackendAgent[]>('/agents/')
    return Array.isArray(data) ? data.map(transformAgent) : []
  },

  /**
   * 获取智能体详情
   */
  getDetail: async (id: number): Promise<Agent> => {
    const data = await request.get<BackendAgent>(`/agents/${id}/`)
    return transformAgent(data)
  },

  /**
   * 创建智能体
   */
  create: async (form: Partial<AgentForm> | any): Promise<Agent> => {
    const requestData: any = {}
    if ('name' in form) requestData.name = form.name
    if ('description' in form) requestData.description = form.description
    if ('systemPrompt' in form) requestData.system_prompt = form.systemPrompt
    if ('system_prompt' in form) requestData.system_prompt = form.system_prompt
    if ('userPromptTemplate' in form) requestData.user_prompt_template = form.userPromptTemplate
    if ('modelConfig' in form) requestData.model_config = form.modelConfig
    if ('model_config' in form) requestData.model_config = form.model_config
    if ('workflowId' in form) requestData.workflow_id = form.workflowId
    if ('knowledgeBaseIds' in form) requestData.knowledge_base_ids = form.knowledgeBaseIds
    if ('pluginIds' in form) requestData.plugin_ids = form.pluginIds
    if ('status' in form) requestData.status = form.status
    
    // 设置默认值
    if (!requestData.user_prompt_template) requestData.user_prompt_template = ''
    if (!requestData.knowledge_base_ids) requestData.knowledge_base_ids = []
    if (!requestData.plugin_ids) requestData.plugin_ids = []
    
    const data = await request.post<BackendAgent>('/agents/', requestData)
    return transformAgent(data)
  },

  /**
   * 更新智能体
   */
  update: async (id: number, form: Partial<AgentForm>): Promise<Agent> => {
    // 转换部分更新数据
    const requestData: Partial<BackendAgentRequest> = {}
    if (form.name !== undefined) requestData.name = form.name
    if (form.description !== undefined) requestData.description = form.description
    if (form.systemPrompt !== undefined) requestData.system_prompt = form.systemPrompt
    if (form.userPromptTemplate !== undefined) requestData.user_prompt_template = form.userPromptTemplate
    if (form.modelConfig !== undefined) requestData.model_config = form.modelConfig
    if (form.workflowId !== undefined) requestData.workflow_id = form.workflowId
    if (form.knowledgeBaseIds !== undefined) requestData.knowledge_base_ids = form.knowledgeBaseIds
    if (form.pluginIds !== undefined) requestData.plugin_ids = form.pluginIds
    if (form.status !== undefined) requestData.status = form.status

    const data = await request.patch<BackendAgent>(`/agents/${id}/`, requestData)
    return transformAgent(data)
  },

  /**
   * 删除智能体
   */
  delete: async (id: number): Promise<void> => {
    await request.delete(`/agents/${id}/`)
  },

  /**
   * 发布智能体
   */
  publish: async (id: number): Promise<Agent> => {
    const data = await request.post<BackendAgent>(`/agents/${id}/publish/`)
    return transformAgent(data)
  },

  /**
   * 测试智能体
   */
  test: async (id: number, message: string, context?: Record<string, any>): Promise<ConversationResponse> => {
    const requestData: ChatRequest = { message, context }
    return await request.post<ConversationResponse>(`/agents/${id}/test/`, requestData)
  },

  /**
   * 与智能体对话
   */
  chat: async (id: number, message: string, context?: Record<string, any>): Promise<ConversationResponse> => {
    const requestData: ChatRequest = { message, context }
    return await request.post<ConversationResponse>(`/agents/${id}/chat/`, requestData)
  },

  /**
   * 为智能体添加插件
   */
  addPlugins: async (id: number, pluginIds: number | number[]): Promise<Agent> => {
    const requestData = {
      plugin_ids: Array.isArray(pluginIds) ? pluginIds : [pluginIds]
    }
    const data = await request.post<BackendAgent>(`/agents/${id}/add_plugins/`, requestData)
    return transformAgent(data)
  },

  /**
   * 从智能体删除插件
   */
  removePlugins: async (id: number, pluginIds: number | number[]): Promise<Agent> => {
    const requestData = {
      plugin_ids: Array.isArray(pluginIds) ? pluginIds : [pluginIds]
    }
    const data = await request.post<BackendAgent>(`/agents/${id}/remove_plugins/`, requestData)
    return transformAgent(data)
  },

  /**
   * 获取智能体对话历史
   */
  getConversations: async (id: number): Promise<ConversationResponse[]> => {
    return await request.get<ConversationResponse[]>(`/agents/${id}/conversations/`)
  },
}

