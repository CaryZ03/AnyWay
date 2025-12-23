// initial-elements.ts
/* eslint-disable */
// @ts-nocheck
import type { GraphNode, GraphEdge } from '@vue-flow/core'
import { MarkerType } from '@vue-flow/core'

export const initialNodes: GraphNode[] = [
  {
    id: '1',
    type: 'start',
    data: {
      name: '开始节点',
      input_text: '用户输入'
    },
    position: { x: 250, y: 0 },
    class: 'light',
  },
  {
    id: '2',
    type: 'output',
    data: { label: 'output' },
    position: { x: 100, y: 100 },
  },
  {
    id: '3',
    type: 'llm',
    data: {
      name: 'LLM节点',
      agent_uuid: 'agent-12345678-1234-1234-1234-123456789abc',
      input: {
        context: '上下文信息',
        question: '用户问题'
      },
      prompt: '你是一个有用的AI助手，请回答用户的问题。',
      temperature: 0.7,
      max_tokens: 2000,
      output: {
        answer: 'str',
        reasoning: 'str'
      }
    },
    position: { x: 400, y: 100 },
    class: 'light',
  },
  {
    id: '4',
    type: 'http',
    data: {
      name: 'HTTP请求',
      url: 'https://api.example.com/data',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer token123'
      },
      body: {
        name: 'test',
        value: 123
      },
      output: {
        code: 'int',
        msg: 'str',
        data: 'obj'
      }
    },
    position: { x: 150, y: 200 },
    class: 'light',
  },
  {
    id: '5',
    type: 'intent',
    data: {
      name: '意图识别',
      input: '用户输入的文本',
      intent_categories: ['查询', '投诉', '建议', '其他'],
      recognition_method: 'llm',
      agent_uuid: 'agent-87654321-4321-4321-4321-cba987654321',
      output: {
        intent: 'str',
        confidence: 'num'
      }
    },
    position: { x: 300, y: 300 },
    class: 'light',
  },
  {
    id: '6',
    type: 'knowledge',
    data: {
      name: '知识库检索',
      knowledge_base_id: 1,
      query: '如何重置密码',
      top_k: 5,
      similarity_threshold: 0.7,
      output: {
        documents: 'arr',
        scores: 'arr'
      }
    },
    position: { x: 300, y: 300 },
    class: 'light',
  },
  {
    id: '7',
    type: 'string',
    data: {
      name: '字符串处理',
      operation: 'concat',
      input_string: 'Hello',
      parameters: {
        separator: ' ',
        suffix: 'World'
      },
      output: {
        result: 'str'
      }
    },
    position: { x: 500, y: 300 },
    class: 'light',
  },
  {
    id: '8',
    type: 'end',
    data: {
      name: '结束节点',
      output_text: '最终结果',
      output: {
        final_answer: 'str'
      }
    },
    position: { x: 300, y: 400 },
    class: 'light',
  },
]

export const initialEdges: GraphEdge[] = [
  {
    id: 'e1-2',
    source: '1',
    target: '2',
    animated: true,
  },
  {
    id: 'e1-3',
    source: '1',
    target: '3',
    label: 'edge with arrowhead',
    markerEnd: MarkerType.ArrowClosed,
  },
  {
    id: 'e4-5',
    type: 'step',
    source: '4',
    target: '5',
    label: 'Node 2',
    style: { stroke: 'orange' },
    labelBgStyle: { fill: 'orange' },
  },
  {
    id: 'e3-4',
    type: 'smoothstep',
    source: '3',
    target: '4',
    label: 'smoothstep-edge',
  },
]