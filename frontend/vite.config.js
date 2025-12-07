import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())
  const apiBaseUrl = env.VITE_API_BASE_URL || 'http://localhost:8000'
  const port = parseInt(env.VITE_PORT || '5173')
  const host = env.VITE_HOST || '0.0.0.0'
  
  return {
    plugins: [vue()],
    server: {
      host: host,
      port: port,
      proxy: {
        '/api': {
          target: apiBaseUrl,
          changeOrigin: true
        }
      }
    }
  }
})
