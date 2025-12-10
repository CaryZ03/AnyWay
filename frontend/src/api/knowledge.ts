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
 * 支持两种接口格式：
 * 1. 标准REST API: /api/v1/knowledge/ (现有后端)
 * 2. Postman文档API: /kb/ (独立知识库服务，需要user_id)
 * 
 * 后端字段名：snake_case (embedding_model, created_at, updated_at)
 * 前端字段名：camelCase (embeddingModel, createdAt, updatedAt)
 */

// 获取当前用户ID（暂时使用固定值，后续可以从用户系统获取）
const getUserId = (): number => {
  // TODO: 从用户系统获取实际user_id
  return 1
}

// 知识库服务基础URL（根据Postman文档）
const KB_BASE_URL = 'https://kenbers.cyou/kb'

/**
 * 转换后端 KnowledgeBase 到前端 KnowledgeBase
 */
function transformKnowledgeBase(backend: any): KnowledgeBase {
  if (!backend) {
    console.warn('transformKnowledgeBase: backend is null or undefined')
    return {
      name: '',
      embeddingModel: 'text-embedding-ada-002'
    }
  }
  
  return {
    id: backend.id,
    name: backend.name || '',
    description: backend.description || undefined,
    embeddingModel: backend.embedding_model || backend.embeddingModel || 'text-embedding-ada-002',
    documentCount: backend.document_count || backend.documentCount || 0,
    createdAt: backend.created_at || backend.createdAt,
    updatedAt: backend.updated_at || backend.updatedAt,
  }
}

/**
 * 使用Postman文档中的接口格式
 */
