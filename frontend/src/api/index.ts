/**
 * API 统一导出
 */
export { agentApi } from './agent'
export { pluginApi } from './plugin'
export { llmApi } from './llm'
export { knowledgeApi } from './knowledge'

// Workflow 相关 API（当前仅使用后端 Workflow API）
import { backendWorkflowApi } from './workflow'

/**
 * Workflow API
 * 目前前端固定使用后端 Workflow API（不再区分 local/backend），
 * 避免类型比较报错，同时保证工作流一定走后端执行引擎。
 */
export const workflowApi = backendWorkflowApi

