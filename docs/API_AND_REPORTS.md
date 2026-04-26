# API和报告文档

本文档合并了API文档和比较报告相关文档。

## GW2 Log Score API 文档

### 概述
用于分析和评分 Guild Wars 2 游戏日志的 RESTful API。

### 基础 URL
`http://localhost:8000/api`

### 主要端点

#### 日志处理
- **POST /logs/parse**: 解析上传的日志文件
- **GET /logs/{log_id}**: 获取日志详情
- **GET /logs**: 获取日志列表

#### 评分系统
- **GET /scoring/rules**: 获取评分规则
- **POST /scoring/calculate**: 计算评分

#### 数据查询
- **GET /players**: 获取玩家数据
- **GET /players/{player_id}**: 获取玩家详情
- **GET /statistics**: 获取统计数据

### 请求/响应格式
支持JSON格式，包含success, data, error字段。

## 比较报告

### 数据比对结果
- **JSON vs ZEVTC**: 字段完整性对比
- **时长计算**: 精确度验证
- **玩家数据**: 一致性检查

### 优化建议
- 数据格式标准化
- 解析器兼容性提升
- 错误处理改进

### 测试覆盖
- 多种战斗类型
- 不同团队规模
- 异常情况处理</content>
<parameter name="filePath">d:\Code\GW2-Log-Score-main\docs\API_AND_REPORTS.md