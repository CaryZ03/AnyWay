/**
 * OpenAPI 3.0 规范类型定义
 * 基于 coze-plugin-lite.json 示例文件定义
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
 */
export interface Server {
  url: string
  description?: string
}

/**
 * 路径集合（key 是路径，value 是路径项）
 */
export interface Paths {
  [path: string]: PathItem
}

/**
 * 路径项（只支持 GET 和 POST）
 */
export interface PathItem {
  get?: Operation
  post?: Operation
}

/**
 * 操作（Operation）
 */
export interface Operation {
  operationId: string
  summary?: string
  description?: string
  tags?: string[]
  parameters?: Parameter[]
  requestBody?: RequestBody
  responses: Responses
}

/**
 * 参数定义
 */
export interface Parameter {
  name: string
  in: 'query' | 'header' | 'path' | 'cookie'
  description?: string
  required?: boolean
  schema?: Schema
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
  example?: any
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
  description?: string
  example?: any
  enum?: (string | number)[]
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
  timeout?: number
  retry?: number
  headers?: Record<string, string>
}

/**
 * 插件实体（后端返回格式）
 * 注意：列表接口可能不返回 openapiSpec，只有详情接口返回完整信息
 */
export interface Plugin {
  id?: number
  name: string
  description?: string
  type: 'builtin' | 'custom'
  openapiSpec?: string | OpenAPISpec  // 列表接口可能没有，详情接口有。可能是 JSON 字符串，也可能是已解析的对象
  config?: string | PluginConfig      // 列表接口可能没有。可能是 JSON 字符串，也可能是已解析的对象
  status: 'enabled' | 'disabled'
  createdAt?: string
  updatedAt?: string
}

/**
 * 插件表单（前端编辑格式）
 */
export interface PluginForm {
  id?: number
  name: string
  description?: string
  type: 'builtin' | 'custom'
  openapiSpec: OpenAPISpec
  config: PluginConfig
  status: 'enabled' | 'disabled'
}
