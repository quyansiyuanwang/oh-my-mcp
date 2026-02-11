# MCP Server 配置指南

本指南介绍如何使用 `configure.py` 脚本快速配置 MCP 服务器环境。

## 快速开始

### 交互式配置（推荐）

最简单的方式是运行交互式配置向导：

```bash
uv run configure.py
```

或使用 Python：

```bash
python configure.py
```

配置向导将引导你完成以下步骤：

1. **环境检查** - 验证 Python 版本和依赖工具
2. **安装依赖** - 自动安装项目依赖包
3. **启用/禁用 Subagent** - 选择是否启用 AI 任务委托功能
4. **配置 Subagent API** - 设置 AI 提供商的 API 密钥（如果启用）
5. **Claude Desktop 集成** - 配置 Claude Desktop 使用此 MCP 服务器

### 非交互式配置

如果已知配置参数，可以使用命令行参数直接配置：

```bash
# 启用 Subagent（不配置提供商）
uv run configure.py --enable-subagent --skip-deps --skip-claude

# 禁用 Subagent
uv run configure.py --disable-subagent --skip-deps --skip-claude

# 配置 OpenAI（自动启用 Subagent）
uv run configure.py --provider openai --api-key sk-xxx

# 配置多个提供商
uv run configure.py \
  --provider openai --api-key sk-xxx \
  --provider anthropic --api-key sk-ant-xxx

# 跳过依赖安装
uv run configure.py --skip-deps --provider openai --api-key sk-xxx

# 跳过 Claude Desktop 配置
uv run configure.py --skip-claude --provider openai --api-key sk-xxx
```

## 配置步骤详解

### 1. 环境检查

脚本会自动检查：

- ✅ Python 版本（需要 3.12+）
- ✅ 虚拟环境（推荐但非必需）
- ✅ 包管理器（pip 或 uv）

### 2. 安装依赖

支持两种安装方式：

- **uv**（推荐）- 更快的安装速度
- **pip** - 标准 Python 包管理器

跳过依赖安装：

```bash
uv run configure.py --skip-deps
```

### 3. 启用/禁用 Subagent 功能

Subagent 是一个可选功能，允许 Claude 将复杂任务委托给其他 AI 模型（如 OpenAI GPT、Anthropic Claude）。

#### 为什么要禁用 Subagent？

- **隐私考虑** - 不希望数据发送到外部 AI 服务
- **成本控制** - 避免产生额外的 API 调用费用
- **简化配置** - 只使用本地 MCP 工具，不需要外部 AI 集成

#### 交互式配置

在交互模式下，脚本会询问：

```
Enable Subagent feature? (y/n):
```

- 选择 `y` - 启用 Subagent，继续配置 API 密钥
- 选择 `n` - 禁用 Subagent，跳过 API 配置

#### 命令行配置

```bash
# 启用 Subagent
uv run configure.py --enable-subagent --skip-deps --skip-claude

# 禁用 Subagent
uv run configure.py --disable-subagent --skip-deps --skip-claude

# 配置提供商时自动启用
uv run configure.py --provider openai --api-key sk-xxx
```

#### 修改现有配置

随时可以通过重新运行脚本来修改设置：

```bash
# 从启用改为禁用
uv run configure.py --disable-subagent --skip-deps --skip-claude

# 从禁用改为启用
uv run configure.py --enable-subagent --skip-deps --skip-claude
```

#### 配置文件

Subagent 状态保存在配置文件中：

```json
{
  "enable_subagent": true,
  "api_keys": { ... },
  "api_bases": { ... }
}
```

#### 环境变量

也可以通过环境变量控制（优先级高于配置文件）：

```bash
# 启用
export ENABLE_SUBAGENT=true

# 禁用
export ENABLE_SUBAGENT=false
```

### 4. 配置 Subagent API

**注意：** 此步骤仅在启用 Subagent 功能时需要。

Subagent 允许 Claude 将复杂任务委托给其他 AI 模型。

#### 支持的 AI 提供商

