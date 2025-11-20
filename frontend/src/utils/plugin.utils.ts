/**
 * 插件相关工具函数
 */
import type { Plugin, PluginForm, OpenAPISpec, PluginConfig } from '@/types/plugin'

/**
 * 将后端实体转换为前端表单模型
 * 智能处理：如果后端返回的是对象，直接使用；如果是字符串，则解析
 */
export function pluginToForm(plugin: Plugin): PluginForm {
  // 如果 openapiSpec 已经是对象，直接使用；否则解析字符串
  const openapiSpec: OpenAPISpec = typeof plugin.openapiSpec === 'string' 
    ? JSON.parse(plugin.openapiSpec || '{}') as OpenAPISpec
    : plugin.openapiSpec

  // 如果 config 已经是对象，直接使用；否则解析字符串
  const config: PluginConfig = typeof plugin.config === 'string'
    ? JSON.parse(plugin.config || '{}') as PluginConfig
    : plugin.config

  return {
    id: plugin.id,
    name: plugin.name,
    description: plugin.description,
    type: plugin.type,
    openapiSpec,
    config,
    status: plugin.status
  }
}

/**
 * 将前端表单模型转换为后端实体
 */
export function formToPlugin(form: PluginForm): Plugin {
  return {
    id: form.id,
    name: form.name,
    description: form.description,
    type: form.type,
    openapiSpec: JSON.stringify(form.openapiSpec),
    config: JSON.stringify(form.config),
    status: form.status
  }
}

/**
 * 验证 OpenAPI 规范
 */
export function validateOpenAPISpec(spec: OpenAPISpec): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  if (!spec.openapi) {
    errors.push('缺少 openapi 版本')
  }

  if (!spec.info || !spec.info.title) {
    errors.push('缺少 info.title')
  }

  if (!spec.info || !spec.info.version) {
    errors.push('缺少 info.version')
  }

  if (!spec.paths || Object.keys(spec.paths).length === 0) {
    errors.push('至少需要一个 path')
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * 创建默认的 OpenAPI 规范
 * 
 * 这个规范是给大模型使用的"API 说明书"，告诉大模型：
 * 1. 有哪些可用的 API 端点（paths）
 * 2. 每个端点需要什么参数、返回什么数据
 * 3. API 服务器地址在哪里（servers）
 * 
 * 工作流程：
 * 1. 用户配置插件时：填写 OpenAPI 规范（定义有哪些 API）
 * 2. 用户与大模型对话时：大模型根据用户需求，从 paths 中选择合适的端点
 * 3. 实际调用时：大模型组合 server URL + path 构建完整请求
 *    例如：server="https://api.example.com" + path="/users" = "https://api.example.com/users"
 * 
 * servers: API 服务器地址
 *   - 通常只有一个（用户配置的 API 地址）
 *   - 如果有多个，大模型会选择第一个，或者根据描述选择
 * 
 * paths: API 端点集合（一个插件可以包含多个功能）
 *   - 一个插件的一套 spec 可以定义多个 paths（多个功能端点）
 *   - 大模型会根据用户需求，从这些 paths 中智能选择调用哪个端点
 *   - 例如：用户说"获取用户列表"，大模型会选择 GET /users
 *   - 例如：用户说"创建订单"，大模型会选择 POST /orders
 *   - 所以一个插件可以负责多个功能，只要在 paths 中定义多个端点即可
 */
export function createDefaultOpenAPISpec(): OpenAPISpec {
  return {
    openapi: '3.0.0',
    info: {
      title: '',
      description: '',
      version: '1.0.0'
    },
    servers: [
      {
        url: '',
        description: 'API服务器地址'
      }
    ],
    paths: {}
  }
}

/**
 * 创建默认的插件配置
 */
export function createDefaultPluginConfig(): PluginConfig {
  return {
    timeout: 30000,
    retry: 3,
    headers: {}
  }
}

