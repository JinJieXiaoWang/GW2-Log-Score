# Design Tokens

本项目的设计系统令牌定义，确保所有组件样式一致。

## 🎨 间距 (Spacing)

| Token | 值 | 应用场景 |
|------|-----|---------|
| `--spacing-xs` | `0.25rem` (4px) | 紧凑间距 |
| `--spacing-sm` | `0.5rem` (8px) | 小间距 |
| `--spacing-md` | `1rem` (16px) | 标准间距 |
| `--spacing-lg` | `1.5rem` (24px) | 大间距 |
| `--spacing-xl` | `2rem` (32px) | 超大间距 |
| `--spacing-2xl` | `3rem` (48px) | 顶级间距 |

**Tailwind 类映射**：
```css
p-4  → padding: var(--spacing-lg);
px-8 → padding-left/right: var(--spacing-2xl);
py-4 → padding-top/bottom: var(--spacing-lg);
```

## 🎨 圆角 (Border Radius)

| Token | 值 | 应用场景 |
|------|-----|---------|
| `--radius-sm` | `0.375rem` (6px) | 小按钮 |
| `--radius-md` | `0.5rem` (8px) | 输入框 |
| `--radius-lg` | `0.75rem` (12px) | 卡片 |
| `--radius-xl` | `1rem` (16px) | 大卡片 |
| `--radius-2xl` | `1.5rem` (24px) | 主卡片/弹框 |

**Tailwind 类映射**：
```css
rounded-xl  → border-radius: var(--radius-xl);
rounded-2xl → border-radius: var(--radius-2xl);
```

## 🎨 字体大小 (Font Size)

| Token | 值 | 应用场景 |
|------|-----|---------|
| `--font-size-xs` | `0.75rem` (12px) | 辅助文本 |
| `--font-size-sm` | `0.875rem` (14px) | 标签文本 |
| `--font-size-base` | `1rem` (16px) | 正文 |
| `--font-size-lg` | `1.125rem` (18px) | 小标题 |
| `--font-size-xl` | `1.25rem` (20px) | 标题 |
| `--font-size-2xl` | `1.5rem` (24px) | 大标题 |
| `--font-size-4xl` | `2.25rem` (36px) | 特大标题 |

## 🎨 字体粗细 (Font Weight)

| Token | 值 | 应用场景 |
|------|-----|---------|
| `--font-weight-normal` | `400` | 常规 |
| `--font-weight-bold` | `700` | 加粗 |
| `--font-weight-black` | `900` | 超粗 |

## 🎨 颜色 (Colors)

### 灰度 (Grays)

| Token | 颜色值 | 应用场景 |
|------|--------|---------|
| `--color-gray-50` | `#f9fafb` | 背景 |
| `--color-gray-100` | `#f3f4f6` | 浅背景 |
| `--color-gray-200` | `#e5e7eb` | 边框 |
| `--color-gray-400` | `#9ca3af` | 次级文本 |
| `--color-gray-500` | `#6b7280` | 辅助文本 |
| `--color-gray-600` | `#4b5563` | 次要文本 |
| `--color-gray-700` | `#374151` | 标题文本 |
| `--color-gray-800` | `#1f2937` | 主要文本 |

### 主题色 (Primary)

| Token | 颜色值 | 应用场景 |
|------|--------|---------|
| `--color-primary` | `#6366f1` | Indigo 500 |
| `--color-primary-dark` | `#4f46e5` | Indigo 600 |
| `--color-purple-400` | `#a78bfa` | 渐变 |

### 功能色 (Functional)

| Token | 颜色值 | 语义 |
|------|--------|------|
| `--color-success` | `#10b981` | 成功/通过 |
| `--color-warning` | `#f59e0b` | 警告/注意 |
| `--color-danger` | `#ef4444` | 错误/危险 |
| `--color-info` | `#0ea5e9` | 信息 |

## 🎨 阴影 (Shadows)

| Token | 值 | 应用场景 |
|------|-----|---------|
| `--shadow-sm` | `0 1px 2px 0 rgb(0 0 0 / 0.05)` | 卡片 |
| `--shadow-lg` | `0 10px 15px -3px rgb(0 0 0 / 0.1)` | 悬浮 |
| `--shadow-xl` | `0 20px 25px -5px rgb(0 0 0 / 0.1)` | 弹框 |
| `--shadow-2xl` | `0 25px 50px -12px rgb(0 0 0 / 0.25)` | 强调 |

## 🎨 过渡动画 (Transitions)

| Token | 值 | 应用场景 |
|------|-----|---------|
| `--duration-fast` | `150ms` | hover 效果 |
| `--duration-normal` | `300ms` | 标准过渡 |
| `--duration-slow` | `500ms` | 强调动画 |
| `--ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | 进入动画 |
| `--ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | 进出动画 |

## 📝 使用示例

### 在 CSS 中使用

```css
.custom-component {
  padding: var(--spacing-xl);
  border-radius: var(--radius-2xl);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  background-color: var(--color-gray-50);
  transition: all var(--duration-normal) var(--ease-in-out);
}
```

### 在 Tailwind 中使用

项目已配置 Tailwind，推荐直接使用 Tailwind 类名：

```html
<div class="p-8 rounded-2xl text-sm font-bold bg-gray-50">
  <!-- 内容 -->
</div>
```

### 在 utilities 中使用 @apply

```css
/* src/assets/styles/utilities/card.css */
.card-container {
  @apply bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden;
}
```
