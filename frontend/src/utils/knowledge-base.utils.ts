/**
 * Knowledge Base 相关工具函数
 */
import type { KnowledgeBase, KnowledgeBaseForm, Document, DocumentForm, DocumentChunk } from '@/types/knowledge-base'

/**
 * 将后端实体转换为前端表单模型
 */
export function knowledgeBaseToForm(knowledgeBase: KnowledgeBase): KnowledgeBaseForm {
  return {
    id: knowledgeBase.id,
    name: knowledgeBase.name,
    description: knowledgeBase.description,
    vectorDbType: knowledgeBase.vectorDbType,
    chunkSize: knowledgeBase.chunkSize,
    chunkOverlap: knowledgeBase.chunkOverlap
  }
}

/**
 * 将前端表单模型转换为后端实体
 */
export function formToKnowledgeBase(form: KnowledgeBaseForm): KnowledgeBase {
  return {
    id: form.id,
    name: form.name,
    description: form.description,
    vectorDbType: form.vectorDbType,
    chunkSize: form.chunkSize,
    chunkOverlap: form.chunkOverlap
  }
}

/**
 * 验证 Knowledge Base
 */
export function validateKnowledgeBase(knowledgeBase: KnowledgeBaseForm): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  if (!knowledgeBase.name || knowledgeBase.name.trim() === '') {
    errors.push('名称不能为空')
  }

  if (!knowledgeBase.vectorDbType || !['chroma', 'milvus'].includes(knowledgeBase.vectorDbType)) {
    errors.push('向量数据库类型必须是 chroma 或 milvus')
  }

  if (knowledgeBase.chunkSize <= 0) {
    errors.push('分块大小必须大于 0')
  }

  if (knowledgeBase.chunkOverlap < 0) {
    errors.push('分块重叠不能小于 0')
  }

  if (knowledgeBase.chunkOverlap >= knowledgeBase.chunkSize) {
    errors.push('分块重叠不能大于等于分块大小')
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * 创建默认的 Knowledge Base 表单
 */
export function createDefaultKnowledgeBaseForm(): KnowledgeBaseForm {
  return {
    name: '',
    description: '',
    vectorDbType: 'chroma',
    chunkSize: 1000,
    chunkOverlap: 200
  }
}

/**
 * 将后端实体转换为前端表单模型
 * 智能处理：如果后端返回的是对象，直接使用；如果是字符串，则解析
 */
export function documentToForm(document: Document): DocumentForm {
  // 如果 chunks 已经是数组，直接使用；否则解析字符串
  const chunks: DocumentChunk[] = Array.isArray(document.chunks)
    ? document.chunks
    : JSON.parse(document.chunks || '[]') as DocumentChunk[]

  // 如果 vectorIds 已经是数组，直接使用；否则解析字符串
  const vectorIds: string[] = Array.isArray(document.vectorIds)
    ? document.vectorIds
    : JSON.parse(document.vectorIds || '[]') as string[]

  return {
    id: document.id,
    knowledgeBaseId: document.knowledgeBaseId,
    filename: document.filename,
    content: document.content,
    chunks,
    vectorIds
  }
}

/**
 * 将前端表单模型转换为后端实体
 */
export function formToDocument(form: DocumentForm): Document {
  return {
    id: form.id,
    knowledgeBaseId: form.knowledgeBaseId,
    filename: form.filename,
    content: form.content,
    chunks: JSON.stringify(form.chunks),
    vectorIds: JSON.stringify(form.vectorIds)
  }
}

/**
 * 验证 Document
 */
export function validateDocument(document: DocumentForm): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  if (!document.filename || document.filename.trim() === '') {
    errors.push('文件名不能为空')
  }

  if (!document.content || document.content.trim() === '') {
    errors.push('内容不能为空')
  }

  if (!document.knowledgeBaseId) {
    errors.push('知识库 ID 不能为空')
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * 创建默认的 Document 表单
 */
export function createDefaultDocumentForm(): DocumentForm {
  return {
    knowledgeBaseId: 0,
    filename: '',
    content: '',
    chunks: [],
    vectorIds: []
  }
}

