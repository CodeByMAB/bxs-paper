import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../static',
    emptyOutDir: false,
    rollupOptions: {
      input: {
        main: './index.html'
      }
    }
  },
  server: {
    proxy: {
      '/metrics': 'http://localhost:8080',
      '/alerts': 'http://localhost:8080',
      '/healthz': 'http://localhost:8080'
    }
  }
})

