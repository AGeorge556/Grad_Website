import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/auth/v1': {
        target: 'https://xqxbqxpxvxvxvxvx.supabase.co',
        changeOrigin: true,
        secure: true,
        headers: {
          'Origin': 'http://localhost:5173'
        },
        cookieDomainRewrite: 'localhost',
        rewrite: (path) => path
      },
    },
    cors: true
  },
})
