# UI设计规范文档

## 1. 概述

本文档定义了GW2-Log-Score项目的UI设计规范，包括色彩系统、字体规范、间距系统、组件设计标准等，确保项目的视觉一致性和可维护性。

### 设计原则
- **一致性**：所有UI元素遵循相同的设计规范
- **可访问性**：确保良好的对比度和交互体验
- **可复用性**：组件设计为高可复用的基础模块
- **扩展性**：设计系统支持未来的功能扩展

## 2. 色彩系统

### 主色调
```css
/* 品牌色 */
--color-primary: #6366f1; /* Indigo 500 */
--color-primary-light: #818cf8; /* Indigo 400 */
--color-primary-dark: #4f46e5; /* Indigo 600 */

/* 成功色 */
--color-success: #10b981; /* Emerald 500 */
--color-success-light: #34d399; /* Emerald 400 */
--color-success-dark: #059669; /* Emerald 600 */

/* 警告色 */
--color-warning: #f59e0b; /* Amber 500 */
--color-warning-light: #fbbf24; /* Amber 400 */
--color-warning-dark: #d97706; /* Amber 600 */

/* 错误色 */
--color-danger: #ef4444; /* Red 500 */
--color-danger-light: #f87171; /* Red 400 */
--color-danger-dark: #dc2626; /* Red 600 */
```

### 中性色
```css
/* 文本色 */
--color-text-primary: #1f2937; /* Gray 800 */
--color-text-secondary: #4b5563; /* Gray 600 */
--color-text-tertiary: #9ca3af; /* Gray 400 */
--color-text-muted: #d1d5db; /* Gray 300 */

/* 背景色 */
--color-bg-primary: #ffffff; /* White */
--color-bg-secondary: #f9fafb; /* Gray 50 */
--color-bg-tertiary: #f3f4f6; /* Gray 100 */

/* 边框色 */
--color-border-light: #e5e7eb; /* Gray 200 */
--color-border: #d1d5db; /* Gray 300 */
--color-border-dark: #9ca3af; /* Gray 400 */
```

### 职业专用色
```css
/* 守护/先驱/意志使 */
--color-profession-guardian: #fcd34d;

/* 战士/狂战/破法/刃武 */
--color-profession-warrior: #f87171;

/* 工程/机械/全息 */
--color-profession-engineer: #fb923c;

/* 游侠/德鲁伊/魂兽/不羁 */
--color-profession-ranger: #4ade80;

/* 盗贼/独行/神枪/幽影 */
--color-profession-thief: #a8a29e;

/* 元素/暴风/编织/催化 */
--color-profession-elementalist: #22d3ee;

/* 幻术/时空/幻灵/艺术 */
--color-profession-mesmer: #a78bfa;

/* 死灵/收割/灾厄/先兆 */
--color-profession-necromancer: #6b7280;

/* 魂武/裁决 */
--color-profession-revenant: #818cf8;
```

## 3. 字体规范

### 字体族
```css
--font-family-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-family-mono: 'Fira Code', 'Consolas', monospace;
```

### 字号系统
| 级别 | 字号 | 行高 | 字重 | 用途 |
|-----|------|------|------|------|
| xs | 12px | 16px | 400-500 | 辅助文本、标签 |
| sm | 14px | 20px | 400-600 | 正文、描述 |
| base | 16px | 24px | 400-600 | 主要正文 |
| lg | 18px | 28px | 500-700 | 小标题 |
| xl | 20px | 28px | 600-700 | 卡片标题 |
| 2xl | 24px | 32px | 700-900 | 页面标题 |
| 3xl | 30px | 36px | 700-900 | 大标题 |

### 字重
```css
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
--font-weight-extrabold: 800;
--font-weight-black: 900;
```

## 4. 间距系统

采用4px基础倍数的间距系统：

| 类别 | 尺寸 | 用途 |
|-----|------|------|
| xs | 4px | 紧凑元素间距 |
| sm | 8px | 小间距 |
| base | 16px | 标准间距 |
| md | 24px | 中等间距 |
| lg | 32px | 大间距 |
| xl | 48px | 超大间距 |
| 2xl | 64px | 页面级间距 |

## 5. 圆角系统

```css
--radius-none: 0;
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-2xl: 20px;
--radius-full: 9999px;
```

## 6. 阴影系统

```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
```

## 7. 组件设计规范

### 按钮组件 (BaseButton)

