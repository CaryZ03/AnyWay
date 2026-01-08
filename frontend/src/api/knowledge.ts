import axios, { type AxiosInstance } from 'axios'
import type { KnowledgeBase, KnowledgeBaseForm } from '@/types/knowledge-base'
import type { BackendDocument, SearchResult } from '@/types/api'

/**
 * Knowledge Base API
 * 严格按照 Postman 文档实现：https://kenbers.cyou/kb/*
 * 
 * Postman 文档接口：
 * 1. POST /create - 创建知识库
 * 2. GET /list?user_id=1 - 查看某用户的所有知识库
 * 3. GET /documents?user_id=1&knowledge_base_id=1 - 查看某个知识库所有文档
 * 4. POST /upload - 上传文档
 * 5. DELETE /document/1?user_id=1 - 删除文档
 * 6. DELETE /delete?user_id=1&knowledge_base_id=1 - 删除知识库
 * 7. POST /query - 查询知识库信息
 */

// 知识库服务基础URL
// 开发环境：通过 Vite 代理访问（vite.config.ts 中配置了 /kb 代理）
// 生产环境：通过 Nginx 代理访问（nginx.conf 中配置了 /kb 代理）
// 统一使用相对路径 /kb，避免 CORS 问题

// 获取当前用户ID（暂时使用固定值，后续可以从用户系统获取）
const getUserId = (): number => {
  // TODO: 从用户系统获取实际user_id
  return 1
}

