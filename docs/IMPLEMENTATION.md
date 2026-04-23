# 项目结构优化与配置管理改进实施建议

## 实施总结

本项目已完成以下优化工作：

1. **配置文件系统建设**：
   - 创建了标准化配置文件体系，包含端口号、环境变量、API地址等核心配置项
   - 设计了JSON格式的配置文件，确保配置项分类清晰、易于维护
   - 实现了配置文件的加载机制，支持环境变量覆盖和配置文件继承

2. **日志系统实现**：
   - 设计并实现了日志记录功能，包括日志级别划分（INFO/WARN/ERROR等）
   - 配置了日志文件的存储路径、命名规则及轮转策略
   - 确保日志内容包含必要的上下文信息（时间戳、模块名、错误堆栈等）

3. **资源文件管理**：
   - 将英译汉相关文件整合到指定的资源目录中
   - 建立了资源文件的版本管理机制，确保多语言支持的可维护性

4. **项目目录结构优化**：
   - 对现有杂乱的项目目录进行了重组，建立了清晰的目录层次
   - 将data目录明确标记为mock数据目录，与正式业务文件分离
   - 该data目录仅用于存放测试样例所需的知识样本文件，不得包含正式业务数据

## 目录结构设计

```
GW2-Log-Score/
├── backend/              # 后端代码
│   ├── api/              # API路由
│   ├── config/           # 配置管理
│   ├── core/             # 核心功能
│   ├── database/         # 数据库管理
│   ├── models/           # 数据模型
│   ├── parser/           # 日志解析器
│   ├── reports/          # 报告生成
│   ├── resources/        # 资源文件
│   │   └── i18n/         # 国际化文件
│   ├── scoring/          # 评分引擎
│   └── main.py           # 主入口
├── config/               # 配置文件
│   ├── default.json      # 默认配置
│   └── production.json   # 生产环境配置
├── data/                 # 测试数据（仅用于测试样例）
│   └── samples/          # 测试样本文件
├── databases/            # 数据库文件
├── docs/                 # 文档
├── frontend/             # 前端代码
│   ├── src/              # 源代码
│   └── dist/             # 构建输出
├── logs/                 # 日志文件
├── scripts/              # 脚本工具
├── tests/                # 测试代码
├── uploads/              # 上传文件
├── .env                  # 环境变量
├── .env.example          # 环境变量示例
├── requirements.txt      # 依赖项
├── start.py              # 启动脚本
└── README.md             # 项目说明
```

## 配置文件模板

### config/default.json

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "database": {
    "url": "sqlite:///databases/gw2_logs.db"
  },
  "upload": {
    "directory": "uploads/",
    "max_size": 10485760
  },
  "logging": {
    "level": "INFO",
    "file": "logs/backend.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "rotation": {
      "max_size": 10485760, 
      "backup_count": 5
    }
  },
  "security": {
    "secret_key": "your-secret-key-here"
  },
  "scoring": {
    "threshold": 80,
    "config": {
      "PVE": {
        "DPS": {
          "weights": {"dps": 0.4, "cc": 0.35, "survival": 0.25},
          "metrics": ["dps", "cc", "survival"]
        },
        "SUPPORT": {
          "weights": {"stability": 0.35, "resistance": 0.35, "boon": 0.3},
          "metrics": ["stability", "resistance", "boon"]
        }
      },
      "WvW": {
        "DPS": {
          "weights": {"dps": 0.6, "downs": 0.2, "survival": 0.2},
          "metrics": ["dps", "downs_per_min", "survival"]
        },
        "SUPPORT": {
          "weights": {"stability": 0.2, "resistance": 0.15, "quickness": 0.15, "cleanses": 0.2, "strips": 0.2, "survival": 0.1},
          "metrics": ["stability_per_sec", "resistance_per_sec", "quickness_per_sec", "cleanses_per_min", "strips_per_min", "survival"]
        },
        "UTILITY": {
          "weights": {"strips": 0.3, "cleanses": 0.3, "cc": 0.2, "survival": 0.2},
          "metrics": ["strips_per_min", "cleanses_per_min", "cc_per_min", "survival"]
        }
      }
    }
  },
  "buff_ids": {
    "稳固": 1122,
    "抗性": 4614,
    "急速": 1187,
    "敏捷": 30328,
    "保护": 717,
    "决心": 718
  },
  "prof_roles": {
    "Firebrand": "SUPPORT",
    "Herald": "SUPPORT",
    "Chronomancer": "SUPPORT",
    "Druid": "SUPPORT",
    "Mechanist": "SUPPORT",
    "Tempest": "SUPPORT",
    "Scrapper": "SUPPORT",
    "Scourge": "UTILITY",
    "Spellbreaker": "UTILITY",
    "Vindicator": "UTILITY",
    "Berserker": "DPS",
    "Willbender": "DPS",
    "Soulbeast": "DPS",
    "Virtuoso": "DPS",
    "Reaper": "DPS",
    "Holosmith": "DPS",
    "Deadeye": "DPS",
    "Daredevil": "DPS",
    "Catalyst": "DPS"
  },
  "environment": "development"
}
```

### config/production.json

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "logging": {
    "level": "WARNING",
    "file": "logs/backend.log"
  },
  "environment": "production"
}
```

