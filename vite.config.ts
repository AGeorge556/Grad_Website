import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    proxy: {
      '/auth': {
        target: 'https://mpwkqvamrqwxhwozaxpa.supabase.co',
        changeOrigin: true,
        secure: true,
        headers: {
          'Origin': 'http://localhost:5173'
        },
        cookieDomainRewrite: 'localhost'
      }
    },
    cors: true
  },
})
