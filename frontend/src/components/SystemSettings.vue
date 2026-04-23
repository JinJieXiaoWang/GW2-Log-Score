<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="p-6 border-b border-gray-100">
      <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
        系统设置
      </h2>
    </div>
    <div class="p-6 space-y-8">
      <!-- 系统信息设置 -->
      <div class="space-y-4">
        <h3 class="text-sm font-bold text-gray-700 flex items-center gap-2">
          <span class="w-2 h-2 bg-indigo-500 rounded-full" />
          系统信息
        </h3>
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">系统名称</label>
            <input 
              v-model="settings.systemName" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
              placeholder="激战2日志评分系统"
            >
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">系统口号</label>
            <input 
              v-model="settings.systemSlogan" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
              placeholder="每一份努力都值得被量化"
            >
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-1">版权信息</label>
            <input 
              v-model="settings.copyright" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
              placeholder="© 2026 Guild Wars 2"
            >
          </div>
        </div>
      </div>
      
      <!-- 评分设置 -->
      <div class="space-y-4">
        <h3 class="text-sm font-bold text-gray-700 flex items-center gap-2">
          <span class="w-2 h-2 bg-green-500 rounded-full" />
          评分设置
        </h3>
        <div class="space-y-6">
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-3">WvW 评分权重</label>
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">DPS</label>
                <input 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  max="1" 
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                  placeholder="0.6"
                >
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">生存</label>
                <input 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  max="1" 
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                  placeholder="0.2"
                >
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">控制</label>
                <input 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  max="1" 
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                  placeholder="0.2"
                >
              </div>
            </div>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-400 mb-3">PVE 评分权重</label>
            <div class="grid grid-cols-3 gap-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">DPS</label>
                <input 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  max="1" 
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                  placeholder="0.7"
                >
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">生存</label>
                <input 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  max="1" 
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                  placeholder="0.15"
                >
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">控制</label>
                <input 
                  type="number" 
                  step="0.01" 
                  min="0" 
                  max="1" 
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                  placeholder="0.15"
                >
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 保存按钮 -->
      <div class="pt-6">
        <button 
          class="w-full py-3 bg-indigo-600 text-white rounded-xl text-sm font-bold shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all" 
          @click="saveSettings"
        >
          保存设置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const settings = ref({
  systemName: '激战2日志评分系统',
  systemSlogan: '每一份努力都值得被量化',
  copyright: '© 2026 Guild Wars 2'
})

const saveSettings = () => {
  // 保存设置到本地存储
  localStorage.setItem('gw2SystemSettings', JSON.stringify(settings.value))
  alert('设置保存成功')
}

// 从本地存储加载设置
const loadSettings = () => {
  const savedSettings = localStorage.getItem('gw2SystemSettings')
  if (savedSettings) {
    settings.value = JSON.parse(savedSettings)
  }
}

// 初始化时加载设置
loadSettings()
</script>

<style scoped>
/* 组件样式 */
</style>