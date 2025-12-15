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
  input_text: string
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
  | PluginNodeConfig
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
 * 字段绑定：将源节点的输出字段绑定到目标节点的输入字段
 */
export interface FieldBinding {
  /**
   * 源节点ID
   */
  sourceNodeId: string
  /**
   * 源节点输出字段名
   */
  sourceField: string
  /**
   * 目标节点输入字段名
   */
  targetField: string
}

/**
 * 工作流边
 */
export interface WorkflowEdge {
  id: string
  source: string
  target: string
  condition?: string
  /**
   * 字段绑定列表：定义从源节点到目标节点的数据绑定
   */
  bindings?: FieldBinding[]
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
  nodes: string | Node[]  // 可能是 JSON 字符串，也可能是已解析的数组
  edges: string | WorkflowEdge[]  // 可能是 JSON 字符串，也可能是已解析的数组
  config: string | WorkflowConfig  // 可能是 JSON 字符串，也可能是已解析的对象
  createdAt?: string
  updatedAt?: string
}

/**
 * 节点字段定义：描述节点的输入和输出字段
 */
export interface NodeFieldDefinition {
  /**
   * 字段名
   */
  name: string
  /**
   * 字段显示名称
   */
  label: string
  /**
   * 字段类型
   */
  type: 'string' | 'number' | 'object' | 'array'
  /**
   * 是否必需
   */
  required?: boolean
  /**
   * 字段描述
   */
  description?: string
}

/**
 * 节点类型元数据：定义每种节点类型的输入和输出字段
 */
export interface NodeTypeMetadata {
  /**
   * 节点类型
   */
  type: Node['type']
  /**
   * 输入字段列表（可绑定的字段）
   */
  inputFields: NodeFieldDefinition[]
  /**
   * 输出字段列表（可被绑定的字段）
   */
  outputFields: NodeFieldDefinition[]
}

/**
 * Workflow 表单（前端编辑格式）
 */
export interface WorkflowForm {
  id?: number
  name: string
  description?: string
  version?: string
  nodes: Node[]
  edges: WorkflowEdge[]
  config: WorkflowConfig
}

