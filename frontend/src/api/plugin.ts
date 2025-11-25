import request from '@/utils/request'
import type { Plugin, PluginForm, PluginConfig } from '@/types/plugin'
import type {
  BackendPlugin,
  BackendPluginRequest,
} from '@/types/api'

/**
 * Plugin API
 * 后端字段名：snake_case (openapi_spec, base_url, auth_config, created_at, updated_at)
 * 前端字段名：camelCase (openapiSpec, config, createdAt, updatedAt)
 * 
 * 注意：后端使用 base_url 和 auth_config 分离，前端使用 config 对象包含两者
 */

/**
 * 转换后端 Plugin 到前端 Plugin
 */
function transformPlugin(backend: BackendPlugin): Plugin {
  const openapiSpec = typeof backend.openapi_spec === 'string'
    ? JSON.parse(backend.openapi_spec)
    : backend.openapi_spec

  const authConfig = typeof backend.auth_config === 'string'
    ? JSON.parse(backend.auth_config)
    : backend.auth_config

  // 合并 base_url 和 auth_config 到 config
  const config: PluginConfig = {
    baseUrl: backend.base_url,
    ...authConfig,
  }

  return {
    id: backend.id,
    name: backend.name,
    description: backend.description,
    type: 'custom', // 后端没有 type 字段，默认为 custom
    openapiSpec,
    config,
    status: backend.status,
    createdAt: backend.created_at,
    updatedAt: backend.updated_at,
  }
}

/**
 * 转换前端 PluginForm 到后端请求格式
 */
function transformPluginRequest(form: PluginForm): BackendPluginRequest {
  // 从 config 中提取 baseUrl 和 auth_config
  const { baseUrl, ...authConfig } = form.config

  return {
    name: form.name,
    description: form.description,
    openapi_spec: form.openapiSpec,
    base_url: baseUrl || '',
    auth_config: authConfig,
    status: form.status,
  }
}

export const pluginApi = {
  /**
   * 获取插件列表
   */
  getList: async (): Promise<Plugin[]> => {
    const data = await request.get<BackendPlugin[]>('/plugins/')
    return Array.isArray(data) ? data.map(transformPlugin) : []
  },

  /**
   * 获取插件详情
   */
  getDetail: async (id: number): Promise<Plugin> => {
    const data = await request.get<BackendPlugin>(`/plugins/${id}/`)
    return transformPlugin(data)
  },

  /**
   * 创建插件
   */
  create: async (form: PluginForm): Promise<Plugin> => {
    const requestData = transformPluginRequest(form)
    const data = await request.post<BackendPlugin>('/plugins/', requestData)
    return transformPlugin(data)
  },

  /**
   * 更新插件
   */
  update: async (id: number, form: Partial<PluginForm>): Promise<Plugin> => {
    const requestData: Partial<BackendPluginRequest> = {}
    
    if (form.name !== undefined) requestData.name = form.name
    if (form.description !== undefined) requestData.description = form.description
    if (form.openapiSpec !== undefined) requestData.openapi_spec = form.openapiSpec
    if (form.config !== undefined) {
      const { baseUrl, ...authConfig } = form.config
      requestData.base_url = baseUrl || ''
      requestData.auth_config = authConfig
    }
    if (form.status !== undefined) requestData.status = form.status

    const data = await request.patch<BackendPlugin>(`/plugins/${id}/`, requestData)
    return transformPlugin(data)
  },

  /**
   * 删除插件
   */
  delete: async (id: number): Promise<void> => {
    await request.delete(`/plugins/${id}/`)
  },

  /**
   * 启用插件
   */
  enable: async (id: number): Promise<Plugin> => {
    const data = await request.post<BackendPlugin>(`/plugins/${id}/enable/`)
    return transformPlugin(data)
  },

  /**
   * 禁用插件
   */
  disable: async (id: number): Promise<Plugin> => {
    const data = await request.post<BackendPlugin>(`/plugins/${id}/disable/`)
    return transformPlugin(data)
  },
}

