# 开发指南

## 1. 项目结构

### 1.1 后端项目结构

```
backend/
├── app/               # 应用核心代码
│   ├── api/           # API路由
│   ├── config/        # 配置管理
│   ├── core/          # 核心功能
│   ├── database/      # 数据库操作
│   ├── parser/        # 日志解析
│   ├── scoring/       # 评分计算
│   ├── services/      # 业务逻辑
│   └── utils/         # 工具函数
├── config/            # 配置文件
├── database/          # 数据库文件
├── logs/              # 日志文件
├── monitoring/        # 监控脚本
├── uploads/           # 上传文件
├── main.py            # 应用入口
├── requirements.txt   # 依赖包
└── test_upload.py     # 测试脚本
```

### 1.2 主要模块说明

- **app/api/**: 定义API路由，处理HTTP请求
- **app/config/**: 配置加载和管理
- **app/core/**: 应用核心功能，如日志、异常处理等
- **app/database/**: 数据库操作和管理
- **app/parser/**: 解析GW2日志文件
- **app/scoring/**: 计算玩家评分
- **app/services/**: 业务逻辑层，处理文件上传、数据处理等
- **app/utils/**: 工具函数和辅助方法

## 2. 环境搭建

### 2.1 依赖安装

```bash
# 安装依赖
pip install -r requirements.txt
```

### 2.2 配置文件

1. 复制默认配置文件：
   ```bash
   cp config/default.json.example config/default.json
   ```

2. 根据需要修改配置文件：
   - `config/default.json`: 默认配置
   - `config/development.json`: 开发环境配置
   - `config/production.json`: 生产环境配置

### 2.3 数据库初始化

数据库会在首次运行时自动初始化，无需手动操作。

## 3. 开发流程

### 3.1 启动开发服务器

```bash
# 启动后端服务器
python main.py

# 启动监控服务
start start_monitor.bat
```

### 3.2 API文档

启动服务器后，可以通过以下地址访问API文档：

```
http://localhost:8001/api/docs
```

### 3.3 代码规范

- 遵循PEP 8代码规范
- 使用类型注解
- 编写详细的文档字符串
- 添加适当的错误处理
- 保持代码风格一致

## 4. 配置管理

### 4.1 配置加载器

使用统一的配置加载器实例：

```python
from app.config.config_loader import config_loader
```

### 4.2 配置访问规范

详细的配置访问规范请参考 `CONFIG_ACCESS_GUIDELINE.md` 文件。

## 5. 错误处理

### 5.1 异常处理

- 在API层捕获并处理异常
- 在服务层添加详细的错误处理
- 在核心计算模块添加输入验证

### 5.2 日志记录

- 使用 `app.core.logger` 记录日志
- 记录关键操作和错误信息
- 保持日志格式一致

## 6. 测试

### 6.1 上传测试

```bash
# 测试文件上传
python test_upload.py
```

### 6.2 功能测试

- 测试文件上传和解析
- 测试评分计算
- 测试API响应

## 7. 部署

### 7.1 生产环境部署

1. 配置生产环境配置文件：
   ```bash
   cp config/production.json.example config/production.json
   ```

2. 启动服务：
   ```bash
   # 使用生产环境配置
   export ENVIRONMENT=production
   python main.py
   ```

### 7.2 监控部署

在生产环境中，建议使用系统服务管理工具（如systemd）来管理监控服务。

## 8. 常见问题

### 8.1 端口占用

如果端口8001被占用，可以修改 `config/default.json` 文件中的端口配置：

```json
{
  "server": {
    "port": 8002
  }
}
```

### 8.2 配置错误

如果出现配置访问错误，请参考 `CONFIG_ACCESS_GUIDELINE.md` 文件中的配置访问规范。

### 8.3 文件上传失败

- 检查文件格式是否支持（支持JSON/EVTC/ZEVTC格式）
- 检查文件大小是否超过限制
- 检查上传目录权限

## 9. 维护

### 9.1 日志管理

- 定期清理日志文件
- 监控日志文件大小

### 9.2 数据库维护

- 定期备份数据库
- 监控数据库大小

### 9.3 配置更新

- 遵循配置变更流程
- 记录配置变更历史

## 10. 贡献

### 10.1 代码提交

- 提交前运行测试
- 编写详细的提交信息
- 遵循代码规范

### 10.2 问题反馈

- 提供详细的错误信息
- 提供复现步骤
- 提供环境信息

## 11. 联系方式

- 项目维护者：[Your Name]
- 联系方式：[your.email@example.com]
- 项目地址：[https://github.com/yourusername/gw2-log-score]
