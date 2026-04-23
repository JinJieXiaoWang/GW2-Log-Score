import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    base: './',
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: false,
      minify: 'esbuild',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'vue-router', 'axios'],
            charts: ['echarts']
          }
        }
      }
    },
    server: {
      port: parseInt(env.VITE_PORT || '5173'),
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true
        }
      }
    },
    preview: {
      port: parseInt(env.VITE_PORT || '4173')
    }
  }
})
