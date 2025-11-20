/**
 * Workflow 相关工具函数
 */
import type {
  Workflow,
  WorkflowForm,
  WorkflowNode,
  WorkflowEdge,
  WorkflowConfig,
  StartNodeConfig,
  LLMNodeConfig,
  PluginNodeConfig,
  ConditionNodeConfig,
  EndNodeConfig,
  StartWorkflowNode,
  LLMWorkflowNode,
  PluginWorkflowNode,
  ConditionWorkflowNode,
  EndWorkflowNode
} from '@/types/workflow'

/**
 * 将后端实体转换为前端表单模型
 * 智能处理：如果后端返回的是对象，直接使用；如果是字符串，则解析
 */
export function workflowToForm(workflow: Workflow): WorkflowForm {
  // 如果 nodes 已经是数组，直接使用；否则解析字符串
  const nodes: WorkflowNode[] = Array.isArray(workflow.nodes)
    ? workflow.nodes
    : JSON.parse(workflow.nodes || '[]') as WorkflowNode[]

  // 如果 edges 已经是数组，直接使用；否则解析字符串
  const edges: WorkflowEdge[] = Array.isArray(workflow.edges)
    ? workflow.edges
    : JSON.parse(workflow.edges || '[]') as WorkflowEdge[]

  // 如果 config 已经是对象，直接使用；否则解析字符串
  const config: WorkflowConfig = typeof workflow.config === 'string'
    ? JSON.parse(workflow.config || '{}') as WorkflowConfig
    : workflow.config

  return {
    id: workflow.id,
    name: workflow.name,
    description: workflow.description,
    version: workflow.version,
    nodes,
    edges,
    config
  }
}

/**
 * 将前端表单模型转换为后端实体
 */
export function formToWorkflow(form: WorkflowForm): Workflow {
  return {
    id: form.id,
    name: form.name,
    description: form.description,
    version: form.version,
    nodes: JSON.stringify(form.nodes),
    edges: JSON.stringify(form.edges),
    config: JSON.stringify(form.config)
  }
}

/**
 * 验证 Workflow
 */
