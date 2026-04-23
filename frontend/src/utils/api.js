import axios from 'axios'
import { API_BASE_URL, API_TIMEOUT } from '../constants/config.js'

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    if (import.meta.env.VITE_APP_ENV === 'development') {
      console.log('[API Request]', config.method?.toUpperCase(), config.url, config.data || config.params)
    }
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    if (import.meta.env.VITE_APP_ENV === 'development') {
      console.log('[API Response]', response.status, response.data)
    }
    return response
  },
  (error) => {
    console.error('[API Response Error]', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// API 方法
export const uploadLog = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const syncData = () => {
  return api.post('/local_sync')
}

export const getScores = (logId) => {
  return api.get('/scores', {
    params: logId ? { log_id: logId } : {}
  })
}

export const getHistory = (mode, timeRange) => {
  return api.get('/history', {
    params: {
      mode,
      time_range: timeRange
    }
  })
}

export const getAttendance = () => {
  return api.get('/attendance')
}

export const clearData = (type) => {
  return api.post('/clear_data', {
    type
  })
}

export default api