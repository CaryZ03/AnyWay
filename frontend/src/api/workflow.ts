import request from '@/utils/request'
import type {
  BackendWorkflow,
  BackendWorkflowRequest,
  WorkflowExecuteRequest,
  WorkflowExecutionResponse,
} from '@/types/api'
import type { WorkflowForm, Node, WorkflowEdge } from '@/types/workflow'
import type { GraphNode, GraphEdge } from '@vue-flow/core'

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
    status: backend.status,
    createdAt: backend.created_at,
    updatedAt: backend.updated_at,
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
  async getDetail(id: string): Promise<WorkflowForm> {
    console.log('getDetail', id)
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
  async update(id: string, form: WorkflowForm): Promise<WorkflowForm> {
    const payload = toBackendRequest(form)
    const data = await request.put<BackendWorkflow>(`/workflows/${id}/`, payload)
    return transformWorkflow(data)
  },

  /**
   * 执行工作流（主要用于调试）
   */
  async execute(id: string, input: WorkflowExecuteRequest['input_data']): Promise<WorkflowExecutionResponse> {
    const data = await request.post<WorkflowExecutionResponse>(`/workflows/${id}/execute/`, {
      input_data: input,
    } as WorkflowExecuteRequest)
    return data
  },

  /**
   * 删除工作流（逻辑删除）
   */
  async delete(id: string): Promise<void> {
    await request.delete(`/workflows/${id}/`)
  },

  /**
   * 获取工作流执行历史列表
   */
  async getExecutions(id: string): Promise<WorkflowExecutionResponse[]> {
    const data = await request.get<WorkflowExecutionResponse[]>(`/workflows/${id}/executions/`)
    return Array.isArray(data) ? data : []
  },

  /**
   * 获取工作流执行详情
   */
  async getExecutionDetail(workflowId: string, executionId: number): Promise<WorkflowExecutionResponse> {
    const data = await request.get<WorkflowExecutionResponse>(`/workflows/${workflowId}/executions/${executionId}/`)
    return data
  },
}

/**
 * 将 VueFlow 的 GraphNode 转换为业务层的 Node
 */
export function graphNodeToNode(graphNode: GraphNode): Node {
  const node: any = {
    id: graphNode.id,
    type: graphNode.type as Node['type'],
    position: graphNode.position,
    data: graphNode.data,
  }
  return node as Node
}

/**
 * 将业务层的 Node 转换为 VueFlow 的 GraphNode
 */
export function nodeToGraphNode(node: Node): GraphNode {
  const graphNode: any = {
    id: node.id,
    type: node.type,
    position: node.position || { x: 0, y: 0 },
    data: node.data,
  }
  return graphNode as GraphNode
}

/**
 * 将 VueFlow 的 GraphEdge 转换为业务层的 WorkflowEdge
 */
export function graphEdgeToWorkflowEdge(graphEdge: GraphEdge): WorkflowEdge {
  return {
    id: graphEdge.id,
    source: graphEdge.source,
    target: graphEdge.target,
    condition: (graphEdge.data as any)?.condition,
  }
}

/**
 * 将业务层的 WorkflowEdge 转换为 VueFlow 的 GraphEdge
 */
export function workflowEdgeToGraphEdge(edge: WorkflowEdge): GraphEdge {
  const graphEdge: any = {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: 'default',
    data: edge.condition ? { condition: edge.condition } : undefined,
  }
  return graphEdge as GraphEdge
}