// 创建专门用于知识库服务的 axios 实例
const kbAxiosInstance: AxiosInstance = axios.create({
  baseURL: '/kb',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
kbAxiosInstance.interceptors.request.use(
  (config) => {
    // 如果是 FormData，删除 Content-Type，让浏览器自动设置
    if (config.data instanceof FormData && config.headers) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理可能的响应格式
kbAxiosInstance.interceptors.response.use(
  (response) => {
    const { data } = response
    // 处理可能的响应格式：{ code: 0, data: [...] } 或直接返回数据
    if (data && typeof data === 'object' && data.code === 0 && data.data !== undefined) {
      return data.data
    }
    return data
  },
  (error) => {
    console.error('[知识库API] 请求失败:', error)
    if (error.response) {
      const { status, data } = error.response
      const errorMessage = data?.message || data?.detail || `请求失败: ${status}`
      return Promise.reject(new Error(errorMessage))
    } else if (error.request) {
      return Promise.reject(new Error('网络错误，请检查网络连接'))
    } else {
      return Promise.reject(error)
    }
  }
)

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
 * 标准化文档状态
 */
function normalizeDocumentStatus(doc: any): 'pending' | 'processing' | 'completed' | 'failed' {
  let status = doc.status
  
  // 标准化 status 值（处理可能的变体）
  if (status) {
    const statusLower = String(status).toLowerCase()
    if (statusLower === 'done' || statusLower === 'success' || statusLower === 'finished') {
      status = 'completed'
    } else if (statusLower === 'error' || statusLower === 'fail') {
      status = 'failed'
    } else if (statusLower === 'running' || statusLower === 'in_progress') {
      status = 'processing'
    } else if (statusLower === 'waiting' || statusLower === 'queued') {
      status = 'pending'
    }
  }
  
  // 如果没有 status 或 status 无效，根据其他字段推断
  if (!status || !['pending', 'processing', 'completed', 'failed'].includes(status)) {
    // 如果有 processed_at 或 chunks 或 chunk_count > 0，说明已处理完成
    if (doc.processed_at || (doc.chunks && (Array.isArray(doc.chunks) ? doc.chunks.length > 0 : true)) || (doc.chunk_count && doc.chunk_count > 0)) {
      status = 'completed'
    } 
    // 如果有 error_message，说明处理失败
    else if (doc.error_message) {
      status = 'failed'
    }
    // 如果有 uploaded_at 或 created_at，说明已上传
    else if (doc.uploaded_at || doc.created_at) {
      // 检查是否上传时间超过一定时间（比如10分钟），如果超过则认为已完成
      const uploadTime = new Date(doc.uploaded_at || doc.created_at).getTime()
      const now = Date.now()
      const tenMinutes = 10 * 60 * 1000
      if (now - uploadTime > tenMinutes) {
        status = 'completed'
      } else {
        status = 'processing'
      }
    }
    // 默认状态为 pending
    else {
      status = 'pending'
    }
  }
  
  return status as 'pending' | 'processing' | 'completed' | 'failed'
}

export const knowledgeApi = {
  /**
   * 1. 创建知识库
   * POST /create
   * Body: { user_id: number, name: string, description?: string }
   */
  create: async (form: Partial<KnowledgeBaseForm>, userId?: number): Promise<KnowledgeBase> => {
    const uid = userId || getUserId()
    if (!form.name) {
      throw new Error('知识库名称不能为空')
    }
    
    const response = await kbAxiosInstance.post('/create', {
      user_id: uid,
      name: form.name,
      description: form.description || ''
    })
    
    // 处理响应：可能是单个对象或数组
    const data = Array.isArray(response) ? response[0] : response
    return transformKnowledgeBase(data)
  },

  /**
   * 2. 查看某用户的所有知识库
   * GET /list?user_id=1
   */
  getList: async (userId?: number): Promise<KnowledgeBase[]> => {
    const uid = userId || getUserId()
    const response: any = await kbAxiosInstance.get('/list', {
      params: { user_id: uid }
    })
    
    // 处理响应：可能是数组或包装在对象中
    const list = Array.isArray(response) ? response : (response?.data || [])
    return list.map((kb: any) => transformKnowledgeBase(kb)).filter((kb: KnowledgeBase) => kb.name)
  },

  /**
   * 获取知识库详情（通过列表接口查找）
   * GET /list?user_id=1，然后查找指定 id
   */
  getDetail: async (id: number, userId?: number): Promise<KnowledgeBase> => {
    const list = await knowledgeApi.getList(userId)
    const kb = list.find(item => item.id === id)
    if (!kb) {
      throw new Error('知识库不存在')
    }
    return kb
  },

  /**
   * 更新知识库
   * 注意：Postman 文档中没有更新接口，此方法保留用于兼容性
   * 实际实现可能需要通过后端代理或其他方式
   */
  update: async (_id: number, _form: Partial<KnowledgeBaseForm>): Promise<KnowledgeBase> => {
    // Postman 文档中没有更新接口，暂时抛出错误
    throw new Error('知识库更新功能暂不支持，请使用删除后重新创建的方式')
  },

  /**
   * 6. 删除知识库
   * DELETE /delete?user_id=1&knowledge_base_id=1
   */
  delete: async (id: number, userId?: number): Promise<void> => {
    const uid = userId || getUserId()
    await kbAxiosInstance.delete('/delete', {
      params: {
        user_id: uid,
        knowledge_base_id: id
      }
    })
  },

  /**
   * 4. 上传文档到知识库
   * POST /upload
   * FormData: { user_id: number, knowledge_base_id: number, file: File }
   */
  uploadDocument: async (knowledgeBaseId: number, file: File, userId?: number): Promise<BackendDocument> => {
    const uid = userId || getUserId()
    const formData = new FormData()
    formData.append('user_id', uid.toString())
    formData.append('knowledge_base_id', knowledgeBaseId.toString())
    formData.append('file', file)
    
    const response: any = await kbAxiosInstance.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    // 处理响应：可能是单个对象或数组
    const doc = Array.isArray(response) ? response[0] : response
    return doc as BackendDocument
  },

  /**
   * 3. 查看某个知识库所有文档
   * GET /documents?user_id=1&knowledge_base_id=1
   */
  getDocuments: async (knowledgeBaseId: number, userId?: number): Promise<BackendDocument[]> => {
    const uid = userId || getUserId()
    const response: any = await kbAxiosInstance.get('/documents', {
      params: {
        user_id: uid,
        knowledge_base_id: knowledgeBaseId
      }
    })
    
    // 处理响应：可能是数组或包装在对象中
    const list = Array.isArray(response) ? response : (response?.data || [])
    
    // 标准化文档数据，确保 status 字段存在
    return list.map((doc: any) => ({
      ...doc,
      status: normalizeDocumentStatus(doc),
      knowledge_base_id: doc.knowledge_base_id || doc.knowledge_base || knowledgeBaseId,
      uploaded_at: doc.uploaded_at || doc.created_at,
    })) as BackendDocument[]
  },

  /**
   * 5. 删除文档
   * DELETE /document/{document_id}?user_id=1
   */
  deleteDocument: async (documentId: number, userId?: number): Promise<void> => {
    const uid = userId || getUserId()
    await kbAxiosInstance.delete(`/document/${documentId}`, {
      params: {
        user_id: uid
      }
    })
  },

  /**
   * 7. 查询知识库信息（RAG搜索）
   * POST /query
   * Body: { user_id: number, knowledge_base_id: number, query: string, top_k: number }
   */
  query: async (knowledgeBaseId: number, query: string, topK: number = 3, userId?: number): Promise<SearchResult[]> => {
    const uid = userId || getUserId()
    const response: any = await kbAxiosInstance.post('/query', {
      user_id: uid,
      knowledge_base_id: knowledgeBaseId,
      query: query,
      top_k: topK
    })
    
    // 处理响应格式：{ documents: [...], metadatas: [...], scores: [...] }
    if (response && typeof response === 'object' && !Array.isArray(response)) {
      if (response.documents && Array.isArray(response.documents)) {
        const documents = response.documents || []
        const metadatas = response.metadatas || []
        const scores = response.scores || []
        
        return documents.map((content: string, index: number) => ({
          id: metadatas[index]?.doc_id?.toString() || `${index}`,
          content: content,
          metadata: metadatas[index] || {},
          score: scores[index]
        }))
      } else if (response.data && Array.isArray(response.data)) {
        return response.data
      }
    } else if (Array.isArray(response)) {
      return response
    }
    
    return []
  },

  /**
   * 搜索知识库（别名，保持向后兼容）
   */
  search: async (knowledgeBaseId: number, query: string, topK: number = 5): Promise<SearchResult[]> => {
    return knowledgeApi.query(knowledgeBaseId, query, topK)
  },
}
