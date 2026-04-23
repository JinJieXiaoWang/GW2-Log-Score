<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="p-6 border-b border-gray-100">
      <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
        详细数据
      </h2>
    </div>
    <div class="p-6">
      <div
        v-if="selectedPlayer"
        class="space-y-6"
      >
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center text-sm font-black text-gray-400 border border-gray-200">
            {{ selectedPlayer.player_name[0] }}
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-800">
              {{ selectedPlayer.player_name }}
            </h3>
            <p class="text-sm text-gray-500">
              {{ selectedPlayer.profession }} - {{ selectedPlayer.role }}
            </p>
          </div>
        </div>
        
        <div
          v-if="radarData.length > 0"
          ref="radarChartRef"
          style="height: 300px"
        />
        <div
          v-else
          class="text-center py-10 text-gray-400"
        >
          暂无数据
        </div>
      </div>
      <div
        v-else
        class="text-center py-10 text-gray-400"
      >
        点击玩家查看详细数据
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  selectedPlayer: {
    type: Object,
    default: null
  }
})

const radarChartRef = ref(null)
let chartInstance = null

// 监听选中玩家变化
watch(() => props.selectedPlayer, () => {
  if (props.selectedPlayer) {
    nextTick(() => {
      initRadarChart()
    })
  }
}, { deep: true })

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(radarChartRef.value)
  
  const option = {
    radar: {
      indicator: radarData.value.map(item => ({
        name: item.name,
        max: 100
      })),
      shape: 'circle',
      splitNumber: 5,
      axisName: {
        fontSize: 10,
        color: '#6B7280'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(79, 70, 229, 0.1)'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(79, 70, 229, 0.02)', 'rgba(79, 70, 229, 0.04)', 'rgba(79, 70, 229, 0.06)', 'rgba(79, 70, 229, 0.08)', 'rgba(79, 70, 229, 0.1)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(79, 70, 229, 0.2)'
        }
      }
    },
    series: [{
      type: 'radar',
      data: [{
        value: radarData.value.map(item => item.value),
        name: props.selectedPlayer.player_name,
        areaStyle: {
          color: 'rgba(79, 70, 229, 0.2)'
        },
        lineStyle: {
          color: '#4F46E5',
          width: 2
        },
        itemStyle: {
          color: '#4F46E5'
        }
      }]
    }]
  }
  
  chartInstance.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

// 计算雷达图数据
const radarData = computed(() => {
  if (!props.selectedPlayer) return []
  
  try {
    const details = typeof props.selectedPlayer.details === 'string' 
      ? JSON.parse(props.selectedPlayer.details) 
      : props.selectedPlayer.details
    
    const detailScores = details?.detail_scores || {}
    const data = []
    
    Object.entries(detailScores).forEach(([key, value]) => {
      data.push({
        name: getScoreName(key),
        value: parseFloat(value)
      })
    })
    
    return data
  } catch (e) {
    return []
  }
})

// 评分名称映射
const getScoreName = (key) => {
  const nameMap = {
    dps: '伤害',
    cc: '控制',
    survival: '生存',
    stability: '稳固',
    resistance: '抗性',
    quickness: '急速',
    cleanses: '清症',
    strips: '剥取',
    downs: '倒地'
  }
  return nameMap[key] || key
}

onMounted(() => {
  if (props.selectedPlayer) {
    nextTick(() => {
      initRadarChart()
    })
  }
})
</script>

<style scoped>
/* 组件样式 */
</style>