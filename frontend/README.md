# GW2 Log Score - Frontend

激战2 战斗日志评分系统前端项目

## 项目概述

这是一个用于分析和评分激战2 战斗日志的 Web 应用前端，使用 Vue 3 + Vite 构建。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **路由**: Vue Router
- **HTTP 客户端**: Axios
- **图表**: ECharts
- **图标**: Lucide Vue

## 目录结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 通用组件
│   ├── composables/     # 组合式函数
│   ├── constants/       # 常量定义
│   ├── hooks/           # 自定义 Hooks
│   ├── router/          # 路由配置
│   ├── styles/          # 全局样式
│   ├── utils/           # 工具函数
│   ├── views/           # 页面视图
│   ├── App.vue
│   └── main.js
├── public/
│   └── robots.txt
├── docs/                # 文档
├── .env.development     # 开发环境
├── .env.production      # 生产环境
└── package.json
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173

### 生产构建

```bash
npm run build
```

### 预览构建结果

```bash
npm run preview
```

## 开发指南

### 代码规范

详细的代码规范请参考 [docs/CODE_GUIDELINES.md](./docs/CODE_GUIDELINES.md)

### 关键目录说明

- **composables/**: 包含可复用的组合式函数，如 `usePlayerDisplay`、`useCoreMetrics`
- **constants/**: 集中管理常量，如职业翻译、分数范围、颜色映射
- **utils/**: 工具函数集合，包括格式化、职业处理等

### 常用命令

```bash
# 代码检查与自动修复
npm run lint

# 代码格式化
npm run format
```

## 环境配置

项目支持多环境配置：

- **.env.development**: 开发环境
- **.env.production**: 生产环境

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| VITE_API_BASE_URL | API 基础路径 | /api |
| VITE_APP_ENV | 环境标识 | - |
| VITE_PORT | 服务端口 | 开发 5173 / 生产 4173 |

## 功能模块

### 主要页面

1. **Dashboard** - 实时数据看板（首页）
2. **History** - 历史记录
3. **Attendance** - 出勤统计
4. **Settings** - 系统设置

### 核心功能

- 玩家信息切换显示（角色名 ↔ 账号ID）
- 职业数据展示与翻译
- 分数计算与可视化
- 历史数据趋势分析
- 出勤统计

## 贡献指南

请遵循代码规范，提交前确保：
1. 运行 `npm run lint` 检查代码
2. 运行 `npm run format` 格式化代码
3. 所有功能测试通过

## 许可证

待确定
