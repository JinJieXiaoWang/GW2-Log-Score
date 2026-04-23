<template>
  <div class="p-8">
    <!-- 头部 -->
    <div class="flex justify-between items-start mb-8">
      <div class="flex items-center gap-4">
        <div class="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center text-2xl font-black text-gray-600 border border-gray-200">
          {{ (player.player_name || 'U')[0] }}
        </div>
        <div>
          <h2 class="text-xl font-black text-gray-800">
            {{ player.player_name }}
          </h2>
          <p class="text-sm text-gray-500">
            {{ player.account || '' }}
          </p>
          <div class="flex items-center gap-2 mt-2">
            <span class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded font-bold uppercase">
              {{ player.profession || 'Unknown' }}
            </span>
            <span
              :class="roleBadgeClass(player.role)"
              class="text-xs px-2 py-1 rounded font-bold uppercase"
            >
              {{ player.role || 'DPS' }}
            </span>
          </div>
        </div>
      </div>
      <button 
        class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
        @click="$emit('close')"
      >
        <svg
          class="w-5 h-5 text-gray-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <!-- 总分 -->
    <div class="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-6 text-white mb-8 shadow-lg">
      <div class="text-sm font-bold opacity-80 mb-1">
        最终评分
      </div>
      <div class="text-4xl font-black">
        {{ (player.total_score || player.score || 0).toFixed(2) }}
      </div>
      <div class="mt-2 text-xs">
        <span class="bg-white bg-opacity-20 backdrop-blur-sm px-2 py-0.5 rounded-full">
          {{ getScoreLevel(player.total_score || player.score || 0) }}
        </span>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- 雷达图 -->
      <div class="bg-gray-50 rounded-2xl p-6">
        <h3 class="text-sm font-bold text-gray-700 uppercase tracking-widest mb-4">
          能力雷达图
        </h3>
        <div
          ref="radarChartRef"
          style="height: 300px"
        />
      </div>

      <!-- 详细数据 -->
      <div class="space-y-4">
        <h3 class="text-sm font-bold text-gray-700 uppercase tracking-widest">
          详细数据
        </h3>
        
        <!-- 战斗数据 -->
        <div class="bg-white rounded-xl border border-gray-100 p-4">
          <h4 class="text-xs font-bold text-gray-500 uppercase mb-3">
            战斗数据
          </h4>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="text-xs text-gray-500">
                秒伤
              </div>
              <div class="text-lg font-bold text-gray-800">
                {{ formatNumber(details.dps || details.dps_val || 0) }}
              </div>
            </div>
            <div>
              <div class="text-xs text-gray-500">
                破控
              </div>
              <div class="text-lg font-bold text-gray-800">
                {{ formatNumber(details.cc || details.cc_val || 0) }}
              </div>
            </div>
            <div>
              <div class="text-xs text-gray-500">
                倒地次数
              </div>
              <div class="text-lg font-bold text-gray-800">
                {{ details.downs || 0 }}
              </div>
            </div>
            <div>
              <div class="text-xs text-gray-500">
                死亡次数
              </div>
              <div class="text-lg font-bold text-gray-800">
                {{ details.deaths || 0 }}
              </div>
            </div>
          </div>
        </div>

        <!-- 核心指标 -->
        <div class="bg-white rounded-xl border border-gray-100 p-4">
          <h4 class="text-xs font-bold text-gray-500 uppercase mb-3">
            核心指标
          </h4>
          <div class="space-y-3">
            <div 
              v-for="(value, key) in coreMetrics" 
              :key="key" 
              class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 transition-colors relative"
            >
              <span class="text-sm text-gray-600">{{ key }}</span>
              <div class="flex items-center gap-3">
                <div class="w-32 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500"
                    :style="{ width: Math.min(100, typeof value === 'number' ? value : 0) + '%' }"
                  />
                </div>
                <span class="text-sm font-bold text-gray-800 w-12 text-right">{{ typeof value === 'number' ? value.toFixed(2) : value }}</span>
              </div>
              <!-- 悬停提示 -->
              <div class="absolute right-0 top-full mt-2 bg-gray-800 text-white text-xs p-2 rounded-lg shadow-lg opacity-0 invisible hover:opacity-100 hover:visible transition-all duration-200 z-10">
                <div>{{ key }}: {{ typeof value === 'number' ? value.toFixed(2) : value }}%</div>
                <div class="text-gray-300 mt-1">
                  基于统计规则计算
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 其他数据 -->
        <div
          v-if="hasOtherData"
          class="bg-white rounded-xl border border-gray-100 p-4"
        >
          <h4 class="text-xs font-bold text-gray-500 uppercase mb-3">
            其他数据
          </h4>
          <div class="space-y-2 text-sm text-gray-600">
            <div
              v-if="details.cleanses !== undefined"
              class="flex justify-between"
            >
              <span>净化次数</span>
              <span class="font-bold">{{ details.cleanses }}</span>
            </div>
            <div
              v-if="details.strips !== undefined"
              class="flex justify-between"
            >
              <span>增益剥离</span>
              <span class="font-bold">{{ details.strips }}</span>
            </div>
            <div
              v-if="details.cleanses_per_min !== undefined"
              class="flex justify-between"
            >
              <span>每分钟净化</span>
              <span class="font-bold">{{ details.cleanses_per_min.toFixed(2) }}</span>
            </div>
            <div
              v-if="details.strips_per_min !== undefined"
              class="flex justify-between"
            >
              <span>每分钟剥离</span>
              <span class="font-bold">{{ details.strips_per_min.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  player: {
    type: Object,
    required: true
  }
})

