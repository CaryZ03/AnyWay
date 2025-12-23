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
 * 注意：后端节点使用 config 字段，前端使用 data 字段，需要转换
 */
function transformWorkflow(backend: BackendWorkflow): WorkflowForm {
  const definition = backend.definition || { nodes: [], edges: [], config: {} }

  // 转换节点：将 config 字段转换为 data 字段
  const frontendNodes = (definition.nodes || []).map((node: any) => {
    const frontendNode: any = {
      id: node.id,
      type: node.type,
    }
    
    // 如果节点有 position，保留它
    if (node.position) {
      frontendNode.position = node.position
    }
    
    // 将 config 字段转换为 data 字段
    if (node.config) {
      frontendNode.data = node.config
    } else if (node.data) {
      // 如果节点已经有 data 字段（可能是前端格式），直接使用
      frontendNode.data = node.data
    } else {
      frontendNode.data = {}
    }
    
    return frontendNode
  })

  return {
    id: backend.id,
    name: backend.name,
    description: backend.description,
    version: (definition.config && definition.config.version) || undefined,
    nodes: frontendNodes,
    edges: definition.edges || [],
    config: definition.config || {},
    status: backend.status,
    createdAt: backend.created_at,
    updatedAt: backend.updated_at,
  }
}

/**
 * 将前端 WorkflowForm 转换为后端请求体
 * 注意：后端期望节点使用 config 字段，前端使用 data 字段，需要转换
 */
function toBackendRequest(form: WorkflowForm): BackendWorkflowRequest {
  // 转换节点：将 data 字段转换为 config 字段，并添加 name 字段
  const backendNodes = form.nodes.map(node => {
    const backendNode: any = {
      id: node.id,
      type: node.type,
    }
    
    // 如果节点有 position，保留它（虽然后端可能不使用）
    if (node.position) {
      backendNode.position = node.position
    }
    
    // 将 data 字段转换为 config 字段
    if (node.data) {
      backendNode.config = node.data
      // 从 config 中提取 name 字段（如果存在）
      if (node.data.name) {
        backendNode.name = node.data.name
      }
    } else if ((node as any).config) {
      // 如果节点已经有 config 字段（从后端返回的数据），直接使用
      backendNode.config = (node as any).config
      if ((node as any).name) {
        backendNode.name = (node as any).name
      }
    } else {
      backendNode.config = {}
    }
    
    return backendNode
  })
  
  return {
    name: form.name,
    description: form.description,
    definition: {
      nodes: backendNodes,
      edges: form.edges,
      config: form.config || {},
    },
    status: form.status || 'draft',
  }
}

// ========== 后端 API（保留原有接口） ==========

/**
 * 后端 Workflow API
 * 用于调用后端接口
 */
