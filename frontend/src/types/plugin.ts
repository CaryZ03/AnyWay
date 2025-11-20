/**
 * OpenAPI 3.0 规范类型定义
 * 基于用户提供的插件定义标准
 */

// ========== OpenAPI 核心类型 ==========

/**
 * OpenAPI 规范主接口
 */
export interface OpenAPISpec {
  openapi: string  // "3.0.0"
  info: Info
  servers?: Server[]
  paths: Paths
  components?: Components
  security?: SecurityRequirement[]
  tags?: Tag[]
}

/**
 * API 信息
 */
export interface Info {
  title: string
  description?: string
  version: string
}

/**
 * 服务器信息
 * 
 * 定义 API 的服务器地址，大模型会使用这个地址来构建完整的 API 请求 URL
 * 
 * 使用场景：
 * - 插件配置时：用户填写 API 的基础地址（如 https://api.example.com）
 * - 大模型调用时：会使用 servers[0].url 作为基础 URL
 * - 完整请求 = server.url + path，例如：
 *   server.url = "https://api.example.com/v1"
 *   path = "/users"
 *   最终请求 = "https://api.example.com/v1/users"
 * 
 * 为什么可以有多个？
 * - 通常只有一个（用户配置的 API 地址）
 * - 如果有多个，大模型会选择第一个，或根据 description 选择
 */
export interface Server {
  url: string
  description?: string
}

/**
 * 路径集合（key 是路径，value 是路径项）
 * 
 * 定义 API 的所有可用端点，大模型会根据用户需求智能选择调用哪个端点
 * 
 * 工作流程：
 * 1. 用户配置插件：定义所有可用的 API 端点（如 /users、/products、/orders）
 * 2. 用户与大模型对话：用户说"帮我获取用户列表"
 * 3. 大模型分析：查看 paths，找到匹配的端点（GET /users）
 * 4. 大模型调用：组合 server.url + "/users" 发送请求
 * 
 * 为什么可以有多个？
 * - 一个 API 通常有多个功能，每个功能对应一个端点
 * - 大模型需要知道所有可用的端点，才能根据用户需求选择正确的
 * 
 * 示例：
 * {
 *   "/users": { 
 *     get: { summary: "获取用户列表", ... },      // 大模型看到这个，知道可以获取用户列表
 *     post: { summary: "创建用户", ... }          // 大模型看到这个，知道可以创建用户
 *   },
 *   "/users/{id}": { 
 *     get: { summary: "获取单个用户", ... }       // 大模型看到这个，知道可以获取特定用户
 *   },
 *   "/orders": { 
 *     post: { summary: "创建订单", ... }          // 大模型看到这个，知道可以创建订单
 *   }
 * }
 */
export interface Paths {
  [path: string]: PathItem
}

/**
 * 路径项（包含各种 HTTP 方法）
 */
export interface PathItem {
  get?: Operation
  post?: Operation
  put?: Operation
  delete?: Operation
  patch?: Operation
  head?: Operation
  options?: Operation
  trace?: Operation
}

/**
 * 操作（Operation）
 */
export interface Operation {
  operationId?: string
  summary?: string
  description?: string
  requestBody?: RequestBody
  responses: Responses
}

/**
 * 请求体
 */
export interface RequestBody {
  required?: boolean
  content: Content
}

/**
 * 内容类型（key 是 content-type，如 "application/json"）
 */
export interface Content {
  [contentType: string]: MediaType
}

/**
 * 媒体类型
 */
export interface MediaType {
  schema?: Schema
}


/**
 * 响应集合（key 是状态码，如 "200"）
 */
export interface Responses {
  [statusCode: string]: Response
}

/**
 * 响应
 */
export interface Response {
  description: string
  content?: Content
}

/**
 * JSON Schema（用于描述数据结构）
 */
export interface Schema {
  type?: 'string' | 'number' | 'integer' | 'boolean' | 'object' | 'array' | 'null'
  required?: string[]
  properties?: Record<string, Schema>
}

// ========== 插件相关类型 ==========

/**
 * 插件配置
 */
export interface PluginConfig {
  apiKey?: string
  baseUrl?: string
}

/**
 * 插件实体（后端返回格式）
 * 
 * 一个插件 = 一个 OpenAPI 规范 = 可以负责多个功能
 * 
 * 工作原理：
 * - 一个插件只有一套 openapiSpec（一个 OpenAPI 规范）
 * - 但一个 OpenAPI 规范可以定义多个 paths（多个 API 端点）
 * - 大模型会根据用户需求，从这些 paths 中智能选择要调用的端点
 * 
 * 示例：一个"电商插件"可以包含：
 *   - GET /products（获取商品列表）
 *   - GET /products/{id}（获取商品详情）
 *   - POST /orders（创建订单）
 *   - GET /orders/{id}（查询订单）
 *   等多个功能端点，大模型会根据用户需求选择调用哪个
 * 
 * 注意：如果后端直接返回解析好的对象，openapiSpec 和 config 就是对象类型
 * 如果后端返回的是字符串，则需要在转换时解析
 */
export interface Plugin {
  id?: number
  name: string
  description?: string
  type: 'builtin' | 'custom'
  openapiSpec: string | OpenAPISpec  // 可能是 JSON 字符串，也可能是已解析的对象
  config: string | PluginConfig      // 可能是 JSON 字符串，也可能是已解析的对象
  status: 'enabled' | 'disabled'
  createdAt?: string
  updatedAt?: string
}

/**
 * 插件表单（前端编辑格式）
 * 
 * 一个插件表单对应一个插件，包含一套 OpenAPI 规范
 * 这套规范可以定义多个功能端点，大模型会从中选择使用
 */
export interface PluginForm {
  id?: number
  name: string
  description?: string
  type: 'builtin' | 'custom'
  openapiSpec: OpenAPISpec  // 解析后的对象，包含多个 paths（多个功能端点）
  config: PluginConfig      // 解析后的对象
  status: 'enabled' | 'disabled'
}

