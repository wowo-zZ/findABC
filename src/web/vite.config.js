import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    hmr: false,  // 禁用热更新
    host: '0.0.0.0'  // 允许局域网访问
  }
})