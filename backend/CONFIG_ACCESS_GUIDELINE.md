# 配置访问规范

## 1. 配置加载器使用指南

### 1.1 配置加载器实例

在整个项目中，应使用统一的配置加载器实例：

```python
from app.config.config_loader import config_loader
```

### 1.2 配置访问方式

配置加载器提供了两种访问配置的方式：

#### 1.2.1 直接属性访问

对于评分规则相关的配置，应使用直接属性访问：

```python
# 正确的访问方式
config = config_loader.scoring_rules_config

# 错误的访问方式 (不存在的方法)
config = config_loader.get_scoring_rules_config()  # 错误！
```

#### 1.2.2 方法访问

对于其他配置，应使用相应的方法访问：

```python
# 正确的访问方式
server_config = config_loader.get_server_config()
database_config = config_loader.get_database_config()
scoring_config = config_loader.get_scoring_config()

# 错误的访问方式 (属性不存在)
server_config = config_loader.server_config  # 错误！
```

## 2. 配置访问最佳实践

### 2.1 避免使用 settings 对象

`settings` 对象是一个 `SimpleNamespace` 对象，仅包含 `config` 字典的内容，不包含 `scoring_rules_config` 等属性：

```python
# 错误的访问方式
from app.config.config_loader import settings
config = settings.scoring_rules_config  # 错误！

# 正确的访问方式
from app.config.config_loader import config_loader
config = config_loader.scoring_rules_config  # 正确！
```

### 2.2 配置验证

在使用配置前，应进行适当的验证：

```python
config = config_loader.scoring_rules_config
if not isinstance(config, dict):
    raise ValueError("Invalid configuration format")
```

### 2.3 错误处理

在访问配置时，应添加适当的错误处理：

```python
try:
    config = config_loader.scoring_rules_config
    # 使用配置
except Exception as e:
    raise ValueError(f"Failed to load configuration: {e}")
```

## 3. 常见错误及解决方案

### 3.1 错误：'ConfigLoader' object has no attribute 'get_scoring_rules_config'

**原因**：尝试调用不存在的 `get_scoring_rules_config()` 方法。

**解决方案**：使用直接属性访问 `config_loader.scoring_rules_config`。

### 3.2 错误：'types.SimpleNamespace' object has no attribute 'scoring_rules_config'

**原因**：尝试从 `settings` 对象访问 `scoring_rules_config` 属性。

**解决方案**：使用 `config_loader.scoring_rules_config` 而不是 `settings.scoring_rules_config`。

### 3.3 错误：配置访问不一致

**原因**：在不同模块中使用不同的配置访问方式。

**解决方案**：统一使用本文档中规定的配置访问方式。

## 4. 配置文件结构

### 4.1 主要配置文件

- `config/default.json` - 默认配置
- `config/scoring_rules.json` - 评分规则配置
- `config/professions.json` - 职业配置

### 4.2 环境配置文件

- `config/development.json` - 开发环境配置
- `config/production.json` - 生产环境配置

## 5. 配置变更流程

1. 修改相应的配置文件
2. 验证配置文件格式是否正确
3. 重启应用以加载新配置
4. 测试配置变更是否生效

## 6. 配置访问代码示例

### 6.1 正确的配置访问示例

```python
from app.config.config_loader import config_loader

# 访问评分规则配置
scoring_rules = config_loader.scoring_rules_config

# 访问服务器配置
server_config = config_loader.get_server_config()

# 访问数据库配置
db_config = config_loader.get_database_config()

# 访问上传配置
upload_config = config_loader.get_upload_config()
```

### 6.2 错误的配置访问示例

```python
# 错误：使用不存在的方法
scoring_rules = config_loader.get_scoring_rules_config()  # 错误！

# 错误：从 settings 对象访问不存在的属性
from app.config.config_loader import settings
scoring_rules = settings.scoring_rules_config  # 错误！

# 错误：直接访问不存在的属性
server_config = config_loader.server_config  # 错误！
```

## 7. 配置访问检查清单

- [ ] 使用 `config_loader` 实例而不是 `settings` 对象
- [ ] 对于评分规则配置，使用直接属性访问 `config_loader.scoring_rules_config`
- [ ] 对于其他配置，使用相应的方法访问，如 `config_loader.get_server_config()`
- [ ] 在使用配置前进行适当的验证
- [ ] 添加适当的错误处理
- [ ] 统一配置访问方式，避免不一致

遵循以上规范，可以有效防止配置访问错误，提高代码的可靠性和可维护性。