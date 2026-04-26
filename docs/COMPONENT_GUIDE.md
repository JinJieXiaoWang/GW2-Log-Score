# 组件库使用指南

本指南介绍如何使用项目中的基础组件库。

## 目录

- [快速开始](#快速开始)
- [BaseButton 按钮组件](#basebutton-按钮组件)
- [BaseCard 卡片组件](#basecard-卡片组件)
- [BaseModal 弹框组件](#basemodal-弹框组件)
- [BaseTable 表格组件](#basetable-表格组件)

---

## 快速开始

### 1. 导入组件

```javascript
import { 
  BaseButton, 
  BaseCard, 
  BaseModal, 
  BaseTable 
} from '@/components/base'
```

### 2. 在模板中使用

```vue
<template>
  <BaseCard>
    <BaseButton variant="primary" @click="openModal">
      点击打开弹框
    </BaseButton>
    
    <BaseModal v-model:show="showModal" title="示例弹框">
      <p>这是弹框内容</p>
    </BaseModal>
  </BaseCard>
</template>
```

---

## BaseButton 按钮组件

用于触发用户操作的按钮组件。

### Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| type | 原生 button 类型 | string | button/submit/reset | button |
| variant | 按钮类型 | string | primary/secondary/success/warning/danger/ghost | primary |
| size | 按钮尺寸 | string | xs/sm/md/lg | md |
| disabled | 是否禁用 | boolean | — | false |
| loading | 是否加载中 | boolean | — | false |
| block | 是否块级按钮 | boolean | — | false |
| icon | 图标组件 | string/Object | — | null |

### Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| click | 点击按钮时触发 | event |

### 使用示例

```vue
<template>
  <div class="space-y-4">
    <!-- 不同类型 -->
    <BaseButton variant="primary">主要按钮</BaseButton>
    <BaseButton variant="secondary">次要按钮</BaseButton>
    <BaseButton variant="success">成功按钮</BaseButton>
    <BaseButton variant="warning">警告按钮</BaseButton>
    <BaseButton variant="danger">危险按钮</BaseButton>
    <BaseButton variant="ghost">幽灵按钮</BaseButton>

    <!-- 不同尺寸 -->
    <BaseButton variant="primary" size="xs">超小</BaseButton>
    <BaseButton variant="primary" size="sm">小</BaseButton>
    <BaseButton variant="primary" size="md">中</BaseButton>
    <BaseButton variant="primary" size="lg">大</BaseButton>

    <!-- 状态 -->
    <BaseButton variant="primary" loading>加载中</BaseButton>
    <BaseButton variant="primary" disabled>禁用</BaseButton>

    <!-- 块级按钮 -->
    <BaseButton variant="primary" block>块级按钮</BaseButton>

    <!-- 带点击事件 -->
    <BaseButton variant="primary" @click="handleClick">
      点击我
    </BaseButton>
  </div>
</template>

<script setup>
const handleClick = () => {
  console.log('按钮被点击了')
}
</script>
```

---

## BaseCard 卡片组件

用于包裹内容的卡片容器组件。

### Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| shadow | 阴影大小 | string | default/lg/none | default |
| borderless | 是否无边框 | boolean | — | false |
| compact | 是否紧凑模式 | boolean | — | false |

### Slots

| 插槽名 | 说明 |
|--------|------|
| default | 卡片主体内容 |
| header | 卡片头部内容 |
| footer | 卡片底部内容 |

### 使用示例

```vue
<template>
  <div class="space-y-6">
    <!-- 基础卡片 -->
    <BaseCard>
      <template #header>
        <h3 class="font-semibold">卡片标题</h3>
      </template>
      <p>这是卡片的主要内容</p>
      <template #footer>
        <span class="text-sm text-gray-500">卡片底部</span>
      </template>
    </BaseCard>

    <!-- 大阴影卡片 -->
    <BaseCard shadow="lg">
      <p>这是大阴影的卡片</p>
    </BaseCard>

    <!-- 紧凑模式 -->
    <BaseCard compact>
      <p>这是紧凑模式的卡片</p>
    </BaseCard>
  </div>
</template>
```

---

## BaseModal 弹框组件

模态对话框组件，用于需要用户确认或展示信息的场景。

### Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| show | 是否显示弹框 | boolean | — | false |
| title | 弹框标题 | string | — | '' |
| size | 弹框尺寸 | string | sm/md/lg/xl/fullscreen | md |
| closeOnEsc | 是否按 ESC 关闭 | boolean | — | true |
| closeOnBackdrop | 是否点击遮罩关闭 | boolean | — | true |
| showClose | 是否显示关闭按钮 | boolean | — | true |
| closeLabel | 关闭按钮的 aria-label | string | — | '关闭' |

### Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| update:show | 显示状态改变时触发 | (show: boolean) |
| close | 关闭弹框时触发 | — |

### Slots

| 插槽名 | 说明 |
|--------|------|
| default | 弹框主体内容 |
| header | 弹框头部（会覆盖 title） |
| footer | 弹框底部 |

### 使用示例

```vue
<template>
  <div>
    <BaseButton variant="primary" @click="showModal = true">
      打开弹框
    </BaseButton>

    <!-- 基础弹框 -->
    <BaseModal 
      v-model:show="showModal" 
      title="确认操作"
    >
      <p>确定要执行此操作吗？</p>
      <template #footer>
        <BaseButton variant="secondary" @click="showModal = false">
          取消
        </BaseButton>
        <BaseButton variant="primary" @click="confirm">
          确认
        </BaseButton>
      </template>
    </BaseModal>

    <!-- 小弹框 -->
    <BaseModal 
      v-model:show="showSmallModal" 
      size="sm"
      title="提示"
    >
      <p>这是一个小弹框</p>
    </BaseModal>

    <!-- 大弹框 -->
    <BaseModal 
      v-model:show="showLargeModal" 
      size="lg"
      title="详情"
    >
      <div class="space-y-4">
        <p>这里可以展示更多内容</p>
        <p>适合展示表单或详细信息</p>
      </div>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const showModal = ref(false)
const showSmallModal = ref(false)
const showLargeModal = ref(false)

const confirm = () => {
  console.log('确认操作')
  showModal.value = false
}
</script>
```

---

## BaseTable 表格组件

用于展示表格数据的组件，支持排序、自定义列等功能。

### Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| columns | 列配置 | Array | — | [] |
| data | 表格数据 | Array | — | [] |
| loading | 是否加载中 | boolean | — | false |
| striped | 是否斑马纹 | boolean | — | false |
| rowKey | 行数据的 key | string/Function | — | 'id' |
| sortKey | 当前排序列 | string | — | null |
| sortOrder | 排序方向 | string | asc/desc | 'asc' |
| emptyText | 空数据文本 | string | — | '暂无数据' |

### Column 配置

| 属性 | 说明 | 类型 |
|------|------|------|
| key | 列数据的 key | string |
| label | 列标题 | string |
| width | 列宽度（像素） | number |
| minWidth | 最小宽度（像素） | number |
| align | 对齐方式 | 'left'/'center'/'right' |
| sortable | 是否可排序 | boolean |
| slot | 自定义列的插槽名 | string |
| formatter | 自定义格式化函数 | Function |

### Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| sort | 排序时触发 | { key: string, order: 'asc'/'desc' } |
| row-click | 点击行时触发 | { row: any, index: number } |

### Slots

| 插槽名 | 说明 | 作用域 |
|--------|------|--------|
| [column.slot] | 自定义列内容 | { row, rowIndex, column } |
| empty | 空状态内容 | — |

### 使用示例

```vue
<template>
  <div>
    <BaseTable
      :columns="columns"
      :data="tableData"
      :striped="true"
      @sort="handleSort"
      @row-click="handleRowClick"
    >
      <!-- 自定义操作列 -->
      <template #actions="{ row }">
        <div class="flex gap-2">
          <BaseButton variant="ghost" size="xs" @click="viewDetail(row)">
            查看
          </BaseButton>
          <BaseButton variant="ghost" size="xs" @click="editRow(row)">
            编辑
          </BaseButton>
        </div>
      </template>

      <!-- 自定义空状态 -->
      <template #empty>
        <div class="text-center py-8">
          <p class="text-gray-400">暂无数据</p>
        </div>
      </template>
    </BaseTable>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const columns = ref([
  { key: 'name', label: '姓名', width: 150, sortable: true },
  { key: 'age', label: '年龄', width: 100, align: 'center' },
  { key: 'score', label: '评分', width: 120, align: 'right', sortable: true },
  { 
    key: 'status', 
    label: '状态', 
    width: 100,
    formatter: (value) => value ? '已激活' : '未激活'
  },
  { key: 'actions', label: '操作', width: 150, slot: 'actions' }
])

const tableData = ref([
  { id: 1, name: '张三', age: 25, score: 92, status: true },
  { id: 2, name: '李四', age: 30, score: 88, status: true },
  { id: 3, name: '王五', age: 28, score: 95, status: false }
])

const handleSort = (sortInfo) => {
  console.log('排序:', sortInfo)
}

const handleRowClick = (rowInfo) => {
  console.log('点击行:', rowInfo)
}

const viewDetail = (row) => {
  console.log('查看详情:', row)
}

const editRow = (row) => {
  console.log('编辑:', row)
}
</script>
```

---

## 最佳实践

### 1. 组件命名

- 业务组件使用语义化名称，如 `PlayerDetail`、`ScoreTable`
- 基础组件统一使用 `Base` 前缀，如 `BaseButton`、`BaseCard`

### 2. Props 设计

- 为组件提供合理的默认值
- 使用类型校验保证数据安全
- 复杂配置使用对象或数组

### 3. 插槽使用

- 优先使用具名插槽提升可读性
- 为插槽提供必要的作用域数据

### 4. 事件处理

- 事件名使用 kebab-case，如 `row-click`
- 提供完整的事件回调参数

### 5. 样式管理

- 组件内部使用 scoped 样式
- 公共样式抽取到 `assets/styles` 目录
- 优先使用 Tailwind CSS 工具类