| 提供商        | 说明                  | API Key 格式          | 文档                                            |
| ------------- | --------------------- | --------------------- | ----------------------------------------------- |
| **OpenAI**    | GPT-4, GPT-3.5 等模型 | `sk-...`              | [OpenAI Docs](https://platform.openai.com/docs) |
| **Anthropic** | Claude 模型           | `sk-ant-...`          | [Anthropic Docs](https://docs.anthropic.com)    |

#### 交互式配置

在交互模式下，脚本会：

1. 显示可用的提供商列表
2. 询问是否配置每个提供商
3. 安全地收集 API 密钥（隐藏输入）
4. 询问是否使用自定义 API Base（可选）

#### 非交互式配置

```bash
# 基本配置
uv run configure.py --provider openai --api-key YOUR_API_KEY

# 使用自定义 API Base
uv run configure.py \
  --provider openai \
  --api-key YOUR_API_KEY \
  --api-base https://custom-api.example.com/v1
```

#### 配置文件位置

API 配置保存在：

- **Windows**: `C:\Users\<用户名>\.subagent_config.json`
- **macOS/Linux**: `~/.subagent_config.json`

配置文件格式：

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

### 5. Claude Desktop 集成

脚本可以自动配置 Claude Desktop 使用此 MCP 服务器。

#### 自动检测

脚本会自动检测 Claude Desktop 配置文件位置：

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

#### 手动配置

如果选择跳过自动配置，可以稍后手动配置：

```bash
# 使用 CLI 工具配置
python -m mcp_server.cli.config --claude
```

#### 重启 Claude Desktop

配置完成后，**必须重启 Claude Desktop** 才能加载 MCP 服务器。

## 配置选项

### 命令行参数

| 参数            | 说明                     | 示例                                    |
| --------------- | ------------------------ | --------------------------------------- |
| `--provider`    | 指定 AI 提供商           | `--provider openai`                     |
| `--api-key`     | 提供商的 API 密钥        | `--api-key sk-xxx`                      |
| `--api-base`    | 自定义 API Base URL      | `--api-base https://api.example.com/v1` |
| `--skip-deps`   | 跳过依赖安装             | `--skip-deps`                           |
| `--skip-claude` | 跳过 Claude Desktop 配置 | `--skip-claude`                         |
| `--no-color`    | 禁用彩色输出             | `--no-color`                            |
| `-h, --help`    | 显示帮助信息             | `--help`                                |

### 多提供商配置

可以在一次运行中配置多个提供商：

```bash
uv run configure.py \
  --provider openai --api-key sk-openai-xxx \
  --provider anthropic --api-key sk-ant-xxx
```

**注意**：`--provider`、`--api-key` 和 `--api-base` 的顺序必须一致。

## 验证配置

### 1. 查看配置摘要

运行配置脚本后会显示配置摘要：

```
Configuration Summary
=====================

Subagent Configuration:
  Config file: ~/.subagent_config.json

  [OK] OpenAI:
      API Key: sk-xx...xxxx
      API Base: https://api.openai.com/v1
```

### 2. 测试配置

运行示例脚本测试配置：

```bash
python examples/subagent_config_example.py
```

### 3. 运行 MCP 服务器

```bash
mcp-server
```

## 常见问题

### Q: Python 版本过低怎么办？

**A**: 本项目需要 Python 3.12 或更高版本。请更新 Python 或使用 pyenv/conda 创建新环境。

### Q: 没有虚拟环境可以运行吗？

**A**: 可以，但强烈推荐使用虚拟环境以避免依赖冲突。

创建虚拟环境：

```bash
# 使用 venv
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 使用 uv（推荐）
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### Q: uv 和 pip 有什么区别？

**A**: uv 是更现代、更快的 Python 包管理器。脚本会优先使用 uv，如果不可用则使用 pip。

安装 uv：

```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Q: 如何修改已保存的配置？

**A**: 重新运行配置脚本即可覆盖现有配置：

```bash
uv run configure.py
```

或者直接编辑配置文件 `~/.subagent_config.json`。

### Q: 配置文件的权限设置？

**A**: 在 Unix 系统上，配置文件自动设置为 `0o600`（仅所有者可读写）以保护 API 密钥。

### Q: Claude Desktop 配置不生效？

**A**: 请确保：

1. 配置文件保存在正确的位置
2. JSON 格式正确（可以用 `python -m json.tool` 验证）
3. **已重启 Claude Desktop**

### Q: 如何获取 API Key？

**A**: 各提供商的 API Key 获取方式：

- **OpenAI**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

## 下一步

配置完成后，你可以：

1. **测试配置**

   ```bash
   python examples/subagent_config_example.py
   ```

2. **运行 MCP 服务器**

   ```bash
   mcp-server
   ```

3. **学习更多**
   - [Subagent 使用指南](./SUBAGENT_GUIDE.md)
   - [配置指南（中文）](./CONFIGURATION_GUIDE_CN.md)
   - [示例代码](../examples/)

4. **在 Claude Desktop 中使用**
   - 重启 Claude Desktop
   - 开始使用 MCP 服务器的强大功能！

## 高级用法

### 环境变量

配置优先级（从高到低）：

1. 环境变量
2. 配置文件 (`~/.subagent_config.json`)
3. 默认值

支持的环境变量：

```bash
# OpenAI
export OPENAI_API_KEY="sk-xxx"
export OPENAI_API_BASE="https://api.openai.com/v1"

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-xxx"
export ANTHROPIC_API_BASE="https://api.anthropic.com/v1"
```

### 编程方式配置

可以在 Python 代码中使用配置：

```python
from src.mcp_server.tools.subagent_config import get_config

# 获取配置实例
config = get_config()

# 设置 API Key
config.set_api_key("openai", "sk-xxx")

# 获取 API Key
api_key = config.get_api_key("openai")

# 设置自定义 API Base
config.set_api_base("openai", "https://custom-api.example.com/v1")
```

参考 [subagent_config_example.py](../examples/subagent_config_example.py) 了解更多。

## 故障排除

### 依赖安装失败

```bash
# 清理缓存后重试
pip cache purge
uv cache clean

# 手动安装
pip install -e .
# 或
uv pip install -e .
```

### 导入错误

确保依赖已安装：

```bash
uv run configure.py  # 不要跳过依赖安装
```

### 配置文件权限错误（Unix）

```bash
# 设置正确的权限
chmod 600 ~/.subagent_config.json
```

### Windows 编码问题

使用 `--no-color` 参数禁用彩色输出：

```bash
uv run configure.py --no-color
```

## 相关文档

- [主 README](../README.md)
- [安装指南](./INSTALLATION.md)
- [Subagent 配置指南](./SUBAGENT_CONFIG.md)
- [Subagent 使用指南](./SUBAGENT_GUIDE.md)
- [配置指南（中文）](./CONFIGURATION_GUIDE_CN.md)

## 支持

如有问题或建议，请：

- 查看 [文档目录](./README.md)
- 提交 [Issue](https://github.com/your-repo/mcp-server/issues)
- 参考 [示例代码](../examples/)
