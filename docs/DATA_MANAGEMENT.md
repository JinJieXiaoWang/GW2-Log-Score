# 数据管理指南

本文档合并了Elite Insights数据字段说明和职业数据管理规范。

## Elite Insights data.json 字段说明

### 基础信息 (根级别字段)
包含eliteInsightsVersion, triggerID, fightName, duration, success等字段。

### Targets (目标/敌人) 字段
数组，每个元素代表一个目标/敌人，包含id, name, totalHealth等。

### Players (玩家) 字段
数组，每个元素代表一个玩家，包含account, characterName, profession等。

### Phases (阶段) 字段
战斗阶段信息。

### Statistics (统计) 字段
dpsAll, statsAll, defenses, support等统计数据。

## GW2 职业数据管理规范

### 概述
统一管理职业数据的规范，解决数据分散问题。

### 数据架构
- **单一真实来源**: 职业数据统一存储在 `config/professions.json`
- **前后端共享**: 配置文件同时被后端和前端使用
- **职责分离**: 结构数据在professions.json，翻译数据在i18n文件中

### 文件结构
```
config/professions.json      # 统一职业数据配置文件
resources/i18n/zh-CN.json    # 中文翻译
frontend/src/composables/useProfessions.js  # 前端处理模块
```

### professions.json 结构
包含roles, professionColors, professions数组等。

### 前端使用方式
通过useProfessions组合式函数获取职业数据。

### 后端使用方式
直接读取config/professions.json文件。

### 数据维护流程
1. 修改config/professions.json
2. 更新resources/i18n/*.json中的翻译
3. 测试前后端功能
4. 提交代码

### 注意事项
- 保持数据一致性
- 定期更新职业信息
- 遵循命名规范</content>
<parameter name="filePath">d:\Code\GW2-Log-Score-main\docs\DATA_MANAGEMENT.md