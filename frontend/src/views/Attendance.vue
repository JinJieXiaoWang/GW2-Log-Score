<template>
  <div class="space-y-8">
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-6 border-b border-gray-100">
        <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
          出勤统计
        </h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">
                玩家
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">
                职业
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">
                定位
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">
                出勤次数
              </th>
              <th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">
                最近出勤
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr
              v-for="player in attendanceData"
              :key="player.name"
              class="hover:bg-gray-50/50 transition-colors"
            >
              <td class="px-8 py-5">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-sm font-black text-gray-400 border border-gray-200">
                    {{ getDisplayNameInitial(player) }}
                  </div>
                  <div>
                    <button
                      class="text-sm font-black text-gray-800 hover:text-indigo-600 transition-colors text-left"
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
              </td>
              <td class="px-8 py-5">
                <span
                  :class="getProfessionClass(translateProfession(player.profession))"
                  class="text-xs px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter"
                >
                  {{ translateProfession(player.profession) }}
                </span>
              </td>
              <td class="px-8 py-5">
                <span
                  :class="getRoleBadgeClass(player.role)"
                  class="text-xs px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter"
                >
                  {{ player.role }}
                </span>
              </td>
              <td class="px-8 py-5">
                <button
                  class="text-sm font-bold text-gray-700 cursor-pointer hover:text-indigo-600"
                  @click="showAttendanceDetail(player.name)"
                >
                  {{ player.attendance_count }}
                </button>
              </td>
              <td class="px-8 py-5">
                <p class="text-sm text-gray-500">
                  {{ formatDate(player.last_attendance) }}
                </p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div
        v-if="attendanceData.length === 0"
        class="text-center py-10 text-gray-400"
      >
        暂无出勤数据
      </div>
    </div>

    <div
      v-if="showDetailModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeDetailModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-8">
          <div class="flex justify-between items-start mb-8">
            <h2 class="text-xl font-black text-gray-800">
              出勤详情
            </h2>
            <button
              class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition-colors"
              @click="closeDetailModal"
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

          <div
            v-if="isLoading"
            class="text-center py-10 text-gray-400"
          >
            加载中...
          </div>

          <div v-else>
            <div class="bg-gray-50 rounded-2xl p-6 mb-8">
              <h3 class="text-sm font-bold text-gray-700 uppercase tracking-widest mb-4">
                玩家信息
              </h3>
              <div class="flex flex-wrap gap-4">
                <div>
                  <p class="text-xs text-gray-500">
                    玩家名称
                  </p>
                  <p class="text-sm font-bold text-gray-800">
                    {{ attendanceDetail.player_info.name || 'N/A' }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-gray-500">
                    账号
                  </p>
                  <p class="text-sm font-bold text-gray-800">
                    {{ attendanceDetail.player_info.account || 'N/A' }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-gray-500">
                    职业
                  </p>
                  <p class="text-sm font-bold text-gray-800">
                    {{ attendanceDetail.player_info.profession || 'N/A' }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-gray-500">
                    定位
                  </p>
                  <p class="text-sm font-bold text-gray-800">
                    {{ attendanceDetail.player_info.role || 'N/A' }}
                  </p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-2xl border border-gray-100 p-6 mb-8">
              <h3 class="text-sm font-bold text-gray-700 uppercase tracking-widest mb-4">
                使用过的角色
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  v-for="role in attendanceDetail.roles"
                  :key="role.name"
                  class="flex items-center gap-3 p-3 rounded-lg bg-gray-50"
                >
                  <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-sm font-black text-gray-400 border border-gray-200">
                    {{ role.name[0] }}
                  </div>
                  <div>
                    <p class="text-sm font-bold text-gray-800">
                      {{ role.name }}
                    </p>
                    <div class="flex items-center gap-2 mt-1">
                      <span
                        :class="getProfessionClass(translateProfession(role.profession))"
                        class="text-xs px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter"
                      >
                        {{ translateProfession(role.profession) }}
                      </span>
                      <span
                        :class="getRoleBadgeClass(role.role)"
                        class="text-xs px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter"
                      >
                        {{ role.role }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-2xl border border-gray-100 p-6 mb-8">
              <h3 class="text-sm font-bold text-gray-700 uppercase tracking-widest mb-4">
                出勤日期记录
              </h3>
              <div class="space-y-3">
                <div
                  v-for="date in attendanceDetail.attendance_dates"
                  :key="date.log_id"
                  class="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <div>
                    <p class="text-sm font-bold text-gray-800">
                      {{ date.encounter_name }}
                    </p>
                    <p class="text-xs text-gray-500">
                      {{ formatDate(date.date) }} · {{ date.mode }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-2xl border border-gray-100 p-6">
              <h3 class="text-sm font-bold text-gray-700 uppercase tracking-widest mb-4">
                打团数据详情
              </h3>
              <div class="overflow-x-auto">
                <table class="w-full">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                        日期
                      </th>
                      <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                        副本
                      </th>
                      <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                        模式
                      </th>
                      <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                        总分
                      </th>
                      <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                        输出
                      </th>
                      <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                        破控
                      </th>
                      <th class="px-4 py-3 text-xs font-bold text-gray-400 uppercase tracking-widest">
                        生存
                      </th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-50">
                    <tr
                      v-for="detail in attendanceDetail.attendance_details"
                      :key="detail.id"
                      class="hover:bg-gray-50/50 transition-colors"
                    >
                      <td class="px-4 py-3 text-sm text-gray-500">
                        {{ formatDate(detail.date) }}
                      </td>
                      <td class="px-4 py-3 text-sm text-gray-700">
                        {{ detail.encounter_name }}
                      </td>
                      <td class="px-4 py-3">
                        <span
                          :class="getModeBadgeClass(detail.mode)"
                          class="text-xs px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter"
                        >
                          {{ detail.mode }}
                        </span>
                      </td>
                      <td class="px-4 py-3 text-sm font-bold text-gray-800">
                        {{ detail.total_score.toFixed(2) }}
                      </td>
                      <td class="px-4 py-3 text-sm text-gray-700">
                        {{ detail.dps.toFixed(2) }}
                      </td>
                      <td class="px-4 py-3 text-sm text-gray-700">
                        {{ detail.cc.toFixed(2) }}
                      </td>
                      <td class="px-4 py-3 text-sm text-gray-700">
                        {{ detail.survival.toFixed(2) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAttendance } from '../utils/api'
import { usePlayerDisplay, useProfessions } from '../composables/index.js'
import { formatDate } from '../utils/index.js'

const attendanceData = ref([])
const showDetailModal = ref(false)
const isLoading = ref(false)
const attendanceDetail = ref({
  player_info: {},
  roles: [],
  attendance_dates: [],
  attendance_details: []
})

const {
  toggleDisplayNameMode,
  getDisplayName,
  getSecondaryName,
  shouldShowSecondaryName,
  getDisplayNameInitial
} = usePlayerDisplay()

const {
  loadProfessions,
  translateProfession,
  getProfessionClass,
  getRoleBadgeClass
} = useProfessions()

const getModeBadgeClass = (mode) => {
  if (mode && mode.includes('WvW')) return 'bg-indigo-50 text-indigo-600'
  if (mode && mode.includes('PVE')) return 'bg-green-50 text-green-600'
  return 'bg-gray-50 text-gray-600'
}

const loadAttendanceData = async () => {
  try {
    const response = await getAttendance()
    attendanceData.value = response.data
  } catch (error) {
    console.error('获取出勤数据失败:', error)
  }
}

const showAttendanceDetail = async (playerName) => {
  isLoading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/attendance/${encodeURIComponent(playerName)}`)
    const data = await response.json()
    attendanceDetail.value = data
    showDetailModal.value = true
  } catch (error) {
    console.error('获取出勤详情失败:', error)
  } finally {
    isLoading.value = false
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  attendanceDetail.value = {
    player_info: {},
    roles: [],
    attendance_dates: [],
    attendance_details: []
  }
}

onMounted(async () => {
  loadProfessions()
  loadAttendanceData()
})
</script>

<style scoped>
</style>
