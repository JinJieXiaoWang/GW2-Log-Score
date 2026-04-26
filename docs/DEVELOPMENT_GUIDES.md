# 开发指南

本文档合并了项目的开发相关文档，包括项目概述、环境设置、代码规范、开发流程等。

## 项目概述

GW2-Log-Score 是一个基于 Python 后端和 Vue3 前端的 GW2 战斗日志解析与出勤评分系统，专注于 WvW 战斗分析。

### 核心功能

1. **日志解析引擎**
   - 支持 JSON 和 ZEVTC 格式日志解析
   - 实时战斗数据提取和处理
   - 玩家行为模式分析

2. **评分系统**
   - 基于战斗表现的综合评分
   - 支持大团和毒瘤两种玩法模式
   - 可配置的评分权重系统

3. **数据可视化**
   - 实时战斗数据图表展示
   - 历史战绩趋势分析
   - 玩家对比分析

4. **出勤管理**
   - 玩家出勤记录和统计
   - 团队表现追踪
   - 历史数据导出

### 技术栈

#### 后端
- **框架**: FastAPI
- **数据库**: SQLite
- **解析**: 自定义二进制解析器
- **数据处理**: Pandas

#### 前端
- **框架**: Vue 3 + Composition API
- **构建**: Vite
- **样式**: Tailwind CSS + PrimeVue
- **图表**: ECharts
- **状态管理**: Vue Composition API

## 项目结构

```
GW2-Log-Score/
├── backend/              # 后端代码
│   ├── api/              # API 接口
│   ├── config/           # 配置管理
│   ├── core/             # 核心功能
│   ├── database/         # 数据库管理
│   ├── models/           # 数据模型
│   ├── parser/           # 日志解析器
│   │   ├── base_parser.py        # 基础解析器
│   │   ├── gw2_log_parser.py     # 主解析器
│   │   ├── wvw_evtc_parser.py    # ZEVTC解析器
│   │   ├── json_handler.py       # JSON处理器
│   │   └── evtc_handler.py       # EVTC处理器
│   ├── scoring/          # 评分引擎
│   │   ├── base_scorer.py        # 基础评分器
│   │   ├── wvw_scorer.py         # WvW评分器
│   │   ├── pve_scorer.py         # PVE评分器
│   │   └── scoring_engine.py     # 主评分引擎
│   └── reports/          # 报告生成
├── frontend/             # 前端代码
│   ├── public/           # 静态资源
│   ├── src/              # 源代码
│   │   ├── assets/       # 静态资源
│   │   ├── components/   # 可复用组件
│   │   │   ├── base/     # 基础组件 (PrimeVue + Tailwind)
│   │   │   ├── charts/   # 图表组件
│   │   │   ├── forms/    # 表单组件
│   │   │   └── layouts/  # 布局组件
│   │   ├── composables/  # 组合式函数
│   │   ├── router/       # 路由配置
│   │   ├── utils/        # 工具函数
│   │   ├── views/        # 页面视图
│   │   ├── App.vue       # 根组件
│   │   └── main.js       # 入口文件
│   ├── index.html        # HTML 模板
│   ├── package.json      # 依赖配置
│   └── vite.config.js    # Vite 配置
├── config/               # 配置文件
├── databases/            # 数据库文件
├── docs/                 # 项目文档
├── tests/                # 测试文件
├── scripts/              # 工具脚本
├── data/                 # 数据文件
├── uploads/              # 上传文件
├── logs/                 # 日志文件
├── .env.example          # 环境变量示例
├── .gitignore            # Git 忽略配置
├── README.md             # 项目说明
└── requirements.txt      # Python 依赖
```

## 开发环境设置

### 后端

