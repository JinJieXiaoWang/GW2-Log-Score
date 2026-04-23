<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
  >
    <div class="bg-white rounded-2xl shadow-xl p-6 max-w-md w-full mx-4 transform transition-all duration-300">
      <div class="text-center space-y-4">
        <h3 class="text-lg font-bold text-gray-800 mt-0 mb-4">
          {{ title }}
        </h3>
        <p class="text-gray-600 whitespace-pre-line">
          {{ message }}
        </p>
        <button 
          class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg font-bold text-sm hover:bg-indigo-700 transition-colors" 
          @click="close"
        >
          {{ buttonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '提示'
  },
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'info', 'warning'].includes(value)
  },
  buttonText: {
    type: String,
    default: '确定'
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

const iconClass = computed(() => {
  const classes = {
    success: 'bg-green-100 text-green-600',
    error: 'bg-red-100 text-red-600',
    info: 'bg-blue-100 text-blue-600',
    warning: 'bg-yellow-100 text-yellow-600'
  }
  return classes[props.type] || classes.info
})
</script>

<style scoped>
/* 组件样式 */
</style>