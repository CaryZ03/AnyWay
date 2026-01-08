/**
 * API 相关类型定义
 * 包含后端格式、请求/响应格式等
 */

// ========== Agent API 类型 ==========

/**
 * 后端 Agent 字段格式（snake_case）
 */
export interface BackendAgent {
  id?: number
  name: string
  description?: string
  system_prompt: string
  user_prompt_template: string
  model_config: string | Record<string, any>
  workflow_id?: number
  knowledge_base_ids: string | number[]
  plugin_ids: string | number[]
  status: 'draft' | 'published'
  created_at?: string
  updated_at?: string
}

/**
 * 后端 Agent 创建/更新请求格式
 */
export interface BackendAgentRequest {
  name: string
  description?: string
  system_prompt: string
  user_prompt_template: string
  model_config: Record<string, any>
  workflow_id?: number
  knowledge_base_ids: number[]
  plugin_ids: number[]
  status: 'draft' | 'published'
}

/**
 * 对话请求格式
 */
export interface ChatRequest {
  message: string
  context?: Record<string, any>
}

/**
 * 对话响应格式
 */
export interface ConversationResponse {
  id: number
  agent: number
  user_message: string
  assistant_message: string
  context: Record<string, any>
  created_at: string
}

// ========== Workflow API 类型 ==========

/**
 * 后端 Workflow 字段格式
 */
export interface BackendWorkflow {
  id?: string
  name: string
  description?: string
  definition: {
    nodes: any[]
    edges: any[]
    config?: any
  }
  status: 'draft' | 'active'
  created_at?: string
  updated_at?: string
}

/**
 * 后端 Workflow 创建/更新请求格式
 */
export interface BackendWorkflowRequest {
  name: string
  description?: string
  definition: {
    nodes: any[]
    edges: any[]
    config?: any
  }
  status?: 'draft' | 'active'
}

/**
 * 工作流执行请求
 */
export interface WorkflowExecuteRequest {
  input_data: Record<string, any>
}

/**
 * 工作流执行响应
 */
export interface WorkflowExecutionResponse {
  id: number
  workflow: number
  input_data: Record<string, any>
  output_data: Record<string, any>
  status: 'pending' | 'running' | 'completed' | 'failed'
  node_status: Record<string, any>
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

/**
 * 工作流执行历史列表项（简化版）
 */
export interface WorkflowExecutionListItem {
  id: number
  workflow: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  created_at: string
}

// ========== Knowledge Base API 类型 ==========

/**
 * 后端 KnowledgeBase 字段格式
 */
export interface BackendKnowledgeBase {
  id?: number
  name: string
  description?: string
  embedding_model: string
  document_count?: number
  created_at?: string
  updated_at?: string
}

/**
 * 后端 KnowledgeBase 创建/更新请求格式
 */
export interface BackendKnowledgeBaseRequest {
  name: string
  description?: string
  embedding_model: string
}

/**
 * 后端 Document 字段格式
 * 注意：根据实际API返回，可能包含以下字段：
 * - knowledge_base_id (Postman API) 或 knowledge_base (标准REST API)
 * - created_at (Postman API) 或 uploaded_at (标准REST API)
 */
export interface BackendDocument {
  id?: number
  knowledge_base?: number  // 标准REST API
  knowledge_base_id?: number  // Postman API
  filename: string
  file_type: string
  file_size: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string
  chunk_count?: number
  uploaded_at?: string  // 标准REST API
  created_at?: string  // Postman API
  updated_at?: string  // Postman API
  processed_at?: string
  sha256?: string  // Postman API
}

/**
 * 知识库搜索请求
 */
export interface SearchRequest {
  query: string
  top_k: number
}

/**
 * 知识库搜索响应（文档块）
 */
export interface SearchResult {
  id: string
  content: string
  metadata?: Record<string, any>
  score?: number
}

// ========== Plugin API 类型 ==========

/**
 * 后端 Plugin 字段格式
 * 注意：list 接口可能不返回 openapi_spec，只有 retrieve 接口返回完整信息
 */
export interface BackendPlugin {
  id?: number
  name: string
  description?: string
  openapi_spec?: string | Record<string, any>  // 列表接口可能没有，详情接口有
  base_url?: string  // 列表接口可能没有
  auth_config?: string | Record<string, any>  // 列表接口可能没有
  status: 'enabled' | 'disabled'
  created_at?: string
  updated_at?: string
}

/**
 * 后端 Plugin 创建/更新请求格式
 */
export interface BackendPluginRequest {
  name: string
  description?: string
  openapi_spec: Record<string, any>
  base_url: string
  auth_config: Record<string, any>
  status?: 'enabled' | 'disabled'
}

// ========== LLM API 类型 ==========

/**
 * LLM 聊天请求
 */
export interface LLMChatRequest {
  messages: Array<{
    role: 'system' | 'user' | 'assistant'
    content: string
  }>
  model?: string
  temperature?: number
}

/**
 * LLM 聊天响应
 */
export interface LLMChatResponse {
  reply: string
}

