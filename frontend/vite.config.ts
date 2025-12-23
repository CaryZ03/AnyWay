import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://106.12.174.161:18080',
        changeOrigin: true, // 把 Host 头也换成后端地址
        rewrite: (path) => path, // 不需要重写就保持原样
      },
      '/kb': {
        target: 'https://kenbers.cyou',
        changeOrigin: true, // 把 Host 头也换成后端地址
        rewrite: (path) => path, // 不需要重写就保持原样
      },
    },
  },
})
