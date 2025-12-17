import axios from 'axios'
import type { AxiosInstance, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios'

// API 基础配置
// 开发环境：通过 Vite 代理访问后端（vite.config.ts 中配置了代理）
// 生产环境：使用相对路径（通过 Nginx 代理）
const API_BASE_URL = '/api/v1'

// 创建 axios 实例
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 自定义 request 接口，返回类型为 T 而不是 AxiosResponse<T>
interface CustomRequestInstance {
  get<T = any>(url: string, config?: any): Promise<T>
  post<T = any>(url: string, data?: any, config?: any): Promise<T>
  put<T = any>(url: string, data?: any, config?: any): Promise<T>
  patch<T = any>(url: string, data?: any, config?: any): Promise<T>
  delete<T = any>(url: string, config?: any): Promise<T>
}

// 创建包装的 request 对象
const request = axiosInstance as unknown as CustomRequestInstance

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 可以在这里添加 token
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 如果是 FormData，删除 Content-Type，让浏览器自动设置
    if (config.data instanceof FormData && config.headers) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    // 后端统一响应格式：{ code, message, data, success }
    const { data } = response
    console.log('[响应拦截器] 原始响应:', data)
    
    // 如果后端返回 success: false，视为错误
    if (data.success === false) {
      return Promise.reject(new Error(data.message || '请求失败'))
    }
    
    // 返回 data 字段
    const result = data.data !== undefined ? data.data : data
    console.log('[响应拦截器] 处理后结果:', result)
    return result
  },
  (error: AxiosError) => {
    // 处理 HTTP 错误
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 未授权，可以跳转到登录页
          console.error('未授权，请重新登录')
          // router.push('/login')
          break
        case 403:
          console.error('拒绝访问')
          break
        case 404:
          console.error('请求地址不存在')
          break
        case 500:
          console.error('服务器内部错误')
          break
        default:
          console.error(`请求失败: ${status}`)
      }
      
      // 返回后端错误信息
      const errorData = data as any
      console.error('[请求错误] 状态码:', status, '完整错误数据:', JSON.stringify(errorData, null, 2))
      
      // 尝试提取详细的错误信息
      let errorMessage = '请求失败'
      
      // 优先使用 message 字段
      if (errorData?.message && errorData.message !== '请求失败') {
        errorMessage = errorData.message
      } 
      // 如果有 data 字段，尝试提取字段级错误
      else if (errorData?.data && typeof errorData.data === 'object' && errorData.data !== null) {
        const errorDataObj = errorData.data as Record<string, any>
        const errorKeys = Object.keys(errorDataObj)
        
        if (errorKeys.length > 0) {
          // 提取第一个字段的错误
          const firstKey = errorKeys[0]
          if (firstKey && firstKey in errorDataObj) {
            const firstError = errorDataObj[firstKey]
            
            if (Array.isArray(firstError) && firstError.length > 0) {
              // 如果是数组，取第一个元素
              errorMessage = `${firstKey}: ${String(firstError[0])}`
            } else if (firstError) {
              // 如果是字符串或其他类型
              errorMessage = `${firstKey}: ${String(firstError)}`
            }
          }
        }
      }
      // 使用 detail 字段
      else if (errorData?.detail) {
        errorMessage = errorData.detail
      }
      
      console.error('[请求错误] 提取的错误信息:', errorMessage)
      
      return Promise.reject(new Error(errorMessage))
    } else if (error.request) {
      console.error('网络错误，请检查网络连接')
      return Promise.reject(new Error('网络错误，请检查网络连接'))
    } else {
      console.error('请求配置错误')
      return Promise.reject(error)
    }
  }
)

export default request