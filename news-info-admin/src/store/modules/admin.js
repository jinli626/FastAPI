import { defineStore } from 'pinia'
import { loginApi, getAdminInfoApi } from '@/api/auth'
import { getToken, setToken, removeToken } from '@/utils/auth-token'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    // token 真源在 localStorage（auth-token.js），此处仅作初始化镜像供响应式使用
    token: getToken(),
    adminInfo: null,
  }),

  getters: {
    isLogin: (state) => !!state.token,
    adminName: (state) => state.adminInfo?.nickname || state.adminInfo?.username || '管理员',
  },

  actions: {
    async login(payload) {
      const data = await loginApi(payload) // { token, adminInfo }
      this.token = data.token
      this.adminInfo = data.adminInfo
      setToken(data.token)
      return data
    },

    async fetchInfo() {
      const data = await getAdminInfoApi()
      this.adminInfo = data
      return data
    },

    logout() {
      this.token = ''
      this.adminInfo = null
      removeToken()
    },
  },

  // 仅持久化 adminInfo，token 由 auth-token.js 管理
  persist: {
    key: 'admin-store',
    pick: ['adminInfo'],
  },
})
