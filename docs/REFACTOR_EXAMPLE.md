# 样式重构示例

本文档展示如何使用新创建的 utilities 样式类重构 ScoreTable.vue

## 📝 重构前

```vue
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
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="score in scores"
            :key="score.id"
            class="hover:bg-gray-50/50 transition-colors cursor-pointer"
          >
            <td class="px-8 py-5">
              <div class="flex items-center gap-3">
                <div
                  class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-sm font-black text-gray-400 border border-gray-200"
                >
                  {{ getDisplayNameInitial(score) }}
                </div>
                <!-- 其他内容 -->
              </div>
            </td>
            <td class="px-8 py-5">
              <span
                class="text-xs px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter"
              >
                {{ translateProfession(score.profession) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
```

## ✅ 重构后

```vue
<template>
  <div class="card-container">
    <div class="card-header">
      <h2 class="card-title">
        评分列表
      </h2>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="table-header-cell">
              玩家
            </th>
            <th class="table-header-cell">
              职业
            </th>
          </tr>
        </thead>
        <tbody class="table-divider">
          <tr
            v-for="score in scores"
            :key="score.id"
            class="table-row"
          >
            <td class="table-cell">
              <div class="flex items-center gap-3">
                <div class="avatar">
                  {{ getDisplayNameInitial(score) }}
                </div>
                <!-- 其他内容 -->
              </div>
            </td>
            <td class="table-cell">
              <span class="badge-compact">
                {{ translateProfession(score.profession) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
```

## 📊 改进对比

| 指标 | 重构前 | 重构后 |
|-----|-------|
| 总类名数 | 15+ | 8 |
| 可维护性 | 低 - 修改需改多处 | 高 - 改一处全局生效 |
| 一致性 | 依赖开发者记忆 | 统一规范 |
| 可扩展性 | 每次手动复制 | 语义化复用 |

## 📝 关键变化

### 1. 卡片容器
```html
<!-- 之前 -->
<div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">

<!-- 之后 -->
<div class="card-container">
```

### 2. 表头单元格
```html
<!-- 之前 -->
<th class="px-8 py-4 text-xs font-bold text-gray-400 uppercase tracking-widest">

<!-- 之后 -->
<th class="table-header-cell">
```

### 3. 头像
```html
<!-- 之前 -->
<div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-sm font-black text-gray-400 border border-gray-200">

<!-- 之后 -->
<div class="avatar">
```

### 4. 徽章
```html
<!-- 之前 -->
<span class="text-xs px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter">

<!-- 之后 -->
<span class="badge-compact">
```

## 🚀 下一步

按照同样的方式，可以重构：

1. PlayerDetail.vue
2. Dashboard.vue
3. History.vue
4. AISuggestions.vue

所有这些文件都有类似的重复样式可以提取。
