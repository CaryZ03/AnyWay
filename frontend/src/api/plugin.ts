import request from '@/utils/request'
import type { Plugin, PluginForm, PluginConfig, OpenAPISpec } from '@/types/plugin'
import type {
  BackendPlugin,
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
 * 注意：列表接口可能不包含 openapi_spec，此时 openapiSpec 为 undefined
 */
function transformPlugin(backend: BackendPlugin): Plugin {
  // 处理 openapi_spec（可能不存在）
  let openapiSpec: string | OpenAPISpec | undefined = undefined
  if (backend.openapi_spec !== undefined && backend.openapi_spec !== null) {
    openapiSpec = typeof backend.openapi_spec === 'string'
      ? JSON.parse(backend.openapi_spec)
      : backend.openapi_spec
  }

  // 处理 auth_config（可能不存在）
  let authConfig: any = {}
  if (backend.auth_config !== undefined && backend.auth_config !== null) {
    authConfig = typeof backend.auth_config === 'string'
      ? JSON.parse(backend.auth_config)
      : backend.auth_config
  }

  // 合并 base_url 和 auth_config 到 config
  const config: PluginConfig = {
    baseUrl: backend.base_url || '',
    ...authConfig,
  }

  return {
    id: backend.id,
    name: backend.name,
    description: backend.description,
    type: 'custom', // 后端没有 type 字段，默认为 custom
    openapiSpec, // 如果不存在，为 undefined（后续需要时再获取）
    config,
    status: backend.status,
    createdAt: backend.created_at,
    updatedAt: backend.updated_at,
  }
}

/**
 * 转换前端 PluginForm 到后端请求格式
 * 注意：后端序列化器只需要 openapi_spec 和 status
 * name、description、base_url 会从 openapi_spec 中自动提取
 * auth_config 会从 openapi_spec.auth_config 中提取（如果存在）
 */
function transformPluginRequest(form: PluginForm) {
  return {
    openapi_spec: form.openapiSpec,
    status: form.status || 'enabled',
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
   * 后端只需要 openapi_spec 和 status，其他字段会自动提取
   */
  create: async (form: PluginForm): Promise<Plugin> => {
    const requestData = transformPluginRequest(form)
    const data = await request.post<BackendPlugin>('/plugins/', requestData)
    return transformPlugin(data)
  },

  /**
   * 更新插件
   * 后端只需要 openapi_spec 和 status，其他字段会自动提取和更新
   */
  update: async (id: number, form: Partial<PluginForm>): Promise<Plugin> => {
    const requestData: any = {}
    
    if (form.openapiSpec !== undefined) {
      requestData.openapi_spec = form.openapiSpec
    }
    
    if (form.status !== undefined) {
      requestData.status = form.status
    }

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