export function validateWorkflow(workflow: WorkflowForm): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  if (!workflow.name || workflow.name.trim() === '') {
    errors.push('名称不能为空')
  }

  if (!Array.isArray(workflow.nodes) || workflow.nodes.length === 0) {
    errors.push('至少需要一个节点')
  }

  // 验证节点
  const nodeIds = new Set<string>()
  let startNodeCount = 0
  let endNodeCount = 0

  for (const node of workflow.nodes) {
    if (!node.id || node.id.trim() === '') {
      errors.push('节点 ID 不能为空')
    } else if (nodeIds.has(node.id)) {
      errors.push(`节点 ID 重复: ${node.id}`)
    } else {
      nodeIds.add(node.id)
    }

    if (!node.type || !['start', 'llm', 'plugin', 'condition', 'end'].includes(node.type)) {
      errors.push(`节点 ${node.id} 的类型无效`)
      continue
    }

    // 统计开始和结束节点
    if (node.type === 'start') {
      startNodeCount++
    } else if (node.type === 'end') {
      endNodeCount++
    }

    // 根据节点类型验证配置
    switch (node.type) {
      case 'start': {
        const startNode = node as StartWorkflowNode
        if (!startNode.config?.input?.userInput) {
          errors.push(`节点 ${node.id} (start) 缺少 input.userInput 配置`)
        }
        break
      }
      case 'llm': {
        const llmNode = node as LLMWorkflowNode
        if (!llmNode.config?.model) {
          errors.push(`节点 ${node.id} (llm) 缺少 model 配置`)
        }
        if (!llmNode.config?.prompt) {
          errors.push(`节点 ${node.id} (llm) 缺少 prompt 配置`)
        }
        if (llmNode.config?.temperature !== undefined && (llmNode.config.temperature < 0 || llmNode.config.temperature > 1)) {
          errors.push(`节点 ${node.id} (llm) temperature 必须在 0-1 之间`)
        }
        break
      }
      case 'plugin': {
        const pluginNode = node as PluginWorkflowNode
        if (!pluginNode.config?.pluginId) {
          errors.push(`节点 ${node.id} (plugin) 缺少 pluginId 配置`)
        }
        if (!pluginNode.config?.operation) {
          errors.push(`节点 ${node.id} (plugin) 缺少 operation 配置`)
        }
        break
      }
      case 'condition': {
        const conditionNode = node as ConditionWorkflowNode
        if (!conditionNode.config?.condition) {
          errors.push(`节点 ${node.id} (condition) 缺少 condition 配置`)
        }
        if (!conditionNode.config?.truePath) {
          errors.push(`节点 ${node.id} (condition) 缺少 truePath 配置`)
        }
        if (!conditionNode.config?.falsePath) {
          errors.push(`节点 ${node.id} (condition) 缺少 falsePath 配置`)
        }
        break
      }
      case 'end': {
        const endNode = node as EndWorkflowNode
        if (!endNode.config?.output?.result) {
          errors.push(`节点 ${node.id} (end) 缺少 output.result 配置`)
        }
        break
      }
    }
  }

  // 验证必须有且仅有一个开始节点
  if (startNodeCount === 0) {
    errors.push('工作流必须至少有一个开始节点')
  } else if (startNodeCount > 1) {
    errors.push('工作流只能有一个开始节点')
  }

  // 验证必须至少有一个结束节点
  if (endNodeCount === 0) {
    errors.push('工作流必须至少有一个结束节点')
  }

  // 验证边
  const edgeIds = new Set<string>()
  for (const edge of workflow.edges) {
    if (!edge.id || edge.id.trim() === '') {
      errors.push('边 ID 不能为空')
    } else if (edgeIds.has(edge.id)) {
      errors.push(`边 ID 重复: ${edge.id}`)
    } else {
      edgeIds.add(edge.id)
    }

    if (!edge.source || !nodeIds.has(edge.source)) {
      errors.push(`边 ${edge.id} 的源节点不存在: ${edge.source}`)
    }

    if (!edge.target || !nodeIds.has(edge.target)) {
      errors.push(`边 ${edge.id} 的目标节点不存在: ${edge.target}`)
    }
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * 创建默认的工作流配置
 */
export function createDefaultWorkflowConfig(): WorkflowConfig {
  return {
    timeout: 300,
    retry: 0,
    parallel: false
  }
}

/**
 * 创建默认的开始节点配置
 */
export function createDefaultStartNodeConfig(): StartNodeConfig {
  return {
    input: {
      userInput: ''
    }
  }
}

/**
 * 创建默认的 LLM 节点配置
 */
export function createDefaultLLMNodeConfig(): LLMNodeConfig {
  return {
    model: 'deepseek',
    prompt: '',
    temperature: 0.7,
    maxTokens: 2000,
    systemPrompt: undefined
  }
}

/**
 * 创建默认的插件节点配置
 */
export function createDefaultPluginNodeConfig(): PluginNodeConfig {
  return {
    pluginId: 0,
    operation: '',
    parameters: {}
  }
}

/**
 * 创建默认的条件节点配置
 */
export function createDefaultConditionNodeConfig(): ConditionNodeConfig {
  return {
    condition: '',
    truePath: '',
    falsePath: ''
  }
}

/**
 * 创建默认的结束节点配置
 */
export function createDefaultEndNodeConfig(): EndNodeConfig {
  return {
    output: {
      result: ''
    }
  }
}

/**
 * 创建默认的开始节点
 */
export function createDefaultStartNode(id: string = 'start_1'): StartWorkflowNode {
  return {
    id,
    type: 'start',
    name: '开始',
    config: createDefaultStartNodeConfig()
  }
}

/**
 * 创建默认的 LLM 节点
 */
export function createDefaultLLMNode(id: string = 'llm_1'): LLMWorkflowNode {
  return {
    id,
    type: 'llm',
    name: 'AI模型调用',
    config: createDefaultLLMNodeConfig()
  }
}

/**
 * 创建默认的插件节点
 */
export function createDefaultPluginNode(id: string = 'plugin_1'): PluginWorkflowNode {
  return {
    id,
    type: 'plugin',
    name: '插件执行',
    config: createDefaultPluginNodeConfig()
  }
}

/**
 * 创建默认的条件节点
 */
export function createDefaultConditionNode(id: string = 'condition_1'): ConditionWorkflowNode {
  return {
    id,
    type: 'condition',
    name: '条件判断',
    config: createDefaultConditionNodeConfig()
  }
}

/**
 * 创建默认的结束节点
 */
export function createDefaultEndNode(id: string = 'end_1'): EndWorkflowNode {
  return {
    id,
    type: 'end',
    name: '结束',
    config: createDefaultEndNodeConfig()
  }
}

/**
 * 创建默认的 Workflow 表单
 */
export function createDefaultWorkflowForm(): WorkflowForm {
  return {
    name: '',
    description: '',
    version: '1.0.0',
    nodes: [],
    edges: [],
    config: createDefaultWorkflowConfig()
  }
}

