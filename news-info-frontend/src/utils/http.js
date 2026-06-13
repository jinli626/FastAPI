import axios from 'axios'
import { showDialog } from 'vant'
import router from '../router'
import { useUserStore } from '../store/user'
import { apiConfig } from '../config/api'

// 标记是否正在处理「登录过期」，避免并发的多个 401 请求弹出多个弹窗
let isHandlingSessionExpired = false

// 登录 / 注册接口本身返回的 401 是「用户名或密码错误」，不属于会话过期，需要排除
const AUTH_ENDPOINTS = ['/api/user/login', '/api/user/register']

function isAuthEndpoint(url) {
  return AUTH_ENDPOINTS.some((path) => url.includes(path))
}

// 统一处理登录过期：清除登录态 -> 退回登录页 -> 弹窗提示
function handleSessionExpired() {
  if (isHandlingSessionExpired) return
  isHandlingSessionExpired = true

  // 清除本地登录状态（token、用户信息等）
  const userStore = useUserStore()
  userStore.logout()

  // 退出到登录界面
  if (router.currentRoute.value.path !== '/login') {
    router.replace('/login')
  }

  // 弹窗提示用户重新登录
  showDialog({
    title: '提示',
    message: '登录已过期，请重新登录',
    confirmButtonText: '重新登录',
  }).finally(() => {
    isHandlingSessionExpired = false
  })
}

// 注册全局 axios 响应拦截器
export function setupHttpInterceptors() {
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      const status = error.response?.status
      const url = error.config?.url || ''

      // 仅处理「本项目后端」且「非登录/注册接口」返回的 401，判定为会话过期
      if (status === 401 && url.startsWith(apiConfig.baseURL) && !isAuthEndpoint(url)) {
        handleSessionExpired()
      }

      // 继续向下抛出错误，保持各业务原有的 catch 逻辑不受影响
      return Promise.reject(error)
    }
  )
}
