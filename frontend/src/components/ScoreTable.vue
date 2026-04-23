<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="p-6 border-b border-gray-100">
      <h2 class="text-sm font-bold text-gray-400 uppercase tracking-widest">
        评分列表
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
              总分
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="score in scores"
            :key="score.id"
            class="hover:bg-gray-50/50 transition-colors cursor-pointer"
            @click="selectPlayer(score)"
          >
            <td class="px-8 py-5">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-sm font-black text-gray-400 border border-gray-200">
                  {{ getDisplayNameInitial(score) }}
                </div>
                <div>
                  <button
                    class="text-sm font-black text-gray-800 hover:text-indigo-600 transition-colors text-left"
                    @click.stop="toggleDisplayNameMode(score)"
                  >
                    {{ getDisplayName(score) }}
                  </button>
                  <p
                    v-if="shouldShowSecondaryName(score)"
                    class="text-xs text-gray-400"
                  >
                    {{ getSecondaryName(score) }}
                  </p>
                </div>
              </div>
            </td>
            <td class="px-8 py-5">
              <span
                :class="getProfessionClass(translateProfession(score.profession))"
                class="text-xs px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter"
              >
                {{ translateProfession(score.profession) }}
              </span>
            </td>
            <td class="px-8 py-5">
              <div class="flex flex-col items-end">
                <p
                  :class="getScoreColorClass(score.total_score)"
                  class="text-2xl font-black"
                >
                  {{ score.total_score.toFixed(2) }}
                </p>
                <div class="w-full bg-gray-100 rounded-full h-1.5 mt-2">
                  <div
                    :class="getScoreBarColorClass(score.total_score)"
                    class="h-1.5 rounded-full transition-all duration-500 ease-out"
                    :style="{ width: score.total_score + '%' }"
                  />
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { usePlayerDisplay, useProfessions } from '../composables/index.js'
import { getScoreColorClass, getScoreBarColorClass } from '../utils/index.js'

defineProps({
  scores: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['select-player'])

// 使用组合式函数管理玩家显示
const {
  toggleDisplayNameMode,
  getDisplayName,
  getSecondaryName,
  shouldShowSecondaryName,
  getDisplayNameInitial
} = usePlayerDisplay()

const {
  translateProfession,
  getProfessionClass
} = useProfessions()

const selectPlayer = (score) => {
  emit('select-player', score)
}
</script>

<style scoped>
/* 组件样式 */
</style>
