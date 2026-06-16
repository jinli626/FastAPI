import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5174,
    open: true,
    proxy: {
      // 开发环境下把 /api、/static 转发到 FastAPI 后端，规避跨域
      '/api': {
        target: 'http://192.168.248.99:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://192.168.248.99:8000',
        changeOrigin: true,
      },
    },
  },
})
