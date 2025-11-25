import request from '@/utils/request'
import type { Workflow, WorkflowForm } from '@/types/workflow'
import type {
  BackendWorkflow,
  BackendWorkflowRequest,
  WorkflowExecuteRequest,
  WorkflowExecutionResponse,
} from '@/types/api'

/**
 * Workflow API
 * 后端字段名：snake_case (definition, created_at, updated_at)
 * 前端字段名：camelCase (nodes, edges, config, createdAt, updatedAt)
 * 
 * 注意：后端使用 definition 字段存储整个工作流定义（包含 nodes, edges, config）
 * 前端使用分离的 nodes, edges, config 字段
 */

/**
 * 转换后端 Workflow 到前端 Workflow
 */
function transformWorkflow(backend: BackendWorkflow): Workflow {
  const definition = backend.definition || { nodes: [], edges: [], config: {} }
  return {
    id: backend.id,
    name: backend.name,
    description: backend.description,
    version: undefined, // 后端没有 version 字段
    nodes: definition.nodes || [],
    edges: definition.edges || [],
    config: definition.config || {},
    createdAt: backend.created_at,
    updatedAt: backend.updated_at,
  }
}

/**
 * 转换前端 WorkflowForm 到后端请求格式
 */
function transformWorkflowRequest(form: WorkflowForm): BackendWorkflowRequest {
  return {
    name: form.name,
    description: form.description,
    definition: {
      nodes: form.nodes,
      edges: form.edges,
      config: form.config,
    },
    status: 'draft', // 默认状态
  }
}

export const workflowApi = {
  /**
   * 获取工作流列表
   */
  getList: async (): Promise<Workflow[]> => {
    const data = await request.get<BackendWorkflow[]>('/workflows/')
    return Array.isArray(data) ? data.map(transformWorkflow) : []
  },

  /**
   * 获取工作流详情
   */
  getDetail: async (id: number): Promise<Workflow> => {
    const data = await request.get<BackendWorkflow>(`/workflows/${id}/`)
    return transformWorkflow(data)
  },

  /**
   * 创建工作流
   */
  create: async (form: WorkflowForm): Promise<Workflow> => {
    const requestData = transformWorkflowRequest(form)
    const data = await request.post<BackendWorkflow>('/workflows/', requestData)
    return transformWorkflow(data)
  },

  /**
   * 更新工作流
   */
  update: async (id: number, form: Partial<WorkflowForm>): Promise<Workflow> => {
    const requestData: Partial<BackendWorkflowRequest> = {}
    
    if (form.name !== undefined) requestData.name = form.name
    if (form.description !== undefined) requestData.description = form.description
    if (form.nodes !== undefined || form.edges !== undefined || form.config !== undefined) {
      requestData.definition = {
        nodes: form.nodes || [],
        edges: form.edges || [],
        config: form.config || {},
      }
    }

    const data = await request.patch<BackendWorkflow>(`/workflows/${id}/`, requestData)
    return transformWorkflow(data)
  },

  /**
   * 删除工作流
   */
  delete: async (id: number): Promise<void> => {
    await request.delete(`/workflows/${id}/`)
  },

  /**
   * 执行工作流
   */
  execute: async (id: number, inputData: Record<string, any>): Promise<WorkflowExecutionResponse> => {
    const requestData: WorkflowExecuteRequest = { input_data: inputData }
    return await request.post<WorkflowExecutionResponse>(`/workflows/${id}/execute/`, requestData)
  },

  /**
   * 获取执行历史
   */
  getExecutions: async (id: number): Promise<WorkflowExecutionResponse[]> => {
    const data = await request.get<WorkflowExecutionResponse[]>(`/workflows/${id}/executions/`)
    return Array.isArray(data) ? data : []
  },
}