## 环境变量模板

### .env.example

```
# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///databases/gw2_logs.db

# 上传配置
UPLOAD_DIR=uploads/
MAX_UPLOAD_SIZE=10485760  # 10MB

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/backend.log

# 安全配置
SECRET_KEY=your-secret-key-here

# 评分配置
SCORE_THRESHOLD=80

# 环境
ENVIRONMENT=development
```

## 日志系统配置

### 日志级别

- **DEBUG**: 详细的调试信息，仅在开发环境使用
- **INFO**: 一般性信息，如服务启动、请求处理等
- **WARNING**: 警告信息，如配置问题、性能问题等
- **ERROR**: 错误信息，如异常、失败的操作等
- **CRITICAL**: 严重错误信息，如系统崩溃、数据丢失等

### 日志轮转策略

- **最大文件大小**: 10MB
- **备份文件数量**: 5个
- **存储路径**: logs/backend.log

## 资源文件管理

### 国际化文件

- **中文**: backend/resources/i18n/zh-CN.json
- **英文**: backend/resources/i18n/en-US.json

### 资源文件版本管理

1. 每次修改国际化文件时，确保同时更新所有语言版本
2. 为重要的资源文件变更添加版本号
3. 定期检查资源文件的完整性和一致性

## 项目目录管理建议

1. **backend/**: 后端代码目录，包含所有服务器端逻辑
2. **config/**: 配置文件目录，存放所有环境的配置文件
3. **data/**: 测试数据目录，仅用于存放测试样例所需的知识样本文件
4. **databases/**: 数据库文件目录，存放所有SQLite数据库文件
5. **docs/**: 文档目录，存放项目相关的文档
6. **frontend/**: 前端代码目录，包含所有客户端逻辑
7. **logs/**: 日志文件目录，存放所有日志文件
8. **scripts/**: 脚本工具目录，存放各种辅助脚本
9. **tests/**: 测试代码目录，存放所有测试文件
10. **uploads/**: 上传文件目录，存放用户上传的文件

## 实施建议

1. **配置管理**:
   - 使用JSON格式的配置文件，便于阅读和维护
   - 为不同环境创建不同的配置文件
   - 使用环境变量覆盖配置文件中的敏感信息

2. **日志管理**:
   - 根据环境设置适当的日志级别
   - 定期清理过期的日志文件
   - 确保日志内容包含足够的上下文信息

3. **资源管理**:
   - 统一管理所有资源文件
   - 为资源文件建立版本控制
   - 确保多语言支持的一致性

4. **目录管理**:
   - 保持目录结构的清晰和一致性
   - 定期清理不必要的文件和目录
   - 确保每个目录的用途明确

5. **代码质量**:
   - 遵循统一的代码风格
   - 定期进行代码审查
   - 编写详细的文档

## 结论

通过本次优化，项目的结构更加清晰，配置管理更加规范，日志系统更加完善，资源文件管理更加有序。这些改进将有助于提高项目的可维护性和可扩展性，为后续的开发和维护工作奠定良好的基础。