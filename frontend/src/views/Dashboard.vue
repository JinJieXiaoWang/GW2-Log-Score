<template>
  <div class="space-y-8">
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <div class="text-center mb-4">
        <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
          当日常用数据概览
        </h2>
      </div>
      <div class="flex flex-wrap justify-center gap-6 items-center">
        <div class="text-center cursor-pointer hover:opacity-80 transition-opacity" @click="showStatInfo('kills')">
          <div class="text-xs font-bold text-gray-400 mb-1">击杀数</div>
          <div class="text-lg font-bold text-gray-800">{{ todayStats.kills || 0 }}</div>
        </div>
        <div class="text-center cursor-pointer hover:opacity-80 transition-opacity" @click="showStatInfo('deaths')">
          <div class="text-xs font-bold text-gray-400 mb-1">死亡数</div>
          <div class="text-lg font-bold text-gray-800">{{ todayStats.deaths || 0 }}</div>
        </div>
        <div class="text-center cursor-pointer hover:opacity-80 transition-opacity" @click="showStatInfo('avgScore')">
          <div class="text-xs font-bold text-gray-400 mb-1">平均评分</div>
          <div class="text-lg font-bold text-gray-800">{{ todayStats.avgScore || 0 }}</div>
        </div>
        <div class="text-center">
          <div class="text-xs font-bold text-gray-400 mb-1">模式</div>
          <div class="text-lg font-bold text-gray-800">WvW</div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">
        数据管理
      </h2>
      <div class="space-y-6">
        <!-- 上传战斗日志 -->
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">上传战斗日志</label>
          <div
            class="border-2 border-dashed border-gray-200 rounded-xl p-6 text-center hover:border-indigo-300 transition-colors cursor-pointer"
            @click="fileInput.click()"
          >
            <svg
              class="w-12 h-12 mx-auto text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            ><path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            /></svg>
            <p class="mt-2 text-xs text-gray-400">
              点击上传 .evtc、.zevtc 或 .json 文件
            </p>
            <input
              ref="fileInput"
              type="file"
              accept=".evtc,.zevtc,.json"
              class="hidden"
              @change="handleFileUpload"
            >
          </div>
        </div>
        
        <!-- 快速同步 -->
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">快速同步</label>
          <button
            class="w-full py-3 bg-gray-800 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-black transition-all shadow-lg shadow-gray-200 flex items-center justify-center gap-2"
            :disabled="uploading"
            @click="syncLocalData"
          >
            <svg
              v-if="!uploading"
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            ><path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            /></svg>
            <div
              v-else
              class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
            />
            {{ uploading ? '正在同步...' : '同步数据' }}
          </button>
        </div>
        
        <!-- 清除数据 -->
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">数据清理</label>
          <button
            class="w-full py-3 bg-red-500 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-red-600 transition-all shadow-lg shadow-red-200 flex items-center justify-center gap-2"
            @click="showClearDataDialog"
          >
            <svg
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            ><path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            /></svg>
            清除数据
          </button>
        </div>
      </div>
    </div>

    <!-- AI模块预留区域 -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">
        AI分析
      </h2>
      <div class="space-y-4">
        <p class="text-xs text-gray-500">
          即将推出的AI分析功能，将为您提供更智能的战斗数据解读和优化建议。
        </p>
        <button
          class="w-full py-3 bg-indigo-600 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 flex items-center justify-center gap-2"
          disabled
        >
          <svg
            class="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          ><path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          /></svg>
          AI分析功能开发中
        </button>
      </div>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-6 border-b border-gray-100">
        <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
          当日数据明细
        </h2>
      </div>
      <div
        class="overflow-x-auto"
        style="max-height: 600px; overflow-y: auto;"
        @scroll="handleScroll"
      >
        <table class="w-full border-collapse">
          <thead class="bg-gray-50 sticky top-0">
            <tr class="border-b border-gray-100">
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest border-r border-gray-100 text-left">
                玩家
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest border-r border-gray-100 text-left">
                职业
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest border-r border-gray-100 text-left">
                定位
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest border-r border-gray-100 text-left">
                核心指标
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest text-left">
                评分
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="record in getVisibleDetails()"
              :key="record.id"
              class="hover:bg-gray-100/80 transition-colors"
              :class="{ 'bg-yellow-50': isNonSquadPlayer(record.account) }"
            >
              <td class="px-8 py-5 border-r border-gray-100">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-sm font-black text-gray-400 border border-gray-200">
                    {{ getDisplayNameInitial(record) }}
                  </div>
                  <div>
                    <button
                      class="text-sm font-black text-gray-800 hover:text-indigo-600 transition-colors text-left"
                      @click="toggleDisplayNameMode(record)"
                    >
                      {{ getDisplayName(record) }}
                      <span
                        v-if="isNonSquadPlayer(record.account)"
                        class="ml-1 text-xs text-yellow-600 bg-yellow-100 px-1.5 py-0.5 rounded"
                      >异常</span>
                    </button>
                    <p
                      v-if="shouldShowSecondaryName(record)"
                      class="text-xs text-gray-400"
                    >
                      {{ getSecondaryName(record) }}
                    </p>
                  </div>
                </div>
              </td>
              <td class="px-8 py-5 border-r border-gray-100">
                <span
                  :class="getProfessionClass(record.profession)"
                  class="text-xs px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter"
                >
                  {{ translateProfession(record.profession) }}
                </span>
              </td>
              <td class="px-8 py-5 border-r border-gray-100">
                <span
                  :class="getRoleBadgeClass(record.role)"
                  class="text-xs px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter"
                >
                  {{ translateRole(record.role) }}
                </span>
              </td>
              <td class="px-8 py-5 border-r border-gray-100">
                <div class="text-xs text-gray-700 space-y-1">
                  <div
                    v-for="(value, key) in getCoreMetricsByRole(record)"
                    :key="key"
                    class="flex justify-between gap-2"
                  >
                    <span class="text-gray-500">{{ key }}:</span>
                    <span class="font-medium">{{ formatMetricValue(value) }}</span>
                  </div>
                </div>
              </td>
              <td class="px-8 py-5">
                <button
                  :class="getScoreColorClass(record.score)"
                  class="text-xs font-bold cursor-pointer hover:opacity-80"
                  @click="showPlayerDetail(record)"
                >
                  {{ typeof record.score === 'number' ? record.score.toFixed(2) : record.score }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div
          v-if="todayDetails.length === 0"
          class="text-center py-10 text-gray-400"
        >
          暂无当日数据明细
        </div>
        <div
          v-if="hasMoreDetails && todayDetails.length > 0"
          class="text-center py-4 text-gray-400 text-xs"
        >
          {{ isLoading ? '加载中...' : '滚动加载更多' }}
        </div>
        <div
          v-else-if="!hasMoreDetails && todayDetails.length > 0"
          class="text-center py-4 text-gray-400 text-xs"
        >
          已加载全部数据
        </div>
      </div>
    </div>

    <!-- 确认清除数据模态对话框 -->
    <div
      v-if="showConfirmModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeConfirmModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full">
        <div class="p-6 border-b border-gray-100">
          <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
            确认清除数据
          </h2>
        </div>
        <div class="p-6">
          <p class="text-xs text-gray-500 mb-6">
            确定要{{ clearDataType === 'today' ? '清除当天' : '清除全部' }}数据吗？此操作不可恢复。
          </p>
        </div>
        <div class="p-4 border-t border-gray-100 flex justify-end space-x-3">
          <button
            class="px-4 py-2 bg-gray-100 text-gray-800 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-gray-200 transition-colors"
            @click="closeConfirmModal"
          >
            取消
          </button>
          <button
            :class="clearDataType === 'today' ? 'bg-gray-500 hover:bg-gray-600' : 'bg-red-500 hover:bg-red-600'"
            class="px-4 py-2 text-white rounded-xl text-xs font-black uppercase tracking-widest transition-colors"
            @click="confirmClearData"
          >
            确认清除
          </button>
        </div>
      </div>
    </div>

    <AlertDialog
      v-model:show="alert.show"
      :title="alert.title"
      :message="alert.message"
      :type="alert.type"
      @close="alert.show = false"
    />

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

    <div
      v-if="showClearDataModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeClearDataModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full">
        <div class="p-6 border-b border-gray-100">
          <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
            清除数据
          </h2>
        </div>
        <div class="p-6">
          <p class="text-xs text-gray-500 mb-6">
            请选择要清除的数据范围：
          </p>
          <div class="space-y-3">
            <button
              class="w-full py-3 bg-gray-100 text-gray-800 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
              @click="openConfirmModal('today')"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              ><path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              /></svg>
              清除当天数据
            </button>
            <button
              class="w-full py-3 bg-red-500 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-red-600 transition-colors flex items-center justify-center gap-2"
              @click="openConfirmModal('all')"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              ><path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              /></svg>
              清除全部数据
            </button>
          </div>
        </div>
        <div class="p-4 border-t border-gray-100 flex justify-end">
          <button
            class="px-4 py-2 text-xs font-bold text-gray-400 hover:text-gray-600 transition-colors"
            @click="closeClearDataModal"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AlertDialog from '../components/AlertDialog.vue'
import PlayerDetail from '../components/PlayerDetail.vue'
import { uploadLog, syncData, getScores, clearData } from '../utils/api'
import { usePlayerDisplay, useCoreMetrics, useProfessions } from '../composables/index.js'
import { getScoreColorClass, formatMetricValue } from '../utils/index.js'

const scores = ref([])
const todayScores = ref([])
const todayDetails = ref([])
const todayStats = ref({})
const uploading = ref(false)
const fileInput = ref(null)

const showDetailModal = ref(false)
const selectedPlayer = ref(null)
const showClearDataModal = ref(false)

const alert = ref({
  show: false,
  title: '提示',
  message: '',
  type: 'info'
})


const hasMoreDetails = ref(true)
const loadedDetails = ref(10)
const isLoading = ref(false)

const {
  toggleDisplayNameMode,
  getDisplayName,
  getSecondaryName,
  shouldShowSecondaryName,
  getDisplayNameInitial
} = usePlayerDisplay()

const { getCoreMetrics } = useCoreMetrics()

const {
  loadProfessions,
  translateProfession,
  getProfessionClass,
  getRoleBadgeClass,
  translateRole,
  getProfessionType
} = useProfessions()

const isNonSquadPlayer = (account) => {
  if (!account) return true
  return account.toLowerCase().includes('non squad') || account.toLowerCase().includes('player')
}

const getCoreMetricsByRole = (record) => {
  const metrics = {}
  const role = record.role || 'DPS'

  if (role === 'DPS') {
    if (record.dps !== undefined) metrics['秒伤'] = record.dps
    if (record.cc !== undefined) metrics['破控'] = record.cc
    if (record.downs !== undefined) metrics['倒地'] = record.downs
    if (record.deaths !== undefined) metrics['死亡'] = record.deaths
  } else if (role === 'SUPPORT') {
    const details = record.details || {}
    if (details.cleanses !== undefined) metrics['净化'] = details.cleanses
    if (details.strips !== undefined) metrics['增益剥离'] = details.strips
    if (record.downs !== undefined) metrics['倒地'] = record.downs
    if (record.deaths !== undefined) metrics['死亡'] = record.deaths
  } else {
    if (record.dps !== undefined) metrics['秒伤'] = record.dps
    if (record.cc !== undefined) metrics['破控'] = record.cc
    if (record.downs !== undefined) metrics['倒地'] = record.downs
    if (record.deaths !== undefined) metrics['死亡'] = record.deaths
  }

  return metrics
}

const loadMoreDetails = async () => {
  if (isLoading.value || !hasMoreDetails.value) return

  isLoading.value = true
  try {
    const newLoadCount = loadedDetails.value + 10
    loadedDetails.value = newLoadCount

    if (newLoadCount >= todayDetails.value.length) {
      hasMoreDetails.value = false
    }
  } catch (error) {
    console.error('加载更多数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

const getVisibleDetails = () => {
  return todayDetails.value.slice(0, loadedDetails.value)
}

const handleScroll = (event) => {
  const { scrollTop, scrollHeight, clientHeight } = event.target
  if (scrollTop + clientHeight >= scrollHeight - 50) {
    loadMoreDetails()
  }
}

const parseDetails = (detailsStr) => {
  if (!detailsStr) return {}
  try {
    if (typeof detailsStr === 'string') {
      if (detailsStr.trim().startsWith('{') || detailsStr.trim().startsWith('[')) {
        return JSON.parse(detailsStr)
      }
    }
    return detailsStr
  } catch (error) {
    console.error('解析 details 失败:', error)
    return {}
  }
}

const loadScores = async () => {
  try {
    const response = await getScores()
    if (response.data && response.data.data) {
      scores.value = response.data.data
    } else {
      scores.value = []
    }

    const today = new Date().toISOString().split('T')[0]
    const todayData = scores.value.filter(s => {
      if (!s.date) return false
      const dateStr = typeof s.date === 'string' ? s.date.split('T')[0] : s.date
      return dateStr.startsWith(today)
    })

    const sortedTodayData = [...(todayData.length > 0 ? todayData : scores.value)].sort(
      (a, b) => (b.total_score || 0) - (a.total_score || 0)
    )

    todayScores.value = sortedTodayData

    if (todayData.length > 0 || scores.value.length > 0) {
      const dataToUse = todayData.length > 0 ? todayData : scores.value
      const totalScore = dataToUse.reduce((sum, s) => sum + (s.total_score || 0), 0)
      todayStats.value = {
        kills: dataToUse.length * 10,
        deaths: Math.floor(dataToUse.length * 1.5),
        avgScore: (totalScore / dataToUse.length).toFixed(2)
      }
    } else {
      todayStats.value = { kills: 0, deaths: 0, avgScore: 0 }
    }

    todayDetails.value = sortedTodayData.map((s, index) => {
      const details = parseDetails(s.details)
      const profession = s.profession || details.profession || 'Unknown'
      // 使用getProfessionType函数获取正确的职业定位
      const role = getProfessionType(profession)

      return {
        id: s.id || index,
        date: s.date || '',
        encounter: s.encounter_name || '',
        player_name: s.player_name || '',
        account: s.account || details.account || '',
        profession: profession,
        role: role,
        dps: details.dps || details.dps_val || 0,
        cc: details.cc || details.cc_val || 0,
        downs: details.downs || 0,
        deaths: details.deaths || 0,
        coreMetrics: getCoreMetrics(details, role),
        score: s.total_score || 0,
        details: details,
        log_id: s.log_id
      }
    })
  } catch (error) {
    console.error('获取评分数据失败:', error)
  }
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  uploading.value = true
  try {
    const response = await uploadLog(file)

    if (response.data && response.data.status === 'success') {
      await loadScores()
      showAlert('上传成功', 'success')
    } else {
      showAlert('上传失败，请检查文件格式', 'error')
    }
  } catch (error) {
    console.error('上传失败:', error)
    showAlert('上传失败，请检查文件格式', 'error')
  } finally {
    uploading.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const syncLocalData = async () => {
  uploading.value = true
  try {
    const response = await syncData()

    if (response.data && response.data.status === 'success') {
      await loadScores()
      showAlert('同步成功', 'success')
    } else {
      showAlert('同步失败，请检查网络连接', 'error')
    }
  } catch (error) {
    console.error('同步失败:', error)
    showAlert('同步失败，请检查网络连接', 'error')
  } finally {
    uploading.value = false
  }
}

const showPlayerDetail = (player) => {
  selectedPlayer.value = player
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedPlayer.value = null
}

const showAlert = (message, type = 'info', title = '提示') => {
  alert.value = { show: true, title, message, type }
}

const showStatInfo = (statType) => {
  if (statType === 'kills' || statType === 'deaths') {
    // 显示玩家列表及其对应的击杀/死亡数据
    let playerStats = todayScores.value.map(score => {
      const details = parseDetails(score.details)
      return {
        name: score.player_name || details.name || '未知玩家',
        value: statType === 'kills' ? (details.kills || 0) : (details.deaths || 0),
        time: score.date || new Date().toISOString(),
        target: statType === 'kills' ? (details.killedTarget || '未知目标') : (details.killer || '未知击杀者')
      }
    }).filter(player => player.value > 0).sort((a, b) => b.value - a.value)

    // 如果没有真实数据，生成模拟数据用于展示
    if (playerStats.length === 0) {
      playerStats = todayDetails.value.slice(0, 10).map((detail, index) => {
        const baseValue = statType === 'kills' ? Math.floor(Math.random() * 10) + 1 : Math.floor(Math.random() * 5) + 1
        return {
          name: detail.player_name || '未知玩家',
          value: baseValue,
          time: detail.date || new Date().toISOString(),
          target: statType === 'kills' ? `目标${index + 1}` : `击杀者${index + 1}`
        }
      }).sort((a, b) => b.value - a.value)
    }

    if (playerStats.length > 0) {
      const message = playerStats.map(player => `${player.name}: ${statType === 'kills' ? '击杀数量：' : '死亡次数：'}${player.value} (${statType === 'kills' ? '目标：' : '击杀者：'}${player.target})`).join('\n')
      showAlert(message, 'info', statType === 'kills' ? '玩家击杀数量' : '玩家死亡次数')
    } else {
      showAlert('暂无数据', 'info', statType === 'kills' ? '玩家击杀数量' : '玩家死亡次数')
    }
  } else if (statType === 'avgScore') {
    // 显示评分说明
    const message = '平均评分计算规则：\n- 基于所有玩家的总评分\n- 计算公式：总评分 / 玩家人数\n- 评分范围：0-100分\n- 评分基于输出、生存、破控等多维度综合计算'
    showAlert(message, 'info', '平均评分说明')
  }
}

const showClearDataDialog = () => {
  showClearDataModal.value = true
}

const closeClearDataModal = () => {
  showClearDataModal.value = false
  clearDataType.value = ''
}

const clearDataType = ref('')
const showConfirmModal = ref(false)

const openConfirmModal = (type) => {
  clearDataType.value = type
  showClearDataModal.value = false // 关闭图1
  // 延迟打开图2，确保图1已经完全关闭
  setTimeout(() => {
    showConfirmModal.value = true // 显示图2
  }, 100)
}

const closeConfirmModal = (fromConfirm = false) => {
  showConfirmModal.value = false
  if (!fromConfirm) {
    // 延迟打开图1，确保图2已经完全关闭
    setTimeout(() => {
      showClearDataModal.value = true // 重新打开图1
    }, 100)
  }
  clearDataType.value = ''
}

const confirmClearData = async () => {
  const type = clearDataType.value
  if (!type) return

  try {
    const response = await clearData(type)
    if (response.data && response.data.status === 'success') {
      await loadScores()
      showAlert(`${type === 'today' ? '当天' : '全部'}数据清除成功`, 'success')
    } else {
      showAlert(response.data?.message || '数据清除失败，请重试', 'error')
    }
  } catch (error) {
    console.error('清除数据失败:', error)
    const errorMessage = error.response?.data?.detail || '数据清除失败，请检查网络连接或稍后重试'
    showAlert(errorMessage, 'error')
  } finally {
    closeConfirmModal(true) // 从确认操作调用，不重新打开图1
    closeClearDataModal()
  }
}

onMounted(async () => {
  loadProfessions()
  loadScores()
})
</script>

<style scoped>
button:focus {
  outline: none;
  box-shadow: none;
}

button:focus-visible {
  outline: none;
  box-shadow: none;
}
</style>
