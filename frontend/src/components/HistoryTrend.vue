<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="p-6 border-b border-gray-100">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center gap-2">
          <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
            历史趋势
          </h2>
          <div
            class="relative"
            @mouseenter="showTooltip = true"
            @mouseleave="showTooltip = false"
          >
            <svg
              class="w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div
              v-if="showTooltip"
              class="absolute top-full left-0 mt-1 bg-white p-3 rounded-lg shadow-lg border border-gray-100 z-10 w-64"
            >
              <p class="text-xs text-gray-600">
                历史趋势功能用于展示团队在不同时间段的表现变化，包括平均评分和参与人数的趋势。
              </p>
              <p class="text-xs text-gray-600 mt-1">
                通过选择不同的模式、时间范围和图表类型，可以更全面地了解团队的发展情况。
              </p>
            </div>
          </div>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <select
          v-model="selectedMode"
          class="text-xs border border-gray-200 rounded-lg px-3 py-1"
        >
          <option value="">
            所有模式
          </option>
          <option value="WvW">
            WvW
          </option>
          <option value="PVE">
            PVE
          </option>
        </select>
        <select
          v-model="selectedTimeRange"
          class="text-xs border border-gray-200 rounded-lg px-3 py-1"
        >
          <option value="7">
            7天
          </option>
          <option value="30">
            30天
          </option>
          <option value="90">
            90天
          </option>
          <option value="365">
            365天
          </option>
          <option value="custom">
            自定义
          </option>
        </select>
        <div
          v-if="selectedTimeRange === 'custom'"
          class="flex gap-2"
        >
          <input
            v-model="customStartDate"
            type="date"
            class="text-xs border border-gray-200 rounded-lg px-3 py-1"
          >
          <input
            v-model="customEndDate"
            type="date"
            class="text-xs border border-gray-200 rounded-lg px-3 py-1"
          >
          <button
            class="text-xs bg-indigo-600 text-white rounded-lg px-3 py-1 hover:bg-indigo-700 transition-colors"
            @click="applyCustomDateRange"
          >
            应用
          </button>
        </div>
        <select
          v-model="selectedChartType"
          class="text-xs border border-gray-200 rounded-lg px-3 py-1"
        >
          <option value="line">
            折线图
          </option>
          <option value="bar">
            柱状图
          </option>
          <option value="area">
            面积图
          </option>
        </select>
        <select
          v-model="selectedMetric"
          class="text-xs border border-gray-200 rounded-lg px-3 py-1"
        >
          <option value="avg_score">
            平均评分
          </option>
          <option value="player_count">
            玩家数量
          </option>
        </select>
      </div>
    </div>
    <div class="p-6">
      <div
        v-if="historyLogs.length > 0"
        ref="chartRef"
        style="height: 300px"
      />
      <div
        v-else
        class="text-center py-10 text-gray-400"
      >
        暂无历史数据
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  historyLogs: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chartInstance = null
const selectedMode = ref('')
const selectedTimeRange = ref('7')
const selectedChartType = ref('line')
const selectedMetric = ref('avg_score')
const showTooltip = ref(false)
const customStartDate = ref('')
const customEndDate = ref('')

// 监听历史数据变化
watch(() => props.historyLogs, () => {
  nextTick(() => {
    initChart()
  })
}, { deep: true })

// 监听筛选条件变化
watch([selectedMode, selectedTimeRange, selectedChartType, selectedMetric], async () => {
  // 这里可以添加筛选逻辑，重新获取数据
  // 暂时使用现有数据进行筛选
  nextTick(() => {
    initChart()
  })
})

// 应用自定义日期范围
const applyCustomDateRange = () => {
  // 这里可以添加自定义日期范围的处理逻辑
  // 暂时使用现有数据进行筛选
  nextTick(() => {
    initChart()
  })
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  // 从历史数据中提取趋势数据
  let dates = []
  let values = []
  
  if (props.historyLogs.length > 0) {
    // 按日期排序
    const sortedLogs = [...props.historyLogs].sort((a, b) => new Date(a.date) - new Date(b.date))
    
    // 提取日期和对应指标
    dates = sortedLogs.map(log => {
      const date = new Date(log.date)
      return `${date.getMonth() + 1}/${date.getDate()}`
    })
    
    if (selectedMetric.value === 'avg_score') {
      values = sortedLogs.map(log => parseFloat(log.avg_score.toFixed(2)))
    } else if (selectedMetric.value === 'player_count') {
      values = sortedLogs.map(log => log.player_count)
    }
  } else {
    // 模拟数据
    dates = ['4/16', '4/17', '4/18', '4/19', '4/20', '4/21', '4/22']
    if (selectedMetric.value === 'avg_score') {
      values = [65.00, 70.00, 68.00, 75.00, 72.00, 78.00, 80.00]
    } else if (selectedMetric.value === 'player_count') {
      values = [5, 6, 5, 7, 6, 8, 7]
    }
  }

  // 计算y轴范围
  let yMin = 0
  let yMax = 100
  if (values.length > 0) {
    if (selectedMetric.value === 'avg_score') {
      yMin = Math.max(0, Math.min(...values) - 5)
      yMax = Math.min(100, Math.max(...values) + 5)
    } else if (selectedMetric.value === 'player_count') {
      yMin = 0
      yMax = Math.max(...values) + 2
    }
  }

  // 图表类型配置
  let seriesConfig = {
    name: selectedMetric.value === 'avg_score' ? '平均评分' : '玩家数量',
    type: selectedChartType.value === 'area' ? 'line' : selectedChartType.value,
    smooth: selectedChartType.value !== 'bar',
    symbol: selectedChartType.value !== 'bar' ? 'circle' : 'none',
    symbolSize: 8,
    lineStyle: {
      color: '#4F46E5',
      width: 3
    },
    itemStyle: {
      color: '#4F46E5',
      borderColor: '#fff',
      borderWidth: 2
    },
    data: values
  }

  // 添加面积图配置
  if (selectedChartType.value === 'area') {
    seriesConfig.areaStyle = {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(79, 70, 229, 0.4)' },
        { offset: 1, color: 'rgba(79, 70, 229, 0.05)' }
      ])
    }
  }

  const option = {
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        fontSize: 10,
        color: '#9ca3af',
        rotate: 45
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(79, 70, 229, 0.2)'
        }
      }
    },
    yAxis: {
      type: 'value',
      min: yMin,
      max: yMax,
      axisLabel: {
        fontSize: 10,
        color: '#9ca3af',
        formatter: '{value}'
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(79, 70, 229, 0.2)'
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(79, 70, 229, 0.1)'
        }
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '3%',
      containLabel: true
    },
    series: [seriesConfig],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      },
      formatter: function(params) {
        const metricName = selectedMetric.value === 'avg_score' ? '平均评分' : '玩家数量'
        return `${params[0].name}<br/>${metricName}: ${params[0].value.toFixed(2)}`
      }
    }
  }
  
  chartInstance.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

onMounted(() => {
  nextTick(() => {
    initChart()
  })
})
</script>

<style scoped>
/* 组件样式 */
</style>