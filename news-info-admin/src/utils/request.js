import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { baseURL } from '@/config/api'
import { getToken, removeToken } from '@/utils/auth-token'

const service = axios.create({
  baseURL,
  timeout: 15000,
})

// 避免并发 401 弹出多个提示
let sessionExpiredHandling = false
function handleSessionExpired() {
  if (sessionExpiredHandling) return
  sessionExpiredHandling = true
  removeToken()
  ElMessage.error('登录已过期，请重新登录')
  router.replace('/login').finally(() => {
    sessionExpiredHandling = false
  })
}

// 请求拦截：注入 Bearer token
service.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截：解包统一格式 { code, message, data }
service.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 200) {
      // 成功直接返回业务数据 data
      return res.data
    }
    // 业务失败（HTTP 200 但 code 非 200，理论上较少出现）
    ElMessage.error(res.message || res.msg || '请求失败')
    return Promise.reject(new Error(res.message || res.msg || 'Error'))
  },
  (error) => {
    const status = error.response?.status
    const data = error.response?.data
    if (status === 401) {
      handleSessionExpired()
    } else {
      ElMessage.error(data?.message || data?.msg || error.message || '网络错误，请稍后重试')
    }
    return Promise.reject(error)
  },
)

export default service