#### 类型
- **主要按钮 (primary)**：用于主要操作
- **次要按钮 (secondary)**：用于次要操作
- **成功按钮 (success)**：用于成功/确认操作
- **警告按钮 (warning)**：用于警告操作
- **危险按钮 (danger)**：用于危险/删除操作
- **幽灵按钮 (ghost)**：用于透明背景按钮

#### 尺寸
- **xs**：超小按钮，用于紧凑区域
- **sm**：小按钮，用于次要操作
- **md**：中等按钮，默认尺寸
- **lg**：大按钮，用于主要CTA

#### 状态
- 默认
- Hover
- Active
- Disabled
- Loading

#### 示例
```vue
<BaseButton type="primary" size="md" @click="handleClick">
  点击我
</BaseButton>
```

### 弹框组件 (BaseModal)

#### 类型
- **信息弹框 (info)**：展示信息
- **确认弹框 (confirm)**：需要用户确认
- **成功弹框 (success)**：展示成功状态
- **警告弹框 (warning)**：展示警告信息
- **错误弹框 (error)**：展示错误信息

#### 尺寸
- **sm**：小弹框
- **md**：中等弹框，默认
- **lg**：大弹框
- **xl**：超大弹框
- **fullscreen**：全屏弹框

#### 特性
- 可自定义标题
- 可自定义底部按钮
- 支持ESC关闭
- 支持点击遮罩关闭
- 支持键盘导航

### 表格组件 (BaseTable)

#### 特性
- 响应式设计
- 支持固定表头
- 支持排序
- 支持分页
- 支持选择行
- 支持加载状态
- 支持空状态
- 斑马纹可选

#### 列配置
```javascript
const columns = [
  { key: 'name', label: '名称', width: 200, sortable: true },
  { key: 'score', label: '评分', width: 100, align: 'right' },
  { key: 'actions', label: '操作', width: 150, slot: true }
]
```

### 卡片组件 (BaseCard)

#### 特性
- 可选头部
- 可选底部
- 可选阴影
- 可选边框
- 支持紧凑模式

### 布局组件

#### PageLayout
- 页面主布局
- 包含导航栏
- 包含内容区域

#### CardGrid
- 卡片网格布局
- 响应式网格
- 支持不同列数

## 8. 响应式断点

```css
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
--breakpoint-2xl: 1536px;
```

## 9. 动画规范

### 过渡时长
```css
--duration-fast: 150ms;
--duration-normal: 200ms;
--duration-slow: 300ms;
```

### 缓动函数
```css
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

## 10. 可访问性

### 对比度
- 文本与背景对比度 ≥ 4.5:1 (AA标准)
- 大文本对比度 ≥ 3:1

### 键盘导航
- 所有交互元素可通过Tab访问
- 有清晰的焦点状态
- 支持Enter和Space触发

### ARIA标签
- 为非文本按钮提供aria-label
- 为弹框提供role="dialog"
- 为模态提供aria-modal="true"

## 11. Tailwind CSS类名约定

### 布局类
- 使用flexbox进行布局
- 使用grid进行网格布局
- 避免硬编码宽度和高度

### 颜色类
- 使用语义化的颜色类：text-primary、bg-success等
- 避免使用具体的颜色值

### 间距类
- 使用标准化的间距类：p-4、gap-4、mt-2等

### 状态类
- hover:、focus:、active:、disabled:

## 12. 组件使用流程

1. **导入组件**
```javascript
import { BaseButton, BaseModal, BaseTable, BaseCard } from '@/components/base'
```

2. **使用组件**
```vue
<template>
  <BaseCard>
    <BaseTable :columns="columns" :data="data" />
    <BaseButton type="primary" @click="openModal">添加</BaseButton>
  </BaseCard>
</template>
```

## 13. 文件结构

```
src/
├── components/
│   └── base/               # 基础组件库
│       ├── BaseButton.vue
│       ├── BaseModal.vue
│       ├── BaseTable.vue
│       ├── BaseCard.vue
│       ├── BaseInput.vue
│       └── index.js        # 统一导出
├── assets/
│   ├── styles/
│   │   ├── base/           # 基础样式
│   │   ├── components/     # 组件样式
│   │   └── utilities/      # 工具样式
│   └── images/             # 图片资源
└── views/                  # 页面组件
```

## 14. 更新日志

- v1.0.0 (2026-04-23)
  - 初始版本
  - 建立色彩系统
  - 建立字体规范
  - 建立组件设计标准
