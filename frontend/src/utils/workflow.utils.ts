/**
 * 工作流工具函数
 */
import type {
  NodeTypeMetadata,
  NodeFieldDefinition,
  Node,
  WorkflowEdge,
  FieldBinding,
} from '@/types/workflow'

/**
 * 节点类型元数据定义
 * 定义每种节点类型的输入和输出字段
 */
export const NODE_TYPE_METADATA: Record<string, NodeTypeMetadata> = {
  start: {
    type: 'start',
    inputFields: [],
    outputFields: [
      {
        name: 'input_text',
        label: '输入文本',
        type: 'string',
        description: '用户输入的文本',
      },
    ],
  },
  llm: {
    type: 'llm',
    inputFields: [
      {
        name: 'prompt',
        label: '提示词',
        type: 'string',
        required: true,
        description: 'LLM提示词，支持变量替换',
      },
    ],
    outputFields: [
      {
        name: 'output_text',
        label: '输出文本',
        type: 'string',
        description: 'LLM生成的文本',
      },
    ],
  },
  http: {
    type: 'http',
    inputFields: [
      {
        name: 'url',
        label: '请求URL',
        type: 'string',
        required: true,
        description: 'HTTP请求URL，支持变量替换',
      },
      {
        name: 'headers',
        label: '请求头',
        type: 'object',
        description: 'HTTP请求头，支持变量替换',
      },
      {
        name: 'body',
        label: '请求体',
        type: 'object',
        description: 'HTTP请求体（POST），支持变量替换',
      },
    ],
    outputFields: [
      {
        name: 'response',
        label: '响应数据',
        type: 'object',
        description: 'HTTP响应数据',
      },
    ],
  },
  knowledge: {
    type: 'knowledge',
    inputFields: [
      {
        name: 'query',
        label: '查询文本',
        type: 'string',
        required: true,
        description: '知识库查询文本，支持变量替换',
      },
    ],
    outputFields: [
      {
        name: 'results',
        label: '检索结果',
        type: 'array',
        description: '知识库检索结果列表',
      },
    ],
  },
  intent: {
    type: 'intent',
    inputFields: [
      {
        name: 'input_text',
        label: '输入文本',
        type: 'string',
        required: true,
        description: '意图识别输入文本，支持变量替换',
      },
    ],
    outputFields: [
      {
        name: 'intent',
        label: '识别意图',
        type: 'string',
        description: '识别出的意图类别',
      },
    ],
  },
  string: {
    type: 'string',
    inputFields: [
      {
        name: 'input_string',
        label: '输入字符串',
        type: 'string',
        required: true,
        description: '字符串处理输入，支持变量替换',
      },
    ],
    outputFields: [
      {
        name: 'output_string',
        label: '输出字符串',
        type: 'string',
        description: '处理后的字符串',
      },
    ],
  },
  end: {
    type: 'end',
    inputFields: [
      {
        name: 'output_text',
        label: '输出文本',
        type: 'string',
        description: '最终输出文本',
      },
    ],
    outputFields: [],
  },
}

/**
 * 获取节点类型的元数据
 */
export function getNodeTypeMetadata(nodeType: string): NodeTypeMetadata | undefined {
  return NODE_TYPE_METADATA[nodeType]
}

/**
 * 获取节点的输入字段列表
 */
export function getNodeInputFields(nodeType: string): NodeFieldDefinition[] {
  return getNodeTypeMetadata(nodeType)?.inputFields || []
}

/**
 * 获取节点的输出字段列表
 */
export function getNodeOutputFields(nodeType: string): NodeFieldDefinition[] {
  return getNodeTypeMetadata(nodeType)?.outputFields || []
}

/**
 * 将字段绑定转换为变量格式
 * 例如：{ sourceNodeId: 'node1', sourceField: 'output_text' } -> '{{node1.output_text}}'
 */
export function bindingToVariable(binding: { sourceNodeId: string; sourceField: string }): string {
  return `{{${binding.sourceNodeId}.${binding.sourceField}}}`
}

/**
 * 从变量格式解析字段绑定
 * 例如：'{{node1.output_text}}' -> { sourceNodeId: 'node1', sourceField: 'output_text' }
 */
export function variableToBinding(variable: string): { sourceNodeId: string; sourceField: string } | null {
  const match = variable.match(/\{\{(\w+)\.(\w+)\}\}/)
  if (!match) return null
  return {
    sourceNodeId: match[1],
    sourceField: match[2],
  }
}

/**
 * 检查字符串是否包含变量
 */
