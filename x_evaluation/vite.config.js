import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/prospie/',
  server: {
    port: 5173,
    strictPort: true,
    hmr: {
      overlay: true,
    },
  },
})
