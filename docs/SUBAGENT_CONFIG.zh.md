# Subagent 配置管理指南

[English](SUBAGENT_CONFIG.md) | 中文

本文档详细介绍如何使用 Subagent 的持久化配置管理功能。

## 📋 目录

- [概述](#概述)
- [配置文件位置](#配置文件位置)
- [配置优先级](#配置优先级)
- [配置管理工具](#配置管理工具)
- [使用示例](#使用示例)
- [安全最佳实践](#安全最佳实践)
- [常见问题](#常见问题)

## 概述

Subagent 提供了灵活的配置管理系统，支持：

✅ **持久化存储** - API 密钥自动保存，下次启动无需重新配置  
✅ **多提供商支持** - OpenAI、Anthropic 统一管理  
✅ **自定义端点** - 支持配置自定义 API 基础 URL  
✅ **配置优先级** - 环境变量优先于配置文件  
✅ **安全存储** - 配置文件自动设置为仅所有者可读（Unix/Linux）  
✅ **脱敏显示** - 查询配置时自动脱敏，保护密钥安全

## 配置文件位置

配置文件默认保存在用户主目录：

**Windows:**

```
C:\Users\<quyansiyuanwang>\.subagent_config.json
```

**Linux/macOS:**

```
~/.subagent_config.json
```

配置文件格式示例：

```json
{
  "api_keys": {
    "openai": "sk-xxxxxxxxxxxxxxxxxxxx",
    "anthropic": "sk-ant-xxxxxxxxxxxx"
  },
  "api_bases": {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com/v1"
  }
}
```

## 配置优先级

Subagent 按以下优先级读取配置：

1. **环境变量**（最高优先级）
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_BASE`
   - `ANTHROPIC_API_BASE`

2. **配置文件**
   - `~/.subagent_config.json`

3. **默认值**
   - 各提供商的官方 API 端点

这种设计允许您：

- 在配置文件中设置常用密钥
- 临时使用环境变量覆盖配置
- 在不同项目中灵活切换配置

## 配置管理工具

### 1. subagent_config_set

设置 API 配置并持久化保存。

**参数:**

- `provider` (str): 提供商名称，支持 "openai"、"anthropic"
- `api_key` (str): API 密钥
- `api_base` (str, 可选): API 基础 URL

**返回:**

- JSON 格式的配置结果，包含密钥预览和配置文件路径

**示例:**

```python
# 设置 OpenAI API
result = subagent_config_set(
    provider="openai",
    api_key="sk-proj-xxxxxxxxxxxxxxxxxxxx"
)

# 设置自定义端点
result = subagent_config_set(
    provider="openai",
    api_key="sk-xxxx",
    api_base="https://api.openai-proxy.com/v1"
)

# 设置 Anthropic
result = subagent_config_set(
    provider="anthropic",
    api_key="sk-ant-xxxxxxxxxxxx"
)
```

### 2. subagent_config_get

获取指定提供商的配置信息（密钥已脱敏）。

**参数:**

- `provider` (str): 提供商名称

**返回:**

- JSON 格式的配置信息，包括：
  - 脱敏后的密钥预览
  - API 基础 URL
  - 配置来源（environment/config_file）
  - 配置文件路径

**示例:**

```python
# 查询 OpenAI 配置
config = subagent_config_get("openai")
print(config)
# {
#   "provider": "openai",
#   "configured": true,
#   "api_key": "sk-proj-...xxxx",
#   "api_base": "https://api.openai.com/v1",
#   "source": "config_file",
#   "config_file": "/home/user/.subagent_config.json",
#   "status": "success"
# }
```

### 3. subagent_config_list

列出所有已配置的提供商。

**参数:**

- 无

**返回:**

- JSON 格式的提供商列表，包含每个提供商的配置状态

**示例:**

```python
# 列出所有配置
providers = subagent_config_list()
print(providers)
# {
#   "providers": {
#     "openai": {
#       "api_key": "sk-proj-...xxxx",
#       "api_base": "https://api.openai.com/v1",
#       "source": "config_file"
#     },
#     "anthropic": {
#       "api_key": "sk-ant-...eQhJ",
#       "api_base": "https://api.anthropic.com/v1",
#       "source": "environment"
#     }
#   },
#   "total_configured": 2,
#   "config_file": "/home/user/.subagent_config.json",
#   "status": "success"
# }
```

## 使用示例

### 示例 1: 首次配置

```python
import json
from mcp_server.tools.subagent import subagent_config_set, subagent_config_list

# 配置 OpenAI
result = subagent_config_set(
    provider="openai",
    api_key="sk-proj-xxxxxxxxxxxxxxxx"
)
print(json.loads(result))

# 配置 Anthropic
result = subagent_config_set(
    provider="anthropic",
    api_key="sk-ant-xxxxxxxxxxxxxxxx"
)
print(json.loads(result))

# 查看所有配置
providers = subagent_config_list()
print(json.loads(providers))
```

### 示例 2: 使用自定义端点

```python
# 配置使用代理的 OpenAI
result = subagent_config_set(
    provider="openai",
    api_key="sk-proj-xxxx",
    api_base="https://my-proxy.com/openai/v1"
)

# 配置 Azure OpenAI
result = subagent_config_set(
    provider="openai",
    api_key="your-azure-key",
    api_base="https://your-resource.openai.azure.com/openai/deployments"
)
```

### 示例 3: 查询和验证配置

```python
import json
from mcp_server.tools.subagent import subagent_config_get, subagent_call

# 查询配置
config = json.loads(subagent_config_get("openai"))
print(f"OpenAI 配置来源: {config['source']}")
print(f"API 端点: {config['api_base']}")

# 测试调用
if config['configured']:
    # 使用配置的密钥进行测试调用
    task = json.dumps({
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello!"}]
    })
    result = subagent_call(task)
    print(result)
```

### 示例 4: 动态切换配置

```python
import os
import json
from mcp_server.tools.subagent import subagent_config_get, subagent_call

# 方案 A: 使用配置文件中的密钥
result = subagent_call(json.dumps({
    "provider": "openai",
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Using config file key"}]
}))

# 方案 B: 临时使用环境变量覆盖
os.environ["OPENAI_API_KEY"] = "sk-temp-xxxxxxxxxxxx"
result = subagent_call(json.dumps({
    "provider": "openai",
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Using env var key"}]
}))

# 验证当前使用的配置
config = json.loads(subagent_config_get("openai"))
print(f"Currently using: {config['source']}")  # "environment"
```

### 示例 5: 多项目配置管理

```python
from pathlib import Path
from mcp_server.tools.subagent_config import SubagentConfig

# 项目 A 使用自己的配置
config_a = SubagentConfig(config_path="./project_a_config.json")
config_a.set_api_key("openai", "sk-project-a-key")

# 项目 B 使用自己的配置
config_b = SubagentConfig(config_path="./project_b_config.json")
config_b.set_api_key("openai", "sk-project-b-key")

# 查看不同项目的配置
print(f"Project A: {config_a.get_api_key('openai')[:10]}...")
print(f"Project B: {config_b.get_api_key('openai')[:10]}...")
```

## 安全最佳实践

### 1. 文件权限

配置文件在 Unix/Linux/macOS 上自动设置为 `600` 权限（仅所有者可读写）：

```bash
ls -la ~/.subagent_config.json
# -rw------- 1 user user 234 Jan 15 10:30 .subagent_config.json
```

### 2. 不要提交配置文件

在 `.gitignore` 中添加：

```gitignore
.subagent_config.json
*_config.json
```

### 3. 使用环境变量（CI/CD）

在 CI/CD 环境中，推荐使用环境变量而非配置文件：

```yaml
# GitHub Actions 示例
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### 4. 定期轮换密钥

建议定期更新 API 密钥：

```python
# 更新密钥
subagent_config_set("openai", "sk-new-key")

# 验证更新
config = subagent_config_get("openai")
print(f"Key updated: {config['api_key']}")
```

### 5. 分离开发和生产配置

```python
import os

# 根据环境选择配置
if os.getenv("ENVIRONMENT") == "production":
    # 生产环境使用环境变量
    pass
else:
    # 开发环境使用配置文件
    from mcp_server.tools.subagent_config import init_config
    init_config("./dev_config.json")
```

## 常见问题

### Q1: 配置文件在哪里？

**A:** 使用 `subagent_config_list()` 查看配置文件路径：

```python
result = json.loads(subagent_config_list())
print(result['config_file'])
```

### Q2: 环境变量和配置文件哪个优先？

**A:** 环境变量优先级更高。如果同时设置了环境变量和配置文件，系统会使用环境变量的值。

### Q3: 如何删除某个提供商的配置？

**A:** 手动编辑配置文件，或使用代码：

```python
from mcp_server.tools.subagent_config import get_config

config = get_config()
config.remove_api_key("openai")
```

### Q4: 配置文件损坏怎么办？

**A:** 删除配置文件，系统会自动创建新的：

```bash
# Unix/Linux/macOS
rm ~/.subagent_config.json

# Windows
del %USERPROFILE%\.subagent_config.json
```

### Q5: 能否加密配置文件？

**A:** 当前版本不支持加密。建议使用操作系统的文件系统加密功能（如 BitLocker、FileVault）或密钥管理服务（如 AWS Secrets Manager）。

### Q6: 如何备份配置？

**A:** 使用导出功能：

```python
from mcp_server.tools.subagent_config import get_config

config = get_config()
backup = config.export_config()
with open("config_backup.json", "w") as f:
    f.write(backup)
```

### Q7: 支持团队共享配置吗？

**A:** 不推荐共享配置文件。建议每个用户：

- 使用自己的 API 密钥
- 在团队文档中标准化 API 端点设置
- 通过环境变量管理密钥

### Q8: 如何迁移到新电脑？

**A:** 复制配置文件到新电脑的对应位置：

```bash
# 从旧电脑
scp ~/.subagent_config.json user@newpc:~/

# 或手动重新配置
python -c "
from mcp_server.tools.subagent import subagent_config_set
subagent_config_set('openai', 'your-key')
"
```

## 总结

Subagent 的配置管理系统提供了：

- 🔒 **安全** - 自动文件权限控制和密钥脱敏
- 🚀 **便捷** - 一次配置，永久生效
- 🔄 **灵活** - 支持环境变量覆盖和自定义端点
- 📊 **透明** - 清晰显示配置来源和状态

无论是个人开发还是团队协作，都能找到适合的配置方案！

---

**相关文档:**

- [Subagent 使用指南](SUBAGENT_GUIDE.zh.md)
- [API 参考文档](SUBAGENT_GUIDE.zh.md)
