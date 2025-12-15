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
 */
export interface IntentNodeConfig {
  /**
   * 输入文本，支持变量替换
   */
  input_text: string
  /**
   * 意图类别列表
   */
  intent_categories: string[]
  /**
   * 识别方式：llm 或 keyword
   */
  recognition_method: 'llm' | 'keyword'
  /**
   * LLM识别方式时需要的智能体UUID
   */
  agent_uuid?: string
  /**
   * 关键词匹配方式时的关键词映射
   */
  keywords?: Record<string, string[]>
}

/**
 * LLM 节点配置
 */
export interface LLMNodeConfig {
  /**
   * 关联的智能体UUID
   */
  agent_uuid: string
  /**
   * 提示词，支持变量替换
   */
  prompt: string
  /**
   * 温度参数，范围0-2，默认0.7
   */
  temperature?: number
  /**
   * 最大生成token数，默认2000
   */
  max_tokens?: number
}

/**
 * HTTP请求节点配置
 */
export interface HTTPNodeConfig {
  /**
   * 请求URL，支持变量替换
   */
  url: string
  /**
   * 请求方法，支持GET/POST，默认GET
   */
  method?: 'GET' | 'POST'
  /**
   * 请求头，支持变量替换
   */
  headers?: Record<string, string>
  /**
   * 请求体（POST请求时使用），支持变量替换
   */
  body?: Record<string, any>
}

/**
 * 知识库检索节点配置
 */
export interface KnowledgeNodeConfig {
  /**
   * 知识库ID
   */
  knowledge_base_id: number
  /**
   * 查询文本，支持变量替换
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
 * 字符串处理节点配置
 */
export interface StringNodeConfig {
  /**
   * 操作类型
   */
  operation: 'concat' | 'replace' | 'substring' | 'format' | 'trim' | 'upper' | 'lower'
  /**
   * 输入字符串，支持变量替换
   */
  input_string: string
  /**
   * 处理参数，根据操作类型不同而不同
   */
  parameters?: Record<string, any>
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
  | HTTPNodeConfig
  | KnowledgeNodeConfig
  | StringNodeConfig
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
 * HTTP请求节点
 */
export interface HTTPWorkflowNode extends BaseWorkflowNode {
  type: 'http'
  config: HTTPNodeConfig
}

/**
 * 知识库检索节点
 */
export interface KnowledgeWorkflowNode extends BaseWorkflowNode {
  type: 'knowledge'
  config: KnowledgeNodeConfig
}

/**
 * 字符串处理节点
 */
export interface StringWorkflowNode extends BaseWorkflowNode {
  type: 'string'
  config: StringNodeConfig
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
  | HTTPWorkflowNode
  | KnowledgeWorkflowNode
  | StringWorkflowNode
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

