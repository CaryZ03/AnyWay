/**
 * API 统一导出
 */
export { agentApi } from './agent'
export { pluginApi } from './plugin'
export { llmApi } from './llm'
export { knowledgeApi } from './knowledge'

// 根据配置选择使用哪个API
import { backendWorkflowApi, localWorkflowApi } from './workflow'

/**
 * Workflow API
 * 根据配置自动选择使用后端API或本地API
 * 
 */
const currentApiMode = 'local'
const selectedApi = currentApiMode === 'local' ? localWorkflowApi : backendWorkflowApi

console.log(`[API配置] 当前使用 ${currentApiMode === 'local' ? '本地存储' : '后端'} API`)

export const workflowApi = selectedApi

