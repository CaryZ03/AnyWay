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
 * 节点输出字段定义
 * 每个节点类型都有固定的输出字段
 */
export const NODE_OUTPUT_FIELDS = {
  start: ['input_text'], // 开始节点输出用户输入
  llm: ['response'], // LLM节点输出response
  http: ['status', 'data'], // HTTP节点输出状态码和数据
  knowledge: ['documents'], // 知识库节点输出找到的所有文件内容列表
  intent: ['intent', 'confidence'], // 意图识别节点输出意图和置信度
  string: ['result'], // 字符串处理节点输出处理结果
  end: ['output_text'], // 结束节点输出最终文本
} as const

export interface BaseNodeConfig {
  name: string
}

/**
 * 开始节点配置
 *
 * 对于当前实现，开始节点只负责把「用户输入」包装成统一的输入数据，
 * 实际字段在运行时由后端注入，这里不需要额外配置。
 */
export interface StartNodeConfig extends BaseNodeConfig {
  // 开始节点不需要额外配置，后端会自动从context获取user_input
}

/**
 * LLM 节点配置
 * 注意：字段名使用camelCase以匹配后端期望（systemPrompt而不是system_prompt）
 */
export interface LLMNodeConfig extends BaseNodeConfig {
  /**
   * 模型名称，默认 doubao-seed-1-6-251015
   */
  model?: string
  /**
   * 系统提示词（可选，有默认值）
   */
  systemPrompt?: string
  /**
   * 用户提示词模板（必需），支持变量替换，格式如 {nodeId.fieldName}
   */
  prompt: string
  /**
   * 温度参数，范围0-2，默认0.7
   */
  temperature?: number
}

/**
 * HTTP请求节点配置
 */
export interface HTTPNodeConfig extends BaseNodeConfig {
  /**
   * 请求URL，支持变量替换，格式如 {nodeId.fieldName}
   */
  url: string
  /**
   * 请求方法，支持GET/POST，默认GET
   */
  method?: 'GET' | 'POST'
  /**
   * 请求头，支持变量替换，格式如 {nodeId.fieldName}
   */
  headers?: Record<string, string>
  /**
   * 请求体（POST请求时使用），支持变量替换，格式如 {nodeId.fieldName}
   */
  body?: Record<string, string>
}

/**
 * 知识库检索节点配置
 */
export interface KnowledgeNodeConfig extends BaseNodeConfig {
  /**
   * 知识库ID
   */
  knowledge_base_id: number
  /**
   * 查询文本，支持变量替换，格式如 {nodeId.fieldName}
   */
  query: string
  /**
   * 返回最相似的K个文档块，范围1-10，默认5
   */
  top_k?: number
  /**
   * 相似度阈值，范围0-1，默认0.7
   */
  similarity_threshold?: number
}

/**
 * 意图识别节点配置
 * 注意：后端使用LLM进行意图识别，需要提供意图列表
 */
export interface IntentNodeConfig extends BaseNodeConfig {
  /**
   * 意图列表（必需），每个意图包含id、name、description、examples
   */
  intents: Array<{
    id: string
    name: string
    description?: string
    examples?: string[]
  }>
  /**
   * 模型名称，默认 doubao-seed-1-6-251015
   */
  model?: string
  /**
   * 温度参数，默认0.2
   */
  temperature?: number
}



/**
 * 字符串处理节点配置
 */
export interface StringNodeConfig extends BaseNodeConfig {
  /**
   * 操作类型
   */
  operation: 'concat' | 'replace' | 'substring' | 'format' | 'trim' | 'upper' | 'lower'
  /**
   * 输入字符串，支持变量替换，格式如 {nodeId.fieldName}
   */
  input_string: string
  /**
   * 处理参数，根据操作类型不同而不同
   */
  parameters?: Record<string, any>
}

/**
 * 结束节点配置
 *
 * 当前实现中，结束节点只是把工作流上下文中的最终 answer 字段作为输出，
 * 因此暂时不需要额外配置。
 */
export interface EndNodeConfig extends BaseNodeConfig {
  /**
   * 输出文本，支持变量替换，格式如 {nodeId.fieldName}
   */
  output_text: string
}

/**
 * 节点配置联合类型
 */
export type NodeConfig =
  | StartNodeConfig
  | IntentNodeConfig
  | LLMNodeConfig
  | HTTPNodeConfig
  | KnowledgeNodeConfig
  | StringNodeConfig
  | EndNodeConfig

/**
 * 工作流节点基础接口
 */
export interface BaseNode {
  id: string
  position?: NodePosition
}

/**
 * 开始节点
 */
export interface StartNode extends BaseNode {
  type: 'start'
  data: StartNodeConfig
}

/**
 * 意图识别节点
 */
export interface IntentNode extends BaseNode {
  type: 'intent'
  data: IntentNodeConfig
}

/**
 * LLM节点
 */
export interface LLMNode extends BaseNode {
  type: 'llm'
  data: LLMNodeConfig
}

/**
 * HTTP请求节点
 */
export interface HTTPNode extends BaseNode {
  type: 'http'
  data: HTTPNodeConfig
}

/**
 * 知识库检索节点
 */
export interface KnowledgeNode extends BaseNode {
  type: 'knowledge'
  data: KnowledgeNodeConfig
}

/**
 * 字符串处理节点
 */
export interface StringNode extends BaseNode {
  type: 'string'
  data: StringNodeConfig
}

/**
 * 结束节点
 */
export interface EndNode extends BaseNode {
  type: 'end'
  data: EndNodeConfig
}

/**
 * 工作流节点联合类型
 */
export type Node =
  | StartNode
  | IntentNode
  | LLMNode
  | HTTPNode
  | KnowledgeNode
  | StringNode
  | EndNode

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
  id?: string
  name: string
  description?: string
  version?: string
  nodes: string | Node[]  // 可能是 JSON 字符串，也可能是已解析的数组
  edges: string | WorkflowEdge[]  // 可能是 JSON 字符串，也可能是已解析的数组
  config: string | WorkflowConfig  // 可能是 JSON 字符串，也可能是已解析的对象
  createdAt?: string
  updatedAt?: string
}

/**
 * Workflow 表单（前端编辑格式）
 */
export interface WorkflowForm {
  id?: string
  name: string
  description?: string
  version?: string
  nodes: Node[]
  edges: WorkflowEdge[]
  config: WorkflowConfig
  status?: 'draft' | 'active'
  createdAt?: string
  updatedAt?: string
}

