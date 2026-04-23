# GW2 Log Score API 文档

## 概述

GW2 Log Score API 是一个用于分析和评分 Guild Wars 2 游戏日志的 RESTful API，提供了日志解析、评分计算、数据查询等功能。

## 基础 URL

默认情况下，API 的基础 URL 为：`http://localhost:8000/api`

## 端点列表

### 1. 日志处理

#### POST /logs/parse

**功能**：解析上传的日志文件

**请求体**：
```multipart/form-data
file: <日志文件>  # 支持 .zevtc 或 .json 格式
```

**响应**：
```json
{
  "success": true,
  "data": {
    "log_id": "string",
    "encounter_name": "string",
    "mode": "string",
    "date": "string",
    "duration": "string",
    "recorded_by": "string",
    "players": [
      {
        "player_name": "string",
        "profession": "string",
        "role": "string",
        "total_score": number,
        "scores": {
          "damage": number,
          "support": number,
          "mechanics": number,
          "survivability": number
        }
      }
    ]
  }
}
```

#### GET /logs

**功能**：获取所有日志记录

**查询参数**：
- `limit`: 限制返回数量（默认 100）
- `offset`: 偏移量（默认 0）
- `encounter`: 按副本名称过滤
- `mode`: 按模式过滤（如 "raid", "fractal"）

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "log_id": "string",
      "encounter_name": "string",
      "mode": "string",
      "date": "string",
      "duration": "string",
      "recorded_by": "string",
      "player_count": number
    }
  ],
  "total": number
}
```

### 2. 评分相关

#### GET /scores/player/{player_name}

**功能**：获取指定玩家的所有评分记录

**路径参数**：
- `player_name`: 玩家名称

**查询参数**：
- `limit`: 限制返回数量（默认 100）
- `offset`: 偏移量（默认 0）
- `encounter`: 按副本名称过滤

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "log_id": "string",
      "encounter_name": "string",
      "date": "string",
      "total_score": number,
      "scores": {
        "damage": number,
        "support": number,
        "mechanics": number,
        "survivability": number
      }
    }
  ],
  "total": number
}
```

#### GET /scores/average/{player_name}

**功能**：获取指定玩家的平均评分

**路径参数**：
- `player_name`: 玩家名称

**查询参数**：
- `encounter`: 按副本名称过滤
- `days`: 最近几天的数据（默认 30）

**响应**：
```json
{
  "success": true,
  "data": {
    "player_name": "string",
    "profession": "string",
    "role": "string",
    "average_score": number,
    "average_scores": {
      "damage": number,
      "support": number,
      "mechanics": number,
      "survivability": number
    },
    "total_logs": number
  }
}
```

### 3. 出勤统计

#### GET /attendance

**功能**：获取出勤统计数据

**查询参数**：
- `start_date`: 开始日期（格式：YYYY-MM-DD）
- `end_date`: 结束日期（格式：YYYY-MM-DD）
- `encounter`: 按副本名称过滤

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "player_name": "string",
      "profession": "string",
      "role": "string",
      "attendance_count": number,
      "total_logs": number,
      "attendance_rate": number,
      "average_score": number
    }
  ]
}
```

### 4. 系统设置

#### GET /settings

**功能**：获取系统设置

**响应**：
```json
{
  "success": true,
  "data": {
    "system_name": "string",
    "system_slogan": "string",
    "score_threshold": number,
    "max_upload_size": number
  }
}
```

#### PUT /settings

**功能**：更新系统设置

**请求体**：
```json
{
  "system_name": "string",
  "system_slogan": "string",
  "score_threshold": number
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "system_name": "string",
    "system_slogan": "string",
    "score_threshold": number,
    "max_upload_size": number
  }
}
```

## 错误响应

当请求失败时，API 会返回以下格式的错误响应：

```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

常见错误代码：
- `INVALID_FILE`: 无效的文件格式
- `PARSE_ERROR`: 日志解析失败
- `NOT_FOUND`: 资源不存在
- `INTERNAL_ERROR`: 内部服务器错误

## 示例用法

### 上传并解析日志

```bash
curl -X POST "http://localhost:8000/api/logs/parse" \
  -F "file=@path/to/log.zevtc"
```

### 获取玩家评分历史

```bash
curl "http://localhost:8000/api/scores/player/PlayerName?limit=10"
```

### 获取出勤统计

```bash
curl "http://localhost:8000/api/attendance?start_date=2026-01-01&end_date=2026-04-30"
```
