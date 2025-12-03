import request from '@/utils/request'
import type { KnowledgeBase, KnowledgeBaseForm } from '@/types/knowledge-base'
import type {
  BackendKnowledgeBase,
  BackendKnowledgeBaseRequest,
  BackendDocument,
  SearchRequest,
  SearchResult,
} from '@/types/api'

/**
 * Knowledge Base API
 * 后端字段名：snake_case (embedding_model, created_at, updated_at)
 * 前端字段名：camelCase (embeddingModel, createdAt, updatedAt)
 */

/**
 * 转换后端 KnowledgeBase 到前端 KnowledgeBase
 */
function transformKnowledgeBase(backend: BackendKnowledgeBase): KnowledgeBase {
  return {
    id: backend.id,
    name: backend.name,
    description: backend.description,
    embeddingModel: backend.embedding_model,
    documentCount: backend.document_count,
    createdAt: backend.created_at,
    updatedAt: backend.updated_at,
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
  create: async (form: Partial<KnowledgeBaseForm>): Promise<KnowledgeBase> => {
    const requestData: Partial<BackendKnowledgeBaseRequest> = {}
    if (form.name !== undefined) requestData.name = form.name
    if (form.description !== undefined) requestData.description = form.description
    if (form.embeddingModel !== undefined) requestData.embedding_model = form.embeddingModel
    
    // 设置默认值
    if (!requestData.embedding_model) requestData.embedding_model = 'text-embedding-ada-002'
    
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
    if (form.embeddingModel !== undefined) requestData.embedding_model = form.embeddingModel

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
   * 上传文档到知识库
   */
  uploadDocument: async (knowledgeBaseId: number, file: File): Promise<BackendDocument> => {
    const formData = new FormData()
    formData.append('file', file)
    return await request.post<BackendDocument>(`/knowledge/${knowledgeBaseId}/upload/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  /**
   * 获取知识库的文档列表
   */
  getDocuments: async (knowledgeBaseId: number): Promise<BackendDocument[]> => {
    return await request.get<BackendDocument[]>(`/knowledge/${knowledgeBaseId}/documents/`)
  },

  /**
   * 搜索知识库
   */
  search: async (knowledgeBaseId: number, query: string, topK: number = 5): Promise<SearchResult[]> => {
    const requestData: SearchRequest = { query, top_k: topK }
    return await request.post<SearchResult[]>(`/knowledge/${knowledgeBaseId}/search/`, requestData)
  },
}


