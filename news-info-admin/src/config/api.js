// API 基础地址：开发环境为空走 vite 代理，生产环境取 .env.production 中的地址
export const baseURL = import.meta.env.VITE_API_BASE_URL || ''
