import request from '@/utils/request'
import type { KnowledgeBase, KnowledgeBaseForm, Document } from '@/types/knowledge-base'
import type {
  BackendKnowledgeBase,
  BackendKnowledgeBaseRequest,
  BackendDocument,
  SearchRequest,
  SearchResult,
} from '@/types/api'

/**
 * Knowledge Base API
 * 后端字段名：snake_case (embedding_model, created_at, updated_at, knowledge_base_id, uploaded_at)
 * 前端字段名：camelCase (vectorDbType, chunkSize, chunkOverlap, createdAt, knowledgeBaseId, uploadedAt)
 * 
 * 注意：后端使用 embedding_model 字段，前端使用 vectorDbType
 * 后端没有 chunkSize 和 chunkOverlap 字段
 */

/**
 * 转换后端 KnowledgeBase 到前端 KnowledgeBase
 */
function transformKnowledgeBase(backend: BackendKnowledgeBase): KnowledgeBase {
  // 后端使用 embedding_model，前端使用 vectorDbType
  // 这里需要根据 embedding_model 推断 vectorDbType，或者使用默认值
  // 由于后端没有 vectorDbType 字段，我们使用默认值 'chroma'
  // 同样，chunkSize 和 chunkOverlap 后端也没有，使用默认值
  return {
    id: backend.id,
    name: backend.name,
    description: backend.description,
    vectorDbType: 'chroma', // 默认值，后端没有此字段
    chunkSize: 1000, // 默认值，后端没有此字段
    chunkOverlap: 200, // 默认值，后端没有此字段
    createdAt: backend.created_at,
  }
}

/**
 * 转换前端 KnowledgeBaseForm 到后端请求格式
 */
function transformKnowledgeBaseRequest(form: KnowledgeBaseForm): BackendKnowledgeBaseRequest {
  return {
    name: form.name,
    description: form.description,
    embedding_model: 'text-embedding-ada-002', // 默认值，前端没有此字段
  }
}

/**
 * 转换后端 Document 到前端 Document
 */
function transformDocument(backend: BackendDocument): Document {
  return {
    id: backend.id,
    knowledgeBaseId: backend.knowledge_base,
    filename: backend.filename,
    content: '', // 后端 Document 模型有 content 字段，但序列化器没有返回
    chunks: [], // 后端没有直接返回 chunks
    vectorIds: [], // 后端没有直接返回 vectorIds
    uploadedAt: backend.uploaded_at,
  }
}

export const knowledgeApi = {
  /**
   * 获取知识库列表
   */
  getList: async (): Promise<KnowledgeBase[]> => {
    const data = await request.get<BackendKnowledgeBase[]>('/knowledge/')
    return Array.isArray(data) ? data.map(transformKnowledgeBase) : []
  },

  /**
   * 获取知识库详情
   */
  getDetail: async (id: number): Promise<KnowledgeBase> => {
    const data = await request.get<BackendKnowledgeBase>(`/knowledge/${id}/`)
    return transformKnowledgeBase(data)
  },

  /**
   * 创建知识库
   */
  create: async (form: KnowledgeBaseForm): Promise<KnowledgeBase> => {
    const requestData = transformKnowledgeBaseRequest(form)
    const data = await request.post<BackendKnowledgeBase>('/knowledge/', requestData)
    return transformKnowledgeBase(data)
  },

  /**
   * 更新知识库
   */
  update: async (id: number, form: Partial<KnowledgeBaseForm>): Promise<KnowledgeBase> => {
    const requestData: Partial<BackendKnowledgeBaseRequest> = {}
    if (form.name !== undefined) requestData.name = form.name
    if (form.description !== undefined) requestData.description = form.description
    // vectorDbType, chunkSize, chunkOverlap 后端不支持更新

    const data = await request.patch<BackendKnowledgeBase>(`/knowledge/${id}/`, requestData)
    return transformKnowledgeBase(data)
  },

  /**
   * 删除知识库
   */
  delete: async (id: number): Promise<void> => {
    await request.delete(`/knowledge/${id}/`)
  },

  /**
   * 上传文档
   */
  uploadDocument: async (knowledgeBaseId: number, file: File): Promise<Document> => {
    const formData = new FormData()
    formData.append('file', file)
    
    // request 工具会自动处理 FormData 和 token
    const data = await request.post<BackendDocument>(`/knowledge/${knowledgeBaseId}/upload/`, formData)
    return transformDocument(data)
  },

  /**
   * 获取文档列表
   */
  getDocuments: async (knowledgeBaseId: number): Promise<Document[]> => {
    const data = await request.get<BackendDocument[]>(`/knowledge/${knowledgeBaseId}/documents/`)
    return Array.isArray(data) ? data.map(transformDocument) : []
  },

  /**
   * 搜索知识库
   */
  search: async (knowledgeBaseId: number, query: string, topK: number = 5): Promise<SearchResult[]> => {
    const requestData: SearchRequest = { query, top_k: topK }
    const data = await request.post<SearchResult[]>(`/knowledge/${knowledgeBaseId}/search/`, requestData)
    return Array.isArray(data) ? data : []
  },
}

