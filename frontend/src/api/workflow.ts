import request from '@/utils/request'
import type {
  BackendWorkflow,
  BackendWorkflowRequest,
  WorkflowExecuteRequest,
  WorkflowExecutionResponse,
} from '@/types/api'
import type { WorkflowForm } from '@/types/workflow'

/**
 * 将后端 Workflow 转换为前端可编辑的 WorkflowForm
 */
function transformWorkflow(backend: BackendWorkflow): WorkflowForm {
  const definition = backend.definition || { nodes: [], edges: [], config: {} }

  return {
    id: backend.id,
    name: backend.name,
    description: backend.description,
    version: (definition.config && definition.config.version) || undefined,
    nodes: definition.nodes || [],
    edges: definition.edges || [],
    config: definition.config || {},
  }
}

/**
 * 将前端 WorkflowForm 转换为后端请求体
 */
function toBackendRequest(form: WorkflowForm): BackendWorkflowRequest {
  return {
    name: form.name,
    description: form.description,
    definition: {
      nodes: form.nodes,
      edges: form.edges,
      config: form.config || {},
    },
    status: 'draft',
  }
}

export const workflowApi = {
  /**
   * 获取工作流列表
   */
  async getList(): Promise<WorkflowForm[]> {
    const data = await request.get<BackendWorkflow[]>('/workflows/')
    if (!Array.isArray(data)) return []
    return data.map(transformWorkflow)
  },

  /**
   * 获取工作流详情
   */
  async getDetail(id: number): Promise<WorkflowForm> {
    const data = await request.get<BackendWorkflow>(`/workflows/${id}/`)
    return transformWorkflow(data)
  },

  /**
   * 创建工作流
   */
  async create(form: WorkflowForm): Promise<WorkflowForm> {
    const payload = toBackendRequest(form)
    const data = await request.post<BackendWorkflow>('/workflows/', payload)
    return transformWorkflow(data)
  },

  /**
   * 更新工作流
   */
  async update(id: number, form: WorkflowForm): Promise<WorkflowForm> {
    const payload = toBackendRequest(form)
    const data = await request.put<BackendWorkflow>(`/workflows/${id}/`, payload)
    return transformWorkflow(data)
  },

  /**
   * 执行工作流（主要用于调试）
   */
  async execute(id: number, input: WorkflowExecuteRequest['input_data']): Promise<WorkflowExecutionResponse> {
    const data = await request.post<WorkflowExecutionResponse>(`/workflows/${id}/execute/`, {
      input_data: input,
    } as WorkflowExecuteRequest)
    return data
  },
}


