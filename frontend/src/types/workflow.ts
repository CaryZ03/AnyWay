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
 *
 * 对于当前实现，开始节点只负责把「用户输入」包装成统一的输入数据，
 * 实际字段在运行时由后端注入，这里不需要额外配置，因此保持为空对象。
 */
export interface StartNodeConfig {
  // 预留扩展位，当前不需要任何配置
}

/**
 * 意图识别节点配置
 *
 * 会把输入的自然语言分类到若干预设意图中，后端会要求大模型严格返回 JSON。
 */
export interface IntentNodeConfig {
  /**
   * 供大模型选择的意图列表
   */
  intents: Array<{
    id: string
    name: string
    description?: string
    examples?: string[]
  }>
  /**
   * 模型名称（目前主要使用豆包）
   */
  model?: string
  /**
   * 温度，默认 0.2，偏保守以保证分类稳定性
   */
  temperature?: number
}

/**
 * LLM 节点配置
 *
 * 该节点会根据系统提示词 + 用户提示词模板，调用大模型生成回答，
 * 后端会要求模型以 JSON 形式返回结果。
 */
export interface LLMNodeConfig {
  /**
   * 模型提供方+名称，这里和后端保持简化，只存模型名即可
   * 例如：doubao-seed-1-6-251015
   */
  model: string
  /**
   * 系统提示词，由前端在创建节点时给出合理默认值，用户可编辑
   */
  systemPrompt: string
  /**
   * 用户提示词模板，由用户填写。后端会在执行时把当前上下文 JSON
   * 以说明文字形式附加在该模板后面。
   */
  prompt: string
  temperature?: number
  maxTokens?: number
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
 * 结束节点配置
 *
 * 当前实现中，结束节点只是把工作流上下文中的最终 answer 字段作为输出，
 * 因此暂时不需要额外配置。
 */
export interface EndNodeConfig {
  // 预留扩展位
}

/**
 * 节点配置联合类型
 */
export type NodeConfig =
  | StartNodeConfig
  | IntentNodeConfig
  | LLMNodeConfig
  | PluginNodeConfig
  | EndNodeConfig

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
 * 意图识别节点
 */
export interface IntentWorkflowNode extends BaseWorkflowNode {
  type: 'intent'
  config: IntentNodeConfig
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
 * 结束节点
 */
export interface EndWorkflowNode extends BaseWorkflowNode {
  type: 'end'
  config: EndNodeConfig
}

/**
 * 工作流节点联合类型
 */
export type WorkflowNode =
  | StartWorkflowNode
  | IntentWorkflowNode
  | LLMWorkflowNode
  | PluginWorkflowNode
  | EndWorkflowNode

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
  /**
   * 可选的版本标记，用于前端展示
   */
  version?: string
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

