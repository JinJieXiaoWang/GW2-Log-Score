<template>
  <div class="example-usage space-y-8 max-w-6xl mx-auto p-8">
    <h1 class="text-3xl font-bold text-gray-800">
      基础组件使用示例
    </h1>

    <!-- 按钮示例 -->
    <section class="space-y-4">
      <h2 class="text-xl font-semibold text-gray-700">
        按钮组件
      </h2>
      <BaseCard>
        <div class="space-y-4">
          <div class="flex flex-wrap gap-3">
            <BaseButton
              variant="primary"
              @click="handleClick"
            >
              主要按钮
            </BaseButton>
            <BaseButton variant="secondary">
              次要按钮
            </BaseButton>
            <BaseButton variant="success">
              成功按钮
            </BaseButton>
            <BaseButton variant="warning">
              警告按钮
            </BaseButton>
            <BaseButton variant="danger">
              危险按钮
            </BaseButton>
            <BaseButton variant="ghost">
              幽灵按钮
            </BaseButton>
          </div>

          <div class="flex flex-wrap gap-3">
            <BaseButton
              variant="primary"
              size="xs"
            >
              超小
            </BaseButton>
            <BaseButton
              variant="primary"
              size="sm"
            >
              小
            </BaseButton>
            <BaseButton
              variant="primary"
              size="md"
            >
              中（默认）
            </BaseButton>
            <BaseButton
              variant="primary"
              size="lg"
            >
              大
            </BaseButton>
          </div>

          <div class="flex flex-wrap gap-3">
            <BaseButton
              variant="primary"
              loading
            >
              加载中
            </BaseButton>
            <BaseButton
              variant="primary"
              disabled
            >
              禁用
            </BaseButton>
          </div>

          <div class="max-w-xs">
            <BaseButton
              variant="primary"
              block
            >
              块级按钮
            </BaseButton>
          </div>
        </div>
      </BaseCard>
    </section>

    <!-- 卡片示例 -->
    <section class="space-y-4">
      <h2 class="text-xl font-semibold text-gray-700">
        卡片组件
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <BaseCard>
          <template #header>
            <h3 class="font-semibold">
              默认卡片
            </h3>
          </template>
          <p>这是卡片的主要内容区域。</p>
          <template #footer>
            <span class="text-sm text-gray-500">卡片底部</span>
          </template>
        </BaseCard>

        <BaseCard shadow="lg">
          <h3 class="font-semibold mb-2">
            大阴影卡片
          </h3>
          <p>没有 header 和 footer 的卡片。</p>
        </BaseCard>

        <BaseCard compact>
          <template #header>
            <h3 class="font-semibold text-sm">
              紧凑模式
            </h3>
          </template>
          <p class="text-sm">
            内容区域更小的卡片。
          </p>
        </BaseCard>
      </div>
    </section>

    <!-- 弹框示例 -->
    <section class="space-y-4">
      <h2 class="text-xl font-semibold text-gray-700">
        弹框组件
      </h2>
      <BaseCard>
        <div class="flex flex-wrap gap-3">
          <BaseButton
            variant="primary"
            @click="showModal = true"
          >
            打开弹框
          </BaseButton>
          <BaseButton
            variant="secondary"
            @click="showSmallModal = true"
          >
            小弹框
          </BaseButton>
          <BaseButton
            variant="ghost"
            @click="showLargeModal = true"
          >
            大弹框
          </BaseButton>
        </div>
      </BaseCard>

      <BaseModal
        v-model:show="showModal"
        title="默认弹框"
      >
        <p class="text-gray-600">
          这是一个默认尺寸的弹框示例。
        </p>
        <template #footer>
          <BaseButton
            variant="secondary"
            @click="showModal = false"
          >
            取消
          </BaseButton>
          <BaseButton
            variant="primary"
            @click="showModal = false"
          >
            确认
          </BaseButton>
        </template>
      </BaseModal>

      <BaseModal
        v-model:show="showSmallModal"
        size="sm"
        title="小弹框"
      >
        <p class="text-gray-600">
          这是一个小尺寸的弹框。
        </p>
        <template #footer>
          <BaseButton
            variant="primary"
            @click="showSmallModal = false"
          >
            确定
          </BaseButton>
        </template>
      </BaseModal>

      <BaseModal
        v-model:show="showLargeModal"
        size="lg"
        title="大弹框"
      >
        <div class="space-y-4">
          <p class="text-gray-600">
            这是一个大尺寸的弹框，可以显示更多内容。
          </p>
          <div class="grid grid-cols-2 gap-4">
            <div class="p-4 bg-gray-50 rounded-lg">
              <h4 class="font-semibold mb-2">
                内容区块 1
              </h4>
              <p class="text-sm text-gray-500">
                这里可以放置更多内容。
              </p>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
              <h4 class="font-semibold mb-2">
                内容区块 2
              </h4>
              <p class="text-sm text-gray-500">
                这里也可以放置更多内容。
              </p>
            </div>
          </div>
        </div>
        <template #footer>
          <BaseButton
            variant="secondary"
            @click="showLargeModal = false"
          >
            关闭
          </BaseButton>
        </template>
      </BaseModal>
    </section>

    <!-- 表格示例 -->
    <section class="space-y-4">
      <h2 class="text-xl font-semibold text-gray-700">
        表格组件
      </h2>
      <BaseCard>
        <BaseTable
          :columns="tableColumns"
          :data="tableData"
          :striped="true"
          @sort="handleSort"
          @row-click="handleRowClick"
        >
          <template #actions>
            <div class="flex gap-2">
              <BaseButton
                variant="ghost"
                size="xs"
              >
                查看
              </BaseButton>
              <BaseButton
                variant="ghost"
                size="xs"
              >
                编辑
              </BaseButton>
            </div>
          </template>
          <template #empty>
            <div class="text-center py-8">
              <p class="text-gray-400">
                暂无数据，请稍后再试
              </p>
            </div>
          </template>
        </BaseTable>
      </BaseCard>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { BaseButton, BaseCard, BaseModal, BaseTable } from './base'

const showModal = ref(false)
const showSmallModal = ref(false)
const showLargeModal = ref(false)

const tableColumns = ref([
  { key: 'name', label: '姓名', width: 150, sortable: true },
  { key: 'profession', label: '职业', width: 120 },
  { key: 'role', label: '定位', width: 100, align: 'center' },
  { key: 'score', label: '评分', width: 100, align: 'right', sortable: true },
  { key: 'actions', label: '操作', width: 150, slot: 'actions' }
])

const tableData = ref([
  { id: 1, name: '张三', profession: '守护者', role: '治疗', score: 92.5 },
  { id: 2, name: '李四', profession: '战士', role: '坦克', score: 88.0 },
  { id: 3, name: '王五', profession: '元素使', role: 'DPS', score: 95.3 },
  { id: 4, name: '赵六', profession: '幻术师', role: '辅助', score: 89.7 },
  { id: 5, name: '钱七', profession: '潜行者', role: 'DPS', score: 91.2 }
])

const handleClick = () => {
  console.log('按钮被点击了')
}

const handleSort = (sortInfo) => {
  console.log('排序:', sortInfo)
}

const handleRowClick = (rowInfo) => {
  console.log('点击行:', rowInfo)
}
</script>

<style scoped>
.example-usage {
  background-color: #f9fafb;
  min-height: 100vh;
}
</style>
