<template>
  <div class="space-y-8">
    <!-- 顶部筛选 -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <div class="flex flex-wrap gap-4 justify-between items-center">
        <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
          历史数据分析
        </h2>
        <div class="flex items-center gap-4">
          <div class="flex flex-col justify-end">
            <label class="block text-xs font-bold text-gray-400 mb-1">时间范围</label>
            <select
              v-model="selectedTimeRange"
              class="text-xs border border-gray-200 rounded-lg px-3 py-2 w-32"
              @change="handleTimeRangeChange"
            >
              <option value="7">
                近七天
              </option>
              <option value="30">
                近三十天
              </option>
              <option value="custom">
                自定义
              </option>
            </select>
          </div>
          <div v-if="selectedTimeRange === 'custom'" class="flex items-end gap-2">
            <input
              v-model="startDate"
              type="date"
              class="text-xs border border-gray-200 rounded-lg px-3 py-2 w-32"
              @change="handleCustomDateChange"
            >
            <span class="text-xs text-gray-400 mb-2">至</span>
            <input
              v-model="endDate"
              type="date"
              class="text-xs border border-gray-200 rounded-lg px-3 py-2 w-32"
              @change="handleCustomDateChange"
            >
          </div>
        </div>
      </div>
    </div>

    <!-- 历史评分平均变化雷达图和历史趋势 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 历史评分平均变化雷达图 -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">
          历史评分平均变化雷达图
        </h2>
        <div
          ref="historyRadarChartRef"
          style="height: 300px"
        />
      </div>

      <!-- 历史趋势 -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">
          历史趋势
        </h2>
        <div
          ref="trendChartRef"
          style="height: 300px"
        />
      </div>
    </div>

    <!-- 历史战斗概览 -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">
        历史战斗概览
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          class="bg-gray-50 rounded-lg p-4 cursor-pointer hover:bg-gray-100 transition-colors"
          @click="showOverviewModal('battles')"
        >
          <p class="text-xs text-gray-400 mb-1">
            总战斗次数
          </p>
          <p class="text-lg font-bold text-gray-800">
            {{ historyLogs.length }}
          </p>
        </div>
        <div 
          class="bg-gray-50 rounded-lg p-4 cursor-pointer hover:bg-gray-100 transition-colors"
          @click="showOverviewModal('players')"
        >
          <p class="text-xs text-gray-400 mb-1">
            总玩家数
          </p>
          <p class="text-lg font-bold text-gray-800">
            {{ getTotalPlayers() }}
          </p>
        </div>
        <div 
          class="bg-gray-50 rounded-lg p-4 cursor-pointer hover:bg-gray-100 transition-colors"
          @click="showOverviewModal('scores')"
        >
          <p class="text-xs text-gray-400 mb-1">
            平均评分
          </p>
          <p class="text-lg font-bold text-gray-800">
            {{ getOverallAvgScore().toFixed(2) }}
          </p>
        </div>
      </div>
    </div>

    <!-- 概览弹窗 -->
    <div
      v-if="showOverviewModalVisible"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeOverviewModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-100 flex justify-between items-center">
          <h2 class="text-lg font-bold text-gray-800">
            {{ getOverviewModalTitle() }}
          </h2>
          <button 
            class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
            @click="closeOverviewModal">
            <svg
              class="w-4 h-4 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
        <div class="p-6">
          <!-- 总战斗次数 -->
          <div
            v-if="currentOverviewTab === 'battles'"
            class="overflow-x-auto"
          >
            <table class="w-full">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                    日期
                  </th>
                  <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                    模式
                  </th>
                  <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                    副本
                  </th>
                  <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                    玩家数
                  </th>
                  <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                    平均评分
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr
                  v-for="log in historyLogs"
                  :key="log.log_id"
                  class="hover:bg-gray-50/50 transition-colors"
                >
                  <td class="px-4 py-3 text-sm text-gray-700">
                    {{ formatDate(log.date) }}
                  </td>
                  <td class="px-4 py-3">
                    <span
                      :class="getModeClass(log.mode)"
                      class="text-[10px] px-2 py-1 rounded font-bold uppercase"
                    >
                      {{ log.mode }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-700">
                    {{ log.encounter_name }}
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-700">
                    {{ getLogPlayerCount(log.log_id) }}
                  </td>
                  <td class="px-4 py-3 text-sm font-bold text-gray-700">
                    {{ getLogAvgScore(log.log_id).toFixed(2) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- 总玩家数 -->
          <div
            v-else-if="currentOverviewTab === 'players'"
            class="space-y-4"
          >
            <div
              v-for="player in historyAvgScores"
              :key="player.name"
              class="flex justify-between items-center p-3 rounded-lg bg-gray-50"
            >
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-sm font-black text-gray-400 border border-gray-200">
                  {{ getDisplayNameInitial(player) }}
                </div>
                <div>
                  <button
                    class="text-sm font-bold text-gray-700 hover:text-indigo-600 transition-colors text-left"
                    @click="toggleDisplayNameMode(player)"
                  >
                    {{ getDisplayName(player) }}
                  </button>
                  <p
                    v-if="shouldShowSecondaryName(player)"
                    class="text-xs text-gray-400"
                  >
                    {{ getSecondaryName(player) }}
                  </p>
                </div>
              </div>
              <div class="text-right">
                <button
                  class="text-sm font-bold text-gray-700 hover:text-indigo-600 cursor-pointer"
                  @click="showPlayerDetailFromOverview(player)"
                >
                  {{ player.avg_score.toFixed(2) }}
                </button>
                <p class="text-xs text-gray-400">
                  {{ player.count }} 场战斗
                </p>
              </div>
            </div>
          </div>
          <!-- 平均评分 -->
          <div
            v-else
            class="bg-gray-50 rounded-lg p-6"
          >
            <h3 class="text-sm font-bold text-gray-700 mb-4">
              评分计算规则
            </h3>
            <div class="space-y-4 text-sm text-gray-600">
              <div>
                <p class="font-bold text-gray-700 mb-2">
                  总分计算方式
                </p>
                <p>总分 = (输出评分 + 破控评分 + 生存评分) / 3</p>
              </div>
              <div>
                <p class="font-bold text-gray-700 mb-2">
                  评分维度
                </p>
                <ul class="list-disc list-inside space-y-1">
                  <li>输出评分：基于玩家的伤害输出能力</li>
                  <li>破控评分：基于玩家的控制技能使用效果</li>
                  <li>生存评分：基于玩家的存活和防御能力</li>
                </ul>
              </div>
              <div>
                <p class="font-bold text-gray-700 mb-2">
                  数据来源
                </p>
                <p>所有评分数据均来自历史战斗记录的统计和分析</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史评分记录 -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-6 border-b border-gray-100">
        <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
          历史战斗记录
        </h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full border-collapse">
          <thead class="bg-gray-50">
            <tr class="border-b border-gray-100">
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest border-r border-gray-100 text-left">
                日期
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest border-r border-gray-100 text-left">
                模式
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest border-r border-gray-100 text-left">
                副本
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest border-r border-gray-100 text-left">
                玩家数
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest text-left">
                平均评分
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="log in historyLogs"
              :key="log.log_id"
              class="hover:bg-gray-50/50 transition-colors"
            >
              <td class="px-8 py-5 text-sm text-gray-700 border-r border-gray-100">
                {{ formatDate(log.date) }}
              </td>
              <td class="px-8 py-5 border-r border-gray-100">
                <span
                  :class="getModeClass(log.mode)"
                  class="text-[10px] px-2 py-1 rounded font-bold uppercase"
                >
                  {{ log.mode }}
                </span>
              </td>
              <td class="px-8 py-5 text-sm text-gray-700 border-r border-gray-100">
                {{ log.encounter_name }}
              </td>
              <td class="px-8 py-5 text-sm text-gray-700 border-r border-gray-100">
                {{ getLogPlayerCount(log.log_id) }}
              </td>
              <td class="px-8 py-5 text-sm font-bold text-gray-700">
                {{ getLogAvgScore(log.log_id).toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div
        v-if="historyLogs.length === 0"
        class="text-center py-10 text-gray-400"
      >
        暂无历史战斗记录
      </div>
    </div>

    <!-- 职业分布统计 -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">
        职业分布统计
      </h2>
      <div class="flex flex-col gap-6">
        <!-- 职业分布图表 -->
        <div>
          <div
            ref="professionChartRef"
            style="height: 300px"
          />
        </div>
      </div>
    </div>

    <!-- 玩家详情弹窗 -->
    <div
      v-if="showDetailModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeDetailModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <PlayerDetail 
          :player="selectedPlayer" 
          @close="closeDetailModal"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import PlayerDetail from '../components/PlayerDetail.vue'
import { getHistory, getScores } from '../utils/api'
import { useProfessions } from '../composables/index.js'
import * as echarts from 'echarts'

const historyLogs = ref([])
const scores = ref([])
const selectedTimeRange = ref('7') // 默认近七天
const startDate = ref('')
const endDate = ref('')

const showDetailModal = ref(false)
const selectedPlayer = ref(null)
const displayNameMode = ref({}) // 存储每个玩家的显示模式
const showOverviewModalVisible = ref(false)
const currentOverviewTab = ref('battles')

const historyRadarChartRef = ref(null)
const trendChartRef = ref(null)
const professionChartRef = ref(null)
let historyRadarChart = null
let trendChart = null
let professionChart = null

// 使用职业数据hook
const {
  loadProfessions,
  translateProfession,
  translations
} = useProfessions()

const historyAvgScores = computed(() => {
  const playerMap = {}
  
  scores.value.forEach(s => {
    const name = s.player_name || s.name || 'Unknown'
    if (!playerMap[name]) {
      playerMap[name] = {
        name: name,
        account: s.account || '',
        totalScore: 0,
        count: 0,
        scores: []
      }
    }
    playerMap[name].totalScore += s.total_score || s.score || 0
    playerMap[name].count += 1
    playerMap[name].scores.push(s)
  })
  
  return Object.values(playerMap)
    .map(p => ({
      ...p,
      avg_score: p.count > 0 ? p.totalScore / p.count : 0
    }))
    .sort((a, b) => b.avg_score - a.avg_score)
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

const getModeClass = (mode) => {
  if (mode && mode.includes('WvW')) return 'bg-indigo-50 text-indigo-600'
  if (mode && mode.includes('PVE')) return 'bg-green-50 text-green-600'
  return 'bg-gray-50 text-gray-600'
}

const getLogAvgScore = (logId) => {
  const logScores = scores.value.filter(s => s.log_id === logId)
  if (logScores.length === 0) return 0
  const totalScore = logScores.reduce((sum, s) => sum + (s.total_score || s.score || 0), 0)
  return totalScore / logScores.length
}

const getTotalPlayers = () => {
  const playerSet = new Set()
  scores.value.forEach(s => {
    if (s.player_name) playerSet.add(s.player_name)
    else if (s.name) playerSet.add(s.name)
    else if (s.account) playerSet.add(s.account)
  })
  return playerSet.size
}

const getOverallAvgScore = () => {
  if (scores.value.length === 0) return 0
  const totalScore = scores.value.reduce((sum, s) => sum + (s.total_score || s.score || 0), 0)
  return totalScore / scores.value.length
}

const getLogPlayerCount = (logId) => {
  const logScores = scores.value.filter(s => s.log_id === logId)
  return logScores.length
}

const getPlayerKey = (player) => {
  return player.name || player.player_name || player.account || 'unknown'
}

const getPlayerDisplayNameMode = (player) => {
  const key = getPlayerKey(player)
  return displayNameMode.value[key] || 'name'
}

const toggleDisplayNameMode = (player) => {
  const key = getPlayerKey(player)
  const currentMode = getPlayerDisplayNameMode(player)
  
  if (currentMode === 'name') {
    displayNameMode.value[key] = 'account'
  } else {
    displayNameMode.value[key] = 'name'
  }
}

const getDisplayName = (player) => {
  const name = player.name || player.player_name || ''
  const account = player.account || ''
  const mode = getPlayerDisplayNameMode(player)
  
  if (mode === 'name') {
    return name || account || 'Unknown'
  } else {
    return account || name || 'Unknown'
  }
}

const getSecondaryName = (player) => {
  const name = player.name || player.player_name || ''
  const account = player.account || ''
  const mode = getPlayerDisplayNameMode(player)
  
  if (mode === 'name' && account && account !== name) return account
  if (mode === 'account' && name && name !== account) return name
  
  return ''
}

const shouldShowSecondaryName = (player) => {
  const name = player.name || player.player_name || ''
  const account = player.account || ''
  
  if (name && account && name !== account) return true
  
  return false
}

const getDisplayNameInitial = (player) => {
  const displayName = getDisplayName(player)
  return (displayName || 'U')[0]
}





const showOverviewModal = (tab) => {
  currentOverviewTab.value = tab
  showOverviewModalVisible.value = true
}

const closeOverviewModal = () => {
  showOverviewModalVisible.value = false
}

const getOverviewModalTitle = () => {
  const titles = {
    'battles': '战斗记录',
    'players': '玩家列表',
    'scores': '评分规则'
  }
  return titles[currentOverviewTab.value] || '概览'
}

const showPlayerDetailFromOverview = (player) => {
  closeOverviewModal()
  showPlayerDetail(player)
}

const initProfessionChart = () => {
  if (!professionChartRef.value) return
  
  // 确保容器有固定尺寸
  const container = professionChartRef.value
  container.style.height = '300px'
  container.style.width = '100%'
  
  if (professionChart) {
    professionChart.dispose()
  }
  
  // 延迟初始化，确保容器尺寸已计算
  setTimeout(() => {
    if (!professionChartRef.value) return
    
    professionChart = echarts.init(professionChartRef.value)
    
    // 统计职业分布
    const professionMap = {}
    scores.value.forEach(s => {
      const profession = s.profession || 'Unknown'
      const translatedProfession = translateProfession(profession)
      professionMap[translatedProfession] = (professionMap[translatedProfession] || 0) + 1
    })
    
    const professionData = Object.entries(professionMap).map(([name, value]) => ({
      name,
      value
    }))
    
    const hasData = professionData.length > 0
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'horizontal',
        bottom: 10,
        data: Object.keys(professionMap)
      },
      series: hasData ? [
        {
          name: '职业分布',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '18',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: professionData
        }
      ] : [],
      graphic: !hasData ? [
        {
          type: 'text',
          left: 'center',
          top: 'center',
          style: {
            text: '暂无数据',
            fill: '#999',
            fontSize: 14
          }
        }
      ] : []
    }
    
    professionChart.setOption(option)
    
    // 添加窗口大小变化监听
    const handleResize = () => {
      professionChart?.resize()
    }
    
    window.addEventListener('resize', handleResize)
    
    // 清理函数
    return () => {
      window.removeEventListener('resize', handleResize)
      if (professionChart) {
        professionChart.dispose()
        professionChart = null
      }
    }
  }, 100)
}

const showPlayerDetail = (player) => {
  // 查找该玩家最新的评分记录
  if (player.scores && player.scores.length > 0) {
    selectedPlayer.value = player.scores[0]
  } else {
    selectedPlayer.value = player
  }
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedPlayer.value = null
}

const initHistoryRadarChart = () => {
  if (!historyRadarChartRef.value) return
  
  // 确保容器有固定尺寸
  const container = historyRadarChartRef.value
  container.style.height = '300px'
  container.style.width = '100%'
  
  if (historyRadarChart) {
    historyRadarChart.dispose()
  }
  
  // 延迟初始化，确保容器尺寸已计算
  setTimeout(() => {
    if (!historyRadarChartRef.value) return
    
    historyRadarChart = echarts.init(historyRadarChartRef.value)
    
    // 从实际数据计算雷达图数据
    let radarData = []
    let hasData = false
    
    if (scores.value.length > 0) {
      // 计算各项指标的平均值
      let totalDps = 0
      let totalSurvival = 0
      let totalCc = 0
      let totalSupport = 0
      let totalTeam = 0
      let count = 0
      
      scores.value.forEach(score => {
        totalDps += score.score_dps || 0
        totalSurvival += score.score_survival || 0
        totalCc += score.score_cc || 0
        totalSupport += score.score_boon || 0
        totalTeam += score.total_score || 0
        count++
      })
      
      if (count > 0) {
        const avgDps = totalDps / count
        const avgSurvival = totalSurvival / count
        const avgCc = totalCc / count
        const avgSupport = totalSupport / count
        const avgTeam = totalTeam / count
        
        radarData = [
          {
            value: [avgDps, avgSurvival, avgCc, avgSupport, avgTeam],
            name: '团队平均',
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
        hasData = true
      }
    }
    
    const option = {
      radar: {
        indicator: [
          { name: '输出', max: 100 },
          { name: '生存', max: 100 },
          { name: '破控', max: 100 },
          { name: '辅助', max: 100 },
          { name: '团队', max: 100 }
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
      series: hasData ? [
        {
          name: '历史平均',
          type: 'radar',
          data: radarData
        }
      ] : [],
      tooltip: {
        trigger: 'item'
      },
      graphic: !hasData ? [
        {
          type: 'text',
          left: 'center',
          top: 'center',
          style: {
            text: '暂无数据',
            fill: '#999',
            fontSize: 14
          }
        }
      ] : []
    }
    
    historyRadarChart.setOption(option)
    
    // 添加窗口大小变化监听
    const handleResize = () => {
      historyRadarChart?.resize()
    }
    
    window.addEventListener('resize', handleResize)
    
    // 清理函数
    return () => {
      window.removeEventListener('resize', handleResize)
      if (historyRadarChart) {
        historyRadarChart.dispose()
        historyRadarChart = null
      }
    }
  }, 100)
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  // 确保容器有固定尺寸
  const container = trendChartRef.value
  container.style.height = '300px'
  container.style.width = '100%'
  
  if (trendChart) {
    trendChart.dispose()
  }
  
  // 延迟初始化，确保容器尺寸已计算
  setTimeout(() => {
    if (!trendChartRef.value) return
    
    trendChart = echarts.init(trendChartRef.value)
    
    // 从实际数据计算趋势图数据
    let dates = []
    let values = []
    let hasData = false
    
    if (historyLogs.value.length > 0) {
      // 按日期分组计算平均评分
      const dateMap = {}
      
      historyLogs.value.forEach(log => {
        const date = new Date(log.date)
        const dateStr = `${date.getMonth() + 1}/${date.getDate()}`
        
        if (!dateMap[dateStr]) {
          dateMap[dateStr] = {
            totalScore: 0,
            count: 0
          }
        }
        
        const logScore = getLogAvgScore(log.log_id)
        dateMap[dateStr].totalScore += logScore
        dateMap[dateStr].count += 1
      })
      
      // 按日期排序
      const sortedDates = Object.keys(dateMap).sort((a, b) => {
        const [aMonth, aDay] = a.split('/').map(Number)
        const [bMonth, bDay] = b.split('/').map(Number)
        return aMonth * 31 + aDay - (bMonth * 31 + bDay)
      })
      
      dates = sortedDates
      values = sortedDates.map(date => {
        const data = dateMap[date]
        return data.totalScore / data.count
      })
      
      hasData = dates.length > 0
    }
    
    const option = {
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          fontSize: 10
        }
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100
      },
      series: hasData ? [
        {
          data: values,
          type: 'line',
          smooth: true,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(79, 70, 229, 0.4)' },
              { offset: 1, color: 'rgba(79, 70, 229, 0.05)' }
            ])
          },
          lineStyle: {
            color: '#4F46E5'
          },
          itemStyle: {
            color: '#4F46E5'
          }
        }
      ] : [],
      tooltip: {
        trigger: 'axis'
      },
      graphic: !hasData ? [
        {
          type: 'text',
          left: 'center',
          top: 'center',
          style: {
            text: '暂无数据',
            fill: '#999',
            fontSize: 14
          }
        }
      ] : []
    }
    
    trendChart.setOption(option)
    
    // 添加窗口大小变化监听
    const handleResize = () => {
      trendChart?.resize()
    }
    
    window.addEventListener('resize', handleResize)
    
    // 清理函数
    return () => {
      window.removeEventListener('resize', handleResize)
      if (trendChart) {
        trendChart.dispose()
        trendChart = null
      }
    }
  }, 100)
}

const loadHistory = async (timeRange = '7', start = null, end = null) => {
  try {
    const [historyResponse, scoresResponse] = await Promise.all([
      getHistory('WvW', timeRange),
      getScores()
    ])
    
    if (historyResponse.data) {
      historyLogs.value = historyResponse.data.data || historyResponse.data || []
    }
    
    if (scoresResponse.data && scoresResponse.data.data) {
      scores.value = scoresResponse.data.data
    } else if (scoresResponse.data) {
      scores.value = scoresResponse.data
    }
    
    // 根据时间范围过滤数据
    if (timeRange === 'custom' && start && end) {
      const startDateObj = new Date(start)
      const endDateObj = new Date(end)
      endDateObj.setHours(23, 59, 59, 999)
      
      historyLogs.value = historyLogs.value.filter(log => {
        const logDate = new Date(log.date)
        return logDate >= startDateObj && logDate <= endDateObj
      })
      
      scores.value = scores.value.filter(score => {
        const scoreDate = new Date(score.date)
        return scoreDate >= startDateObj && scoreDate <= endDateObj
      })
    } else if (timeRange !== 'custom') {
      const days = parseInt(timeRange)
      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - days)
      
      historyLogs.value = historyLogs.value.filter(log => {
        const logDate = new Date(log.date)
        return logDate >= cutoffDate
      })
      
      scores.value = scores.value.filter(score => {
        const scoreDate = new Date(score.date)
        return scoreDate >= cutoffDate
      })
    }
    
    console.log('历史日志数据:', historyLogs.value)
    console.log('评分数据:', scores.value)
    
    nextTick(() => {
      initHistoryRadarChart()
      initTrendChart()
      initProfessionChart()
    })
  } catch (error) {
    console.error('加载历史数据失败:', error)
  }
}

const handleTimeRangeChange = () => {
  if (selectedTimeRange.value === 'custom') {
    // 设置默认自定义日期范围为最近7天
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 7)
    
    startDate.value = start.toISOString().split('T')[0]
    endDate.value = end.toISOString().split('T')[0]
  } else {
    loadHistory(selectedTimeRange.value)
  }
}

const handleCustomDateChange = () => {
  if (startDate.value && endDate.value) {
    loadHistory('custom', startDate.value, endDate.value)
  }
}

onMounted(async () => {
  // 先加载职业数据
  await loadProfessions()
  // 然后加载历史数据
  loadHistory()
})
</script>

<style scoped>
/* 视图样式 */
button:focus {
  outline: none;
  box-shadow: none;
}

button:focus-visible {
  outline: none;
  box-shadow: none;
}
</style>
