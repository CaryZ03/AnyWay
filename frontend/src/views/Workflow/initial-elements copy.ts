// initial-elements.ts
/* eslint-disable */
// @ts-nocheck
import type { GraphNode, GraphEdge } from '@vue-flow/core'
import { MarkerType } from '@vue-flow/core'

export const initialNodes: GraphNode[] = [
  {
    id: '1',
    type: 'start',
    data: { input_text: 'start' },
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
      label: 'LLM',
      output: {
        url: 'str',
        method: 'str',
        headers: {
          'Content-Type': 'str',
        },
        body: {
          name: 'str',
        },
      }
    },
    position: { x: 400, y: 100 },
    class: 'light',
  },
  {
    id: '4',
    type: 'http',
    data: { 
      label: 'HTTP', 
      output: {
        code: 'number',
        msg: 'string',
        data: 'obj',
      } 
    },
    position: { x: 150, y: 200 },
    class: 'light',
  },
  {
    id: '5',
    type: 'intent',
    data: { label: 'Intent' },
    position: { x: 300, y: 300 },
    class: 'light',
  },
  {
    id: '6',
    type: 'knowledge',
    data: { label: 'Knowledge' },
    position: { x: 300, y: 300 },
    class: 'light',
  },
  {
    id: '7',
    type: 'string',
    data: { label: 'String' },
    position: { x: 500, y: 300 },
    class: 'light',
  },
  {
    id: '8',
    type: 'end',
    data: { label: 'end' },
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