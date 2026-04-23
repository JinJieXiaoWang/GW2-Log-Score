<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <header class="mb-8 text-center">
        <div class="inline-block bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
          <h1 class="text-3xl font-bold tracking-tight">
            {{ systemSettings.systemName }}
          </h1>
        </div>
        <p class="text-sm text-gray-600 mt-3 max-w-2xl mx-auto">
          {{ systemSettings.systemSlogan }}
        </p>
        <div class="w-24 h-1 bg-gradient-to-r from-indigo-300 via-purple-300 to-indigo-300 mx-auto mt-4 rounded-full" />
      </header>

      <!-- Navigation -->
      <nav class="flex space-x-4 mb-8 justify-center">
        <router-link 
          to="/" 
          :class="$route.path === '/' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-500 hover:text-gray-700'"
          class="px-4 py-2 rounded-lg text-sm font-bold shadow-sm border border-transparent transition-all"
        >
          实时数据看板
        </router-link>
        <router-link 
          to="/history" 
          :class="$route.path === '/history' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-500 hover:text-gray-700'"
          class="px-4 py-2 rounded-lg text-sm font-bold shadow-sm border border-transparent transition-all"
        >
          历史数据分析
        </router-link>
        <router-link 
          to="/attendance" 
          :class="$route.path === '/attendance' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-500 hover:text-gray-700'"
          class="px-4 py-2 rounded-lg text-sm font-bold shadow-sm border border-transparent transition-all"
        >
          出勤统计
        </router-link>
        <router-link 
          to="/settings" 
          :class="$route.path === '/settings' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-500 hover:text-gray-700'"
          class="px-4 py-2 rounded-lg text-sm font-bold shadow-sm border border-transparent transition-all"
        >
          系统设置
        </router-link>
      </nav>

      <!-- Views -->
      <router-view />

      <!-- Footer -->
      <footer class="mt-16 pt-8 border-t border-gray-200">
        <div class="text-center">
          <p class="text-xs text-gray-500">
            {{ systemSettings.copyright }}
          </p>
          <p class="text-xs text-gray-400 mt-1">
            每一份努力都值得被量化
          </p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'

// 系统设置
const systemSettings = reactive({
  systemName: '激战2日志评分系统',
  systemSlogan: '每一份努力都值得被量化',
  copyright: '© 2026 Guild Wars 2'
})

// 从本地存储加载设置
const loadSettings = () => {
  const savedSettings = localStorage.getItem('gw2SystemSettings')
  if (savedSettings) {
    const settings = JSON.parse(savedSettings)
    Object.assign(systemSettings, settings)
  }
}

onMounted(() => {
  loadSettings()
  
  // 监听本地存储变化
  window.addEventListener('storage', (e) => {
    if (e.key === 'gw2SystemSettings') {
      loadSettings()
    }
  })
})
</script>

<style>
/* 全局样式 */
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f9fafb;
  color: #1f2937;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 动画 */
@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin-slow {
  animation: spin-slow 3s linear infinite;
}
</style>
