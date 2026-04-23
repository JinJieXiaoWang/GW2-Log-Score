<template>
  <div :class="{ 'base-table--loading': loading }">
    <div
      v-if="loading"
      class="base-table__loading-overlay"
    >
      <span class="sr-only">加载中...</span>
    </div>
    <table class="base-table">
      <thead class="base-table__header">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            :class="headerCellClasses(column)"
            :style="headerCellStyle(column)"
            @click="handleSort(column)"
          >
            <div class="flex items-center justify-between">
              <span>{{ column.label }}</span>
              <span
                v-if="column.sortable"
                class="base-table__sort-icon"
              >
                <SortIcon v-if="sortKey === column.key && sortOrder === 'asc'" />
                <SortDescIcon v-else-if="sortKey === column.key && sortOrder === 'desc'" />
                <SortIcon
                  v-else
                  style="opacity: 0.3"
                />
              </span>
            </div>
          </th>
        </tr>
      </thead>
      <tbody v-if="!loading && data.length > 0">
        <tr
          v-for="(row, rowIndex) in data"
          :key="typeof props.rowKey === 'function' ? props.rowKey(row, rowIndex) : (row[props.rowKey] ?? rowIndex)"
          :class="rowClasses()"
          @click="handleRowClick(row, rowIndex)"
        >
          <td
            v-for="column in columns"
            :key="column.key"
            :class="bodyCellClasses(column)"
            :style="bodyCellStyle(column)"
          >
            <slot
              v-if="column.slot"
              :name="column.slot"
              :row="row"
              :row-index="rowIndex"
              :column="column"
            />
            <template v-else>
              {{ renderCellValue(row, column) }}
            </template>
          </td>
        </tr>
      </tbody>
    </table>
    <div
      v-if="!loading && data.length === 0"
      class="base-table__empty"
    >
      <slot name="empty">
        {{ emptyText }}
      </slot>
    </div>
  </div>
</template>

<script setup>
import { SortIcon, SortDescIcon } from './icons'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
    default: () => []
  },
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  striped: {
    type: Boolean,
    default: false
  },
  rowKey: {
    type: [String, Function],
    default: 'id'
  },
  sortKey: {
    type: String,
    default: null
  },
  sortOrder: {
    type: String,
    default: 'asc',
    validator: (value) => ['asc', 'desc'].includes(value)
  },
  emptyText: {
    type: String,
    default: '暂无数据'
  }
})

const emit = defineEmits(['sort', 'row-click'])

const headerCellClasses = (column) => [
  'base-table__header-cell',
  {
    'base-table__header-cell--sortable': column.sortable
  }
]

const headerCellStyle = (column) => ({
  width: column.width ? `${column.width}px` : undefined,
  minWidth: column.minWidth ? `${column.minWidth}px` : undefined
})

const bodyCellClasses = (column) => [
  'base-table__body-cell',
  {
    'base-table__body-cell--align-center': column.align === 'center',
    'base-table__body-cell--align-right': column.align === 'right'
  }
]

const bodyCellStyle = (column) => ({
  width: column.width ? `${column.width}px` : undefined,
  minWidth: column.minWidth ? `${column.minWidth}px` : undefined
})

const rowClasses = () => [
  'base-table__body-row',
  {
    'base-table__body-row--striped': props.striped
  }
]

const renderCellValue = (row, column) => {
  const value = row[column.key]
  if (column.formatter) {
    return column.formatter(value, row, column)
  }
  return value
}

const handleSort = (column) => {
  if (column.sortable) {
    emit('sort', {
      key: column.key,
      order: props.sortKey === column.key && props.sortOrder === 'asc' ? 'desc' : 'asc'
    })
  }
}

const handleRowClick = (row, index) => {
  emit('row-click', { row, index })
}
</script>

<style scoped>
.base-table__header-cell {
  cursor: default;
}
</style>
