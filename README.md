# GW2 Log Score

激战2日志解析与出勤评分系统

## 项目结构

```
GW2-Log-Score/
├── backend/           # 后端代码
│   ├── config/        # 配置文件
│   ├── docs/          # 后端文档
│   ├── gw2_log_score/ # 后端源码包
│   ├── pyproject.toml # Python项目配置
│   ├── requirements.txt # 依赖文件
│   └── tests/         # 测试代码
├── frontend/          # 前端代码
├── resources/         # 共享资源文件
├── LICENSE            # 许可证
├── README.md          # 项目说明
└── .gitignore         # Git忽略文件
```

## 技术栈

- **前端**：Vue.js 3, Vite, Tailwind CSS, ECharts
- **后端**：FastAPI, SQLite
- **状态管理**：Vue Composition API
- **路由管理**：Vue Router
- **HTTP客户端**：Axios
- **代码规范**：ESLint, Prettier

## 功能特性

- **多格式支持**：支持JSON和ZEVTC格式的日志文件
- **WvW战斗分析**：专门针对WvW战斗进行分析和评分
- **出勤管理**：记录和管理玩家出勤情况
- **评分系统**：基于战斗表现对玩家进行评分
- **数据可视化**：提供直观的数据展示界面
- **API接口**：提供RESTful API接口供前端调用
- **职业颜色区分**：不同职业和定位有明显的视觉标识
- **职业定位显示**：正确显示职业的定位信息

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
cd frontend
npm install
```

### 运行后端

```bash
python src/main.py --serve --port 8080
```

### 运行前端

```bash
cd frontend
npm run dev
```

## BUFF 图标库

项目新增 `src/utils/gw2_icon_downloader.py`，用于从 Guild Wars 2 API 拉取增益/减益(buff)图标并生成本地映射。

用法示例：

```bash
python src/utils/gw2_icon_downloader.py --buff-ids 35676 37233 --output-dir resources/icons/buffs
```

或者从文本文件读取 BUFF ID：

```bash
python src/utils/gw2_icon_downloader.py --ids-file buff_ids.txt
```

生成结果会保存在 `resources/icons/buffs`，映射文件默认写入 `resources/icons/buffs/buff_mapping.json`。

## 日志文件格式

系统支持以下格式的日志文件：

1. **JSON格式**：由EI（Encounter Insights）导出的data.json文件
2. **ZEVTC格式**：arcdps生成的原生日志格式，支持压缩和非压缩版本

## 解析流程

1. 上传日志文件（JSON或ZEVTC格式）
2. 系统自动识别文件格式并选择相应的解析器
3. 解析战斗数据，提取玩家信息和战斗统计
4. 计算玩家评分和出勤情况
5. 存储数据到数据库
6. 生成报表和可视化展示

## 评分系统

WvW评分基于以下因素：

- **大团模式**：
  - 有效伤害
  - 破控伤害
  - 存活能力
  - 辅助能力（稳固覆盖率、抗性覆盖率、撕BUFF、清条件）

- **毒瘤模式**：
  - 击杀数
  - 存活时间
  - 击倒敌人数
  - 存活能力

## API接口

- `POST /api/upload` - 上传日志文件
- `GET /api/players` - 获取玩家列表
- `GET /api/attendance` - 获取出勤记录
- `GET /api/scores` - 获取评分数据
- `GET /api/professions` - 获取职业信息
- `GET /api/history` - 获取历史数据
- `POST /api/clear` - 清除数据
- `POST /api/sync` - 同步数据

## 开发指南

### 代码风格

项目使用以下代码风格工具：
- **black**：代码格式化
- **isort**：导入排序
- **flake8**：代码质量检查
- **ESLint**：前端代码质量检查
- **Prettier**：前端代码格式化

### 配置文件

职业配置文件位于 `config/default.json`，包含职业翻译、颜色和定位信息。

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