export function hasVariable(text: string): boolean {
  return /\{\{\w+\.\w+\}\}/.test(text)
}

/**
 * 替换字符串中的变量
 * 将变量格式替换为实际值
 */
export function replaceVariables(
  text: string,
  variables: Record<string, any>
): string {
  return text.replace(/\{\{(\w+)\.(\w+)\}\}/g, (match, nodeId, fieldName) => {
    const value = variables[nodeId]?.[fieldName]
    return value !== undefined ? String(value) : match
  })
}

/**
 * 应用字段绑定到节点和边
 * 将绑定关系更新到 Edge 的 bindings 字段，并将目标节点的字段值设置为变量格式
 * 
 * 注意：一个目标节点可能有多个上游节点，每个上游节点对应一条边
 * 所以需要为每条边分别管理绑定关系
 */
export function applyFieldBindings(
  nodes: Node[],
  edges: WorkflowEdge[],
  targetNodeId: string,
  bindings: FieldBinding[]
): { nodes: Node[]; edges: WorkflowEdge[] } {
  // 复制数组以避免直接修改
  const updatedNodes = nodes.map(n => ({ ...n, data: { ...n.data } }))
  const updatedEdges = edges.map(e => ({
    ...e,
    bindings: e.bindings ? [...e.bindings] : [],
  }))
  
  // 找到目标节点
  const targetNodeIndex = updatedNodes.findIndex(n => n.id === targetNodeId)
  if (targetNodeIndex === -1) {
    return { nodes, edges }
  }
  
  const targetNode = updatedNodes[targetNodeIndex]
  const targetNodeData = targetNode.data as any
  
  // 按源节点分组绑定
  const bindingsBySource = new Map<string, FieldBinding[]>()
  bindings.forEach(binding => {
    if (!bindingsBySource.has(binding.sourceNodeId)) {
      bindingsBySource.set(binding.sourceNodeId, [])
    }
    bindingsBySource.get(binding.sourceNodeId)!.push(binding)
  })
  
  // 为每个源节点更新或创建边
  bindingsBySource.forEach((sourceBindings, sourceNodeId) => {
    // 查找或创建边
    let edgeIndex = updatedEdges.findIndex(
      e => e.source === sourceNodeId && e.target === targetNodeId
    )
    
    let edge: WorkflowEdge
    if (edgeIndex === -1) {
      // 创建新边
      edge = {
        id: `e-${sourceNodeId}-${targetNodeId}`,
        source: sourceNodeId,
        target: targetNodeId,
        bindings: [],
      }
      updatedEdges.push(edge)
      edgeIndex = updatedEdges.length - 1
    } else {
      edge = updatedEdges[edgeIndex]
    }
    
    // 更新该边的绑定
    sourceBindings.forEach(binding => {
      const existingIndex = edge.bindings!.findIndex(
        b => b.targetField === binding.targetField
      )
      
      if (existingIndex !== -1) {
        edge.bindings![existingIndex] = binding
      } else {
        edge.bindings!.push(binding)
      }
      
      // 更新目标节点的字段值为变量格式
      targetNodeData[binding.targetField] = bindingToVariable({
        sourceNodeId: binding.sourceNodeId,
        sourceField: binding.sourceField,
      })
    })
    
    // 移除已取消的绑定（只保留当前配置的绑定）
    const sourceBindingFields = new Set(sourceBindings.map(b => b.targetField))
    edge.bindings = edge.bindings!.filter(b => sourceBindingFields.has(b.targetField))
    
    updatedEdges[edgeIndex] = edge
  })
  
  // 清理：移除所有已取消的绑定（如果某个字段不再绑定，需要从节点数据中移除变量格式）
  const allBindingFields = new Set(bindings.map(b => b.targetField))
  const inputFields = getNodeInputFields(targetNode.type)
  
  inputFields.forEach(field => {
    if (!allBindingFields.has(field.name)) {
      // 如果字段值包含变量格式但不是当前绑定，清除它
      const currentValue = targetNodeData[field.name]
      if (typeof currentValue === 'string' && currentValue.includes('{{')) {
        // 检查是否是已取消的绑定
        const match = currentValue.match(/\{\{(\w+)\.(\w+)\}\}/)
        if (match) {
          // 清除变量格式，保留为空字符串或原值（根据业务需求）
          // 这里选择清除，用户需要手动输入
          delete targetNodeData[field.name]
        }
      }
    }
  })
  
  return { nodes: updatedNodes, edges: updatedEdges }
}

