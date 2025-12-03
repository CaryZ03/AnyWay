/**
 * Knowledge Base 相关类型定义
 */

/**
 * Knowledge Base 实体（前端格式）
 */
export interface KnowledgeBase {
  id?: number
  name: string
  description?: string
  embeddingModel: string
  documentCount?: number
  createdAt?: string
  updatedAt?: string
}

/**
 * Knowledge Base 表单（前端编辑格式）
 */
export interface KnowledgeBaseForm {
  id?: number
  name: string
  description?: string
  embeddingModel: string
}

/**
 * 文档分块
 */
export interface DocumentChunk {
  id?: string
  content: string
  metadata?: Record<string, any>
}

/**
 * Document 实体（后端返回格式）
 */
export interface Document {
  id?: number
  knowledgeBaseId: number
  filename: string
  content: string
  chunks: string | DocumentChunk[]  // 可能是 JSON 字符串，也可能是已解析的数组
  vectorIds: string | string[]  // 可能是 JSON 字符串，也可能是已解析的数组
  uploadedAt?: string
}

/**
 * Document 表单（前端编辑格式）
 */
export interface DocumentForm {
  id?: number
  knowledgeBaseId: number
  filename: string
  content: string
  chunks: DocumentChunk[]
  vectorIds: string[]
}