defineEmits(['close'])

const radarChartRef = ref(null)
let radarChart = null

const details = computed(() => {
  if (!props.player.details) return {}
  if (typeof props.player.details === 'string') {
    try {
      return JSON.parse(props.player.details)
    } catch (e) {
      return {}
    }
  }
  return props.player.details
})

const coreMetrics = computed(() => {
  const role = props.player.role || details.value.role || 'DPS'
  const detailScores = details.value.detail_scores || details.value.scores || {}
  const metrics = {}
  
  if (role === 'DPS') {
    metrics['输出评分'] = detailScores.dps !== undefined ? detailScores.dps : 0
    metrics['破控评分'] = detailScores.cc !== undefined ? detailScores.cc : 0
    metrics['生存评分'] = detailScores.survival !== undefined ? detailScores.survival : 0
  } else if (role === 'SUPPORT') {
    metrics['稳固覆盖'] = detailScores.stability !== undefined ? detailScores.stability : 0
    metrics['抗性覆盖'] = detailScores.resistance !== undefined ? detailScores.resistance : 0
    metrics['急速覆盖'] = detailScores.quickness !== undefined ? detailScores.quickness : 0
    metrics['敏捷覆盖'] = detailScores.alacrity !== undefined ? detailScores.alacrity : 0
    metrics['净化评分'] = detailScores.cleanses !== undefined ? detailScores.cleanses : 0
    metrics['增益剥离'] = detailScores.strips !== undefined ? detailScores.strips : 0
    metrics['生存评分'] = detailScores.survival !== undefined ? detailScores.survival : 0
  } else {
    metrics['净化评分'] = detailScores.cleanses !== undefined ? detailScores.cleanses : 0
    metrics['增益剥离'] = detailScores.strips !== undefined ? detailScores.strips : 0
    metrics['破控评分'] = detailScores.cc !== undefined ? detailScores.cc : 0
    metrics['生存评分'] = detailScores.survival !== undefined ? detailScores.survival : 0
  }
  
  return metrics
})

const hasOtherData = computed(() => {
  return details.value.cleanses !== undefined || 
         details.value.strips !== undefined ||
         details.value.cleanses_per_min !== undefined ||
         details.value.strips_per_min !== undefined
})

