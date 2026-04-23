# GW2 Log Score - 前端代码规范

## 目录结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源（图片、字体等）
│   ├── components/      # 通用 Vue 组件
│   ├── composables/     # 组合式函数（useXxx）
│   ├── constants/       # 常量定义
│   ├── hooks/           # 自定义 Hooks
│   ├── router/          # 路由配置
│   ├── styles/          # 全局样式
│   ├── utils/           # 工具函数
│   ├── views/           # 页面视图组件
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── public/              # 公共资源
├── docs/                # 文档
├── .env.development     # 开发环境配置
├── .env.production      # 生产环境配置
├── vite.config.js       # Vite 配置
└── package.json         # 项目依赖
```

## 命名规范

### 文件命名
- **组件文件**：PascalCase（如 `ScoreTable.vue`）
- **组合式函数**：camelCase，以 use 开头（如 `usePlayerDisplay.js`）
- **工具函数**：camelCase（如 `format.js`）
- **常量文件**：camelCase（如 `profession.js`）

### 变量与函数命名
- **变量**：camelCase（如 `playerName`）
- **常量**：UPPER_SNAKE_CASE（如 `PROFESSION_COLORS`）
- **函数**：camelCase（如 `getDisplayName`）
- **事件处理**：handleXxx（如 `handleClick`）

### Vue 组件
- **组件名**：PascalCase
- **Props**：camelCase 声明，kebab-case 使用
- **Emits**：kebab-case（如 `select-player`）
- **Ref 变量**：直接使用值语义（如 `const count = ref(0)`）

## 代码组织

### 常量定义
- 所有常量统一放在 `src/constants/` 目录
- 按功能模块分类
- 通过 `index.js` 统一导出

### 工具函数
- 所有工具函数统一放在 `src/utils/` 目录
- 按功能分类（format、profession、role 等）
- 保持函数纯净，无副作用

### 组合式函数
- 所有组合式函数放在 `src/composables/` 目录
- 以 `use` 前缀命名
- 单一职责，功能清晰

## 代码风格

### Vue SFC 结构
```vue
<script setup>
// 1. 导入
import { ref, computed } from 'vue'

// 2. 定义 Props/Emits
const props = defineProps()
const emit = defineEmits()

// 3. 组合式函数
const { someValue } = useSomeComposable()

// 4. 响应式数据
const data = ref()

// 5. 计算属性
const computedValue = computed(() => {})

// 6. 方法
const handleEvent = () => {}

// 7. 生命周期
onMounted(() => {})
</script>

<template>
  <!-- 模板内容 -->
</template>

<style scoped>
/* 样式内容 */
</style>
```

### Tailwind CSS 使用
- 优先使用 Tailwind 工具类
- 复杂样式考虑抽离到 `styles/` 目录
- 保持样式原子化

## Git 提交规范

### 提交消息格式
```
<type>(<scope>): <subject>

<body>
```

### Type 类型
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 环境配置

### 开发环境
```bash
npm run dev
```
- 访问 `http://localhost:5173`
- API 代理到 `http://127.0.0.1:8000`

### 生产环境
```bash
npm run build
npm run preview
```
- 构建产物在 `dist/` 目录

## 代码检查与格式化

```bash
# Lint 检查并自动修复
npm run lint

# 格式化代码
npm run format
```