export const backendWorkflowApi = {
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
    console.log('data', data)
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
    const data = await request.patch<BackendWorkflow>(`/workflows/${id}/`, payload)
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

// ========== 本地存储 API ==========

/**
 * 本地存储文件路径（相对于public目录）
 */
const LOCAL_STORAGE_FILE = '/workflows.json'

/**
 * 从本地文件读取workflow数据
 */
async function readLocalWorkflows(): Promise<BackendWorkflow[]> {
  try {
    const response = await fetch(LOCAL_STORAGE_FILE)
    if (!response.ok) {
      // 如果文件不存在，返回空数组
      return []
    }
    const data = await response.json()
    return Array.isArray(data) ? data : []
  } catch (error) {
    console.warn('读取本地workflow文件失败，返回空数组:', error)
    return []
  }
}

/**
 * 保存workflow数据到localStorage
 * 注意：由于浏览器安全限制，无法直接写入文件
 * 这里使用localStorage作为主要存储方式
 */
function saveLocalWorkflows(workflows: BackendWorkflow[]): void {
  try {
    // 保存到localStorage
    localStorage.setItem('workflows_data', JSON.stringify(workflows))
    console.log('已保存workflow数据到localStorage，共', workflows.length, '个工作流')
  } catch (error) {
    console.error('保存workflow数据失败:', error)
    throw error
  }
}

/**
 * 从localStorage读取workflow数据（优先）
 */
function readFromLocalStorage(): BackendWorkflow[] {
  try {
    const data = localStorage.getItem('workflows_data')
    if (data) {
      return JSON.parse(data)
    }
  } catch (error) {
    console.warn('从localStorage读取workflow数据失败:', error)
  }
  return []
}

/**
 * 本地存储 Workflow API
 * 使用 localStorage 作为存储方式
 */
export const localWorkflowApi = {
  /**
   * 获取工作流列表
   */
  async getList(): Promise<WorkflowForm[]> {
    // 优先从localStorage读取，如果没有则尝试从文件读取
    let workflows = readFromLocalStorage()
    if (workflows.length === 0) {
      workflows = await readLocalWorkflows()
    }
    if (!Array.isArray(workflows)) return []
    return workflows.map(transformWorkflow)
  },

  /**
   * 获取工作流详情
   */
  async getDetail(id: string): Promise<WorkflowForm> {
    console.log('getDetail', id)
    // 从localStorage或文件读取
    let workflows = readFromLocalStorage()
    if (workflows.length === 0) {
      workflows = await readLocalWorkflows()
    }
    const workflow = workflows.find(w => w.id === id)
    if (!workflow) {
      throw new Error(`工作流 ${id} 不存在`)
    }
    console.log('data', workflow)
    return transformWorkflow(workflow)
  },

  /**
   * 创建工作流
   */
  async create(form: WorkflowForm): Promise<WorkflowForm> {
    const payload = toBackendRequest(form)
    // 生成ID
    const newId = `workflow-${Date.now()}`
    const newWorkflow: BackendWorkflow = {
      ...payload,
      id: newId,
      status: payload.status || 'draft',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    
    // 读取现有数据
    let workflows = readFromLocalStorage()
    if (workflows.length === 0) {
      workflows = await readLocalWorkflows()
    }
    
    // 添加新工作流
    workflows.push(newWorkflow)
    
    // 保存
    saveLocalWorkflows(workflows)
    
    return transformWorkflow(newWorkflow)
  },

  /**
   * 更新工作流
   */
  async update(id: string, form: WorkflowForm): Promise<WorkflowForm> {
    const payload = toBackendRequest(form)
    
    // 读取现有数据
    let workflows = readFromLocalStorage()
    if (workflows.length === 0) {
      workflows = await readLocalWorkflows()
    }
    
    // 查找并更新
    const index = workflows.findIndex(w => w.id === id)
    if (index === -1) {
      throw new Error(`工作流 ${id} 不存在`)
    }
    
    const existingWorkflow = workflows[index]
    if (!existingWorkflow) {
      throw new Error(`工作流 ${id} 不存在`)
    }
    
    const updatedWorkflow: BackendWorkflow = {
      ...existingWorkflow,
      ...payload,
      id: id,
      status: payload.status || existingWorkflow.status || 'draft',
      updated_at: new Date().toISOString(),
    }
    
    workflows[index] = updatedWorkflow
    
    // 保存
    saveLocalWorkflows(workflows)
    
    return transformWorkflow(updatedWorkflow)
  },

  /**
   * 执行工作流（主要用于调试）
   */
  async execute(id: string, input: WorkflowExecuteRequest['input_data']): Promise<WorkflowExecutionResponse> {
    // 暂时返回模拟数据
    console.warn('执行工作流功能暂时不可用（使用本地存储模式）')
    return {
      id: Date.now(),
      workflow: parseInt(id) || 0,
      input_data: input,
      output_data: {},
      status: 'completed',
      node_status: {},
      created_at: new Date().toISOString(),
    }
  },

  /**
   * 删除工作流（逻辑删除）
   */
  async delete(workflowId: string): Promise<void> {
    // 读取现有数据
    let workflows = readFromLocalStorage()
    if (workflows.length === 0) {
      workflows = await readLocalWorkflows()
    }
    
    // 过滤掉要删除的工作流
    const filtered = workflows.filter(w => w.id !== workflowId)
    
    if (filtered.length === workflows.length) {
      throw new Error(`工作流 ${workflowId} 不存在`)
    }
    
    // 保存
    saveLocalWorkflows(filtered)
  },

  /**
   * 获取工作流执行历史列表
   */
  async getExecutions(_workflowId: string): Promise<WorkflowExecutionResponse[]> {
    // 暂时返回空数组
    console.warn('获取执行历史功能暂时不可用（使用本地存储模式）')
    return []
  },

  /**
   * 获取工作流执行详情
   */
  async getExecutionDetail(workflowId: string, executionId: number): Promise<WorkflowExecutionResponse> {
    // 暂时返回模拟数据
    console.warn('获取执行详情功能暂时不可用（使用本地存储模式）')
    return {
      id: executionId,
      workflow: parseInt(workflowId) || 0,
      input_data: {},
      output_data: {},
      status: 'completed',
      node_status: {},
      created_at: new Date().toISOString(),
    }
  },
}

/**
 * 导出workflow数据为JSON文件（可选功能）
 */
export function exportWorkflowsToFile(): void {
  try {
    const workflows = readFromLocalStorage()
    const blob = new Blob([JSON.stringify(workflows, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `workflows-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    console.log('已导出workflow数据到文件')
  } catch (error) {
    console.error('导出workflow数据失败:', error)
    throw error
  }
}

/**
 * 从JSON文件导入workflow数据（可选功能）
 */
export async function importWorkflowsFromFile(file: File): Promise<void> {
  try {
    const text = await file.text()
    const workflows = JSON.parse(text)
    if (!Array.isArray(workflows)) {
      throw new Error('文件格式错误：必须是workflow数组')
    }
    saveLocalWorkflows(workflows)
    console.log('已从文件导入', workflows.length, '个工作流')
  } catch (error) {
    console.error('导入workflow数据失败:', error)
    throw error
  }
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
 * 
 * 注意：GraphNode 的完整类型包含很多运行时计算的属性（如 dimensions, computedPosition 等），
 * 这些属性会在 Vue Flow 渲染时自动计算，所以这里只需要提供基础属性即可。
 * 使用类型断言 `as GraphNode` 来避免类型检查错误。
 */
export function nodeToGraphNode(node: Node): GraphNode {
  // 只提供基础属性，Vue Flow 会在运行时自动计算其他属性（如 dimensions 等）
  return {
    id: node.id,
    type: node.type,
    position: node.position || { x: 0, y: 0 },
    data: node.data || node.config,
  } as GraphNode
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
 * 
 * 注意：GraphEdge 的完整类型包含很多运行时计算的属性（如 sourceNode, targetNode 等），
 * 这些属性会在 Vue Flow 渲染时自动计算，所以这里只需要提供基础属性即可。
 * 使用类型断言 `as GraphEdge` 来避免类型检查错误。
 */
export function workflowEdgeToGraphEdge(edge: WorkflowEdge): GraphEdge {
  // 只提供基础属性，Vue Flow 会在运行时自动计算其他属性（如 sourceNode, targetNode 等）
  return {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: 'default',
    data: edge.condition ? { condition: edge.condition } : {},
  } as GraphEdge
}


