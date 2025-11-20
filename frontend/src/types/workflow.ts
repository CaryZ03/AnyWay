/**
 * Workflow 相关类型定义
 */

/**
 * 节点位置
 */
export interface NodePosition {
  x: number
  y: number
}

/**
 * 开始节点配置
 */
export interface StartNodeConfig {
  input: {
    userInput: string
  }
}

/**
 * LLM节点配置
 */
export interface LLMNodeConfig {
  model: 'deepseek' | 'doubao' | 'qwen'
  prompt: string
  temperature?: number
  maxTokens?: number
  systemPrompt?: string
}

/**
 * 插件节点配置
 */
export interface PluginNodeConfig {
  pluginId: number
  operation: string
  parameters?: Record<string, string>
}

/**
 * 条件节点配置
 */
export interface ConditionNodeConfig {
  condition: string
  truePath: string
  falsePath: string
}

/**
 * 结束节点配置
 */
export interface EndNodeConfig {
  output: {
    result: string
  }
}

/**
 * 节点配置联合类型
 */
export type NodeConfig = StartNodeConfig | LLMNodeConfig | PluginNodeConfig | ConditionNodeConfig | EndNodeConfig

/**
 * 工作流节点基础接口
 */
export interface BaseWorkflowNode {
  id: string
  name?: string
  position?: NodePosition
}

/**
 * 开始节点
 */
export interface StartWorkflowNode extends BaseWorkflowNode {
  type: 'start'
  config: StartNodeConfig
}

/**
 * LLM节点
 */
export interface LLMWorkflowNode extends BaseWorkflowNode {
  type: 'llm'
  config: LLMNodeConfig
}

/**
 * 插件节点
 */
export interface PluginWorkflowNode extends BaseWorkflowNode {
  type: 'plugin'
  config: PluginNodeConfig
}

/**
 * 条件节点
 */
export interface ConditionWorkflowNode extends BaseWorkflowNode {
  type: 'condition'
  config: ConditionNodeConfig
}

/**
 * 结束节点
 */
export interface EndWorkflowNode extends BaseWorkflowNode {
  type: 'end'
  config: EndNodeConfig
}

/**
 * 工作流节点联合类型
 */
export type WorkflowNode = StartWorkflowNode | LLMWorkflowNode | PluginWorkflowNode | ConditionWorkflowNode | EndWorkflowNode

/**
 * 工作流边
 */
export interface WorkflowEdge {
  id: string
  source: string
  target: string
  condition?: string
}

/**
 * 工作流配置
 */
export interface WorkflowConfig {
  timeout?: number
  retry?: number
  parallel?: boolean
}

/**
 * Workflow 实体（后端返回格式）
 */
export interface Workflow {
  id?: number
  name: string
  description?: string
  version?: string
  nodes: string | WorkflowNode[]  // 可能是 JSON 字符串，也可能是已解析的数组
  edges: string | WorkflowEdge[]  // 可能是 JSON 字符串，也可能是已解析的数组
  config: string | WorkflowConfig  // 可能是 JSON 字符串，也可能是已解析的对象
  createdAt?: string
  updatedAt?: string
}

/**
 * Workflow 表单（前端编辑格式）
 */
export interface WorkflowForm {
  id?: number
  name: string
  description?: string
  version?: string
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  config: WorkflowConfig
}