const getScoreLevel = (score) => {
  if (score >= 95) return 'S+ 级'
  if (score >= 90) return 'S 级'
  if (score >= 85) return 'A+ 级'
  if (score >= 80) return 'A 级'
  if (score >= 75) return 'B+ 级'
  if (score >= 70) return 'B 级'
  if (score >= 60) return 'C 级'
  if (score >= 50) return 'D 级'
  if (score >= 30) return 'E 级'
  return 'F 级'
}

const roleBadgeClass = (role) => {
  switch (role) {
    case 'DPS':
      return 'bg-red-100 text-red-600'
    case 'SUPPORT':
      return 'bg-blue-100 text-blue-600'
    case 'UTILITY':
      return 'bg-green-100 text-green-600'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  if (typeof num !== 'number') return num
  return num.toLocaleString('zh-CN')
}

const initRadarChart = () => {
  if (!radarChartRef.value) return
  
  // 确保容器有固定尺寸
  const container = radarChartRef.value
  container.style.height = '300px'
  container.style.width = '100%'
  
  if (radarChart) {
    radarChart.dispose()
  }
  
  // 延迟初始化，确保容器尺寸已计算
  setTimeout(() => {
    if (!radarChartRef.value) return
    
    radarChart = echarts.init(radarChartRef.value)
    
    const metrics = coreMetrics.value
    const metricKeys = Object.keys(metrics)
    
    if (metricKeys.length === 0) {
      // 默认雷达图
      const option = {
        radar: {
          indicator: [
            { name: '输出', max: 100 },
            { name: '生存', max: 100 },
            { name: '破控', max: 100 },
            { name: '辅助', max: 100 }
          ],
          splitArea: {
            areaStyle: {
              color: ['rgba(79, 70, 229, 0.05)', 'rgba(79, 70, 229, 0.1)']
            }
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(79, 70, 229, 0.2)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(79, 70, 229, 0.2)'
            }
          }
        },
        series: [
          {
            name: '能力值',
            type: 'radar',
            data: [
              {
                value: [60, 70, 50, 40],
                name: '当前玩家',
                areaStyle: {
                  color: 'rgba(79, 70, 229, 0.3)'
                },
                lineStyle: {
                  color: '#4F46E5',
                  width: 2
                },
                itemStyle: {
                  color: '#4F46E5'
                }
              }
            ]
          }
        ],
        tooltip: {
          trigger: 'item'
        }
      }
      radarChart.setOption(option)
    } else {
      const option = {
        radar: {
          indicator: metricKeys.map(key => ({ name: key, max: 100 })),
          splitArea: {
            areaStyle: {
              color: ['rgba(79, 70, 229, 0.05)', 'rgba(79, 70, 229, 0.1)']
            }
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(79, 70, 229, 0.2)'
            }
          },
          splitLine: {
            lineStyle: {
              color: 'rgba(79, 70, 229, 0.2)'
            }
          }
        },
        series: [
          {
            name: '能力值',
            type: 'radar',
            data: [
              {
                value: metricKeys.map(key => Math.min(100, Math.max(0, typeof metrics[key] === 'number' ? metrics[key] : 0))),
                name: '当前玩家',
                areaStyle: {
                  color: 'rgba(79, 70, 229, 0.3)'
                },
                lineStyle: {
                  color: '#4F46E5',
                  width: 2
                },
                itemStyle: {
                  color: '#4F46E5'
                }
              }
            ]
          }
        ],
        tooltip: {
          trigger: 'item'
        }
      }
      radarChart.setOption(option)
    }
    
    // 添加窗口大小变化监听
    const handleResize = () => {
      radarChart?.resize()
    }
    
    window.addEventListener('resize', handleResize)
    
    // 清理函数
    return () => {
      window.removeEventListener('resize', handleResize)
      if (radarChart) {
        radarChart.dispose()
        radarChart = null
      }
    }
  }, 100)
}

watch(() => props.player, () => {
  nextTick(() => {
    initRadarChart()
  })
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    initRadarChart()
  })
})
</script>

<style scoped>
/* 样式 */
button:focus {
  outline: none;
  box-shadow: none;
}

button:focus-visible {
  outline: none;
  box-shadow: none;
}
</style>