export const knowledgeApi = {
  /**
   * 获取知识库列表（根据user_id）
   */
  getList: async (userId?: number): Promise<KnowledgeBase[]> => {
    const uid = userId || getUserId()
    try {
      // 先尝试使用Postman文档中的接口
      const axios = (await import('axios')).default
      const response = await axios.get(`${KB_BASE_URL}/list`, {
        params: { user_id: uid },
        timeout: 5000
      })
      console.log('[知识库API] Postman接口响应:', response.data)
      const data = response.data
      
      // 处理响应数据：根据实际API返回格式 { code: 0, data: [...] }
      let list: any[] = []
      if (Array.isArray(data)) {
        list = data
      } else if (data && typeof data === 'object') {
        // 优先处理 { code: 0, data: [...] } 格式
        if (data.code === 0 && Array.isArray(data.data)) {
          list = data.data
        } else {
          // 降级处理其他可能的响应格式
          list = data.data || data.result || data.items || (data.success !== false ? [data] : [])
        }
      }
      
      console.log('[知识库API] 解析后的列表:', list)
      const result = list.map(transformKnowledgeBase).filter(kb => kb.name) // 过滤掉无效数据
      console.log('[知识库API] 转换后的结果:', result)
      return result
    } catch (error: any) {
      console.warn('[知识库API] Postman接口失败，尝试使用标准REST API:', error?.message || error)
      // 降级到标准REST API
      try {
        const data = await request.get<BackendKnowledgeBase[]>('/knowledge/')
        console.log('[知识库API] 标准REST API响应:', data)
        const result = Array.isArray(data) ? data.map(transformKnowledgeBase) : []
        console.log('[知识库API] 标准REST API转换结果:', result)
        return result
      } catch (fallbackError: any) {
        console.error('[知识库API] 标准REST API也失败:', fallbackError?.message || fallbackError)
        return []
      }
    }
  },

  /**
   * 获取知识库详情
   */
  getDetail: async (id: number): Promise<KnowledgeBase> => {
    try {
      const axios = (await import('axios')).default
      const response = await axios.get(`${KB_BASE_URL}/list`, {
        params: { user_id: getUserId() }
      })
      const data = response.data
      // 处理 { code: 0, data: [...] } 格式
      let list: any[] = []
      if (Array.isArray(data)) {
        list = data
      } else if (data && typeof data === 'object') {
        if (data.code === 0 && Array.isArray(data.data)) {
          list = data.data
        } else {
          list = data.data || []
        }
      }
      const kb = list.find((item: any) => item.id === id)
      if (kb) {
        return transformKnowledgeBase(kb)
      }
      throw new Error('知识库不存在')
    } catch (error) {
      console.warn('使用Postman接口失败，尝试使用标准REST API:', error)
      const data = await request.get<BackendKnowledgeBase>(`/knowledge/${id}/`)
      return transformKnowledgeBase(data)
    }
  },

  /**
   * 创建知识库
   */
  create: async (form: Partial<KnowledgeBaseForm>, userId?: number): Promise<KnowledgeBase> => {
    const uid = userId || getUserId()
    if (!form.name) {
      throw new Error('知识库名称不能为空')
    }
    
    try {
      const axios = (await import('axios')).default
      console.log('[知识库API] 创建知识库请求:', { user_id: uid, name: form.name, description: form.description })
      const response = await axios.post(`${KB_BASE_URL}/create`, {
        user_id: uid,
        name: form.name,
        description: form.description || ''
      }, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      })
      console.log('[知识库API] Postman接口创建响应:', response.data)
      const data = response.data
      
      // 处理响应数据：根据实际API返回格式 { code: 0, data: {...} }
      let kb: any = null
      if (Array.isArray(data)) {
        kb = data[0]
      } else if (data && typeof data === 'object') {
        // 优先处理 { code: 0, data: {...} } 格式
        if (data.code === 0 && data.data) {
          kb = data.data
        } else {
          kb = data.data || data.result || data
        }
      }
      
      if (!kb) {
        throw new Error('创建知识库失败：响应数据格式错误')
      }
      
      const result = transformKnowledgeBase(kb)
      console.log('[知识库API] 创建成功，转换后的结果:', result)
      return result
    } catch (error: any) {
      console.warn('[知识库API] Postman接口创建失败，尝试使用标准REST API:', error?.message || error)
      // 降级到标准REST API
      try {
        const requestData: Partial<BackendKnowledgeBaseRequest> = {
          name: form.name || '',
          description: form.description,
          embedding_model: form.embeddingModel || 'text-embedding-ada-002'
        }
        console.log('[知识库API] 使用标准REST API创建:', requestData)
        const data = await request.post<BackendKnowledgeBase>('/knowledge/', requestData)
        console.log('[知识库API] 标准REST API创建响应:', data)
        const result = transformKnowledgeBase(data)
        console.log('[知识库API] 标准REST API创建成功:', result)
        return result
      } catch (fallbackError: any) {
        console.error('[知识库API] 标准REST API创建也失败:', fallbackError?.message || fallbackError)
        throw new Error(fallbackError?.message || '创建知识库失败')
      }
    }
  },

  /**
   * 更新知识库
   */
  update: async (id: number, form: Partial<KnowledgeBaseForm>): Promise<KnowledgeBase> => {
    // Postman文档中没有更新接口，使用标准REST API
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
  delete: async (id: number, userId?: number): Promise<void> => {
    const uid = userId || getUserId()
    try {
      const axios = (await import('axios')).default
      await axios.delete(`${KB_BASE_URL}/delete`, {
        params: {
          user_id: uid,
          knowledge_base_id: id
        }
      })
    } catch (error) {
      console.warn('使用Postman接口失败，尝试使用标准REST API:', error)
      await request.delete(`/knowledge/${id}/`)
    }
  },

  /**
   * 上传文档到知识库
   */
  uploadDocument: async (knowledgeBaseId: number, file: File, userId?: number): Promise<BackendDocument> => {
    const uid = userId || getUserId()
    try {
      const axios = (await import('axios')).default
      const formData = new FormData()
      formData.append('user_id', uid.toString())
      formData.append('knowledge_base_id', knowledgeBaseId.toString())
      formData.append('file', file)
      
      const response = await axios.post(`${KB_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      const data = response.data
      return Array.isArray(data) ? data[0] : (data?.data || data)
    } catch (error) {
      console.warn('使用Postman接口失败，尝试使用标准REST API:', error)
      // 降级到标准REST API
      const formData = new FormData()
      formData.append('file', file)
      return await request.post<BackendDocument>(`/knowledge/${knowledgeBaseId}/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    }
  },

  /**
   * 获取知识库的文档列表
   */
  getDocuments: async (knowledgeBaseId: number, userId?: number): Promise<BackendDocument[]> => {
    const uid = userId || getUserId()
    try {
      const axios = (await import('axios')).default
      const response = await axios.get(`${KB_BASE_URL}/documents`, {
        params: {
          user_id: uid,
          knowledge_base_id: knowledgeBaseId
        },
        timeout: 5000
      })
      console.log('[知识库API] 获取文档列表响应:', response.data)
      const data = response.data
      // 处理 { code: 0, data: [...] } 格式
      let list: any[] = []
      if (Array.isArray(data)) {
        list = data
      } else if (data && typeof data === 'object') {
        if (data.code === 0 && Array.isArray(data.data)) {
          list = data.data
        } else {
          list = data.data || data.result || []
        }
      }
      console.log('[知识库API] 解析后的文档列表:', list)
      return list
    } catch (error: any) {
      console.warn('[知识库API] Postman接口获取文档失败，尝试使用标准REST API:', error?.message || error)
      try {
        return await request.get<BackendDocument[]>(`/knowledge/${knowledgeBaseId}/documents/`)
      } catch (fallbackError: any) {
        console.error('[知识库API] 标准REST API获取文档也失败:', fallbackError?.message || fallbackError)
        return []
      }
    }
  },

  /**
   * 删除文档
   */
  deleteDocument: async (documentId: number, userId?: number): Promise<void> => {
    const uid = userId || getUserId()
    try {
      const axios = (await import('axios')).default
      await axios.delete(`${KB_BASE_URL}/document/${documentId}`, {
        params: {
          user_id: uid
        }
      })
    } catch (error) {
      console.warn('使用Postman接口失败:', error)
      throw error
    }
  },

  /**
   * 查询知识库（RAG搜索）
   */
  query: async (knowledgeBaseId: number, query: string, topK: number = 3, userId?: number): Promise<SearchResult[]> => {
    const uid = userId || getUserId()
    try {
      const axios = (await import('axios')).default
      const response = await axios.post(`${KB_BASE_URL}/query`, {
        user_id: uid,
        knowledge_base_id: knowledgeBaseId,
        query: query,
        top_k: topK
      }, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      })
      console.log('[知识库API] 查询知识库响应:', response.data)
      const data = response.data
      
      // 处理 { code: 0, data: { documents: [...], metadatas: [...], scores: [...] } } 格式
      let results: SearchResult[] = []
      if (data && typeof data === 'object') {
        if (data.code === 0 && data.data) {
          const queryData = data.data
          if (queryData.documents && Array.isArray(queryData.documents)) {
            // 将 documents, metadatas, scores 组合成 SearchResult[]
            const documents = queryData.documents || []
            const metadatas = queryData.metadatas || []
            const scores = queryData.scores || []
            
            results = documents.map((content: string, index: number) => ({
              id: metadatas[index]?.doc_id?.toString() || `${index}`,
              content: content,
              metadata: metadatas[index] || {},
              score: scores[index]
            }))
          }
        } else if (Array.isArray(data.data)) {
          results = data.data
        } else if (Array.isArray(data)) {
          results = data
        } else {
          results = data.data || data.result || []
        }
      }
      
      console.log('[知识库API] 解析后的查询结果:', results)
      return results
    } catch (error: any) {
      console.warn('[知识库API] Postman接口查询失败，尝试使用标准REST API:', error?.message || error)
      // 降级到标准REST API
      try {
        const requestData: SearchRequest = { query, top_k: topK }
        return await request.post<SearchResult[]>(`/knowledge/${knowledgeBaseId}/search/`, requestData)
      } catch (fallbackError: any) {
        console.error('[知识库API] 标准REST API查询也失败:', fallbackError?.message || fallbackError)
        return []
      }
    }
  },

  /**
   * 搜索知识库（别名，保持向后兼容）
   */
  search: async (knowledgeBaseId: number, query: string, topK: number = 5): Promise<SearchResult[]> => {
    return knowledgeApi.query(knowledgeBaseId, query, topK)
  },
}