1. **安装 Python 依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置相应的配置
   ```

3. **启动开发服务器**
   ```bash
   python backend/main.py --serve
   ```

4. **运行测试**
   ```bash
   pytest
   ```

### 前端

1. **安装 Node.js 依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **启动开发服务器**
   ```bash
   npm run dev
   ```

3. **构建生产版本**
   ```bash
   npm run build
   ```

## 代码规范

### 后端

- 遵循 PEP 8 代码规范
- 使用类型提示
- 函数和方法应该有清晰的文档字符串
- 异常处理应该明确且有意义

### 前端

- 使用 ESLint 和 Prettier 进行代码检查和格式化
- 组件命名使用 PascalCase
- 变量和函数命名使用 camelCase
- 遵循 Vue 3 Composition API 最佳实践

### 提交规范

- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或工具配置更新

## 开发流程

1. **创建新功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **开发功能**
   - 实现后端 API 接口
   - 实现前端页面和组件
   - 编写测试用例

3. **运行测试**
   ```bash
   # 后端测试
   pytest
   
   # 前端测试
   cd frontend
   npm run test
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 实现新功能"
   ```

5. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 在 GitHub 上创建 Pull Request
   - 描述功能实现和测试情况
   - 等待代码审查

## 核心模块说明

### 后端

1. **日志解析器 (parser)**
   - 负责解析 Guild Wars 2 游戏日志文件
   - 支持 .zevtc 和 .json 格式
   - 提取战斗数据和玩家信息

2. **评分引擎 (scoring)**
   - 根据解析的数据计算玩家评分
   - 考虑伤害输出、支援能力、机制处理和生存能力
   - 生成详细的评分报告

3. **数据库管理 (database)**
   - 存储日志数据和评分记录
   - 提供数据查询和统计功能
   - 使用 SQLite 作为数据库

4. **API 路由 (api)**
   - 提供 RESTful API 接口
   - 处理前端请求
   - 返回标准化的响应格式

### 前端

1. **页面视图 (views)**
   - Dashboard: 实时数据看板
   - History: 历史平均评分
   - Attendance: 出勤统计
   - Settings: 系统设置

2. **可复用组件 (components)**
   - BaseButton/BaseCard/BaseModal/BaseTable: 基础UI组件 (PrimeVue + Tailwind)
   - ScoreTable: 评分表格
   - HistoryTrend: 历史趋势图表
   - PlayerRadar: 玩家能力雷达图
   - SystemSettings: 系统设置组件

3. **工具函数 (utils)**
   - api.js: API 调用封装
   - 其他辅助函数

## 组件样式优化指南

### 概述

在前端开发中，样式统一性和可维护性至关重要。本节针对Vue组件的样式优化问题，提供重写和样式提取的指导原则。

### 核心问题分析

**为什么需要样式优化？**
- **重复代码减少**：多个组件中重复的CSS类会导致代码冗余，增加维护成本。
- **样式一致性**：确保整个应用的视觉风格统一，避免不同组件间的样式冲突。
- **可维护性**：集中管理样式，便于主题切换和响应式设计调整。
- **性能优化**：减少CSS体积，提升渲染性能。

**Vue文件中的CSS优化原则：**
- 重复出现的样式组合应该提取
- 主题相关的颜色、字体、间距变量
- 复杂的布局样式
- 动画和过渡效果

### 实施策略

#### 使用Tailwind CSS的@apply指令
```css
.btn-primary {
  @apply bg-primary-500 text-white hover:bg-primary-600 px-4 py-2 rounded-lg;
}
```

#### CSS变量和设计系统
```css
:root {
  --color-primary: #6366f1;
  --spacing-card: 1.5rem;
}
```

#### 组件级样式类
对于组件特有的重复样式，创建局部样式类。

### 重构指南

- **基础组件**：已使用PrimeVue + Tailwind重构
- **业务组件**：逐步提取重复样式，如表格头样式 `table-header`

## 部署指南

### 本地部署

1. **启动后端服务**
   ```bash
   python backend/main.py --serve --host 0.0.0.0 --port 8000
   ```

2. **启动前端服务**
   ```bash
   cd frontend
   npm run dev
   ```

### 生产部署

1. **构建前端**
   ```bash
   cd frontend
   npm run build
   ```

2. **使用 Gunicorn 启动后端**
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
   ```

3. **配置反向代理**
   - 使用 Nginx 或 Apache 作为反向代理
   - 配置 HTTPS

## 常见问题

### 后端

1. **日志解析失败**
   - 检查日志文件格式是否正确
   - 确保日志文件没有损坏
   - 查看后端日志获取详细错误信息

2. **数据库连接问题**
   - 检查数据库文件路径是否正确
   - 确保数据库文件有写入权限

### 前端

1. **API 调用失败**
   - 检查后端服务是否运行
   - 确认 API 基础 URL 配置正确
   - 查看浏览器控制台的错误信息

2. **页面加载缓慢**
   - 检查网络连接
   - 优化组件渲染
   - 考虑使用分页加载大量数据

## 贡献指南

1. **报告问题**
   - 在 GitHub Issues 中创建详细的问题描述
   - 包含复现步骤和期望行为

2. **提交代码**
   - 遵循代码规范
   - 编写清晰的提交信息
   - 确保测试通过

3. **文档更新**
   - 及时更新 API 文档和开发指南
   - 保持文档与代码同步

## 许可证

MIT License</content>
<parameter name="filePath">d:\Code\GW2-Log-Score-main\docs\DEVELOPMENT_GUIDES.md