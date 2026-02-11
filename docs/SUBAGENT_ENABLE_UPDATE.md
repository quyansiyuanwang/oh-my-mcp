# Subagent 启用/禁用功能更新

## 📋 更新内容

添加了全局配置选项，允许用户控制是否启用 Subagent 功能。

## 🎯 新增功能

### 1. 配置文件支持

在 `~/.subagent_config.json` 中新增 `enable_subagent` 字段：

```json
{
  "enable_subagent": true,
  "api_keys": { ... },
  "api_bases": { ... }
}
```

### 2. SubagentConfig 新增方法

- `get_enable_subagent()` - 获取启用状态（默认 true）
- `set_enable_subagent(enabled: bool)` - 设置启用状态

**优先级：** 环境变量 > 配置文件 > 默认值

### 3. 环境变量支持

```bash
# 启用（Windows PowerShell）
$env:ENABLE_SUBAGENT = "true"

# 禁用（Windows PowerShell）
$env:ENABLE_SUBAGENT = "false"

# Linux/macOS
export ENABLE_SUBAGENT=true
export ENABLE_SUBAGENT=false
```

### 4. 交互式配置增强

在 `Stage 3` 中新增询问：

```
Stage 3: Configure Subagent Feature
====================================
Subagent allows Claude to delegate complex tasks to other AI models.
This feature requires API credentials from AI providers (OpenAI/Anthropic/ZhipuAI).

Enable Subagent feature? (y/n):
```

- 选择 `y` - 启用并继续配置 API
- 选择 `n` - 禁用并跳过 API 配置

### 5. 命令行参数

新增互斥参数组：

```bash
# 启用 Subagent
uv run configure.py --enable-subagent --skip-deps --skip-claude

# 禁用 Subagent
uv run configure.py --disable-subagent --skip-deps --skip-claude

# 配置提供商时自动启用
uv run configure.py --provider openai --api-key sk-xxx
```

### 6. 配置摘要显示

`show_config_summary()` 现在显示 Subagent 状态：

```
Configuration Summary
=====================

Subagent Configuration:
  Config file: ~/.subagent_config.json
  Status: ENABLED

  v Anthropic:
      API Key: sk-a...xxx
      API Base: https://api.anthropic.com/v1
```

禁用时：

```
Configuration Summary
=====================

Subagent Configuration:
  Config file: ~/.subagent_config.json
  Status: DISABLED
[WARN]   Subagent is disabled - AI delegation features will not work
[INFO]   Enable it by running: uv run configure.py
```

## 📚 更新文档

### 1. SETUP_GUIDE.md

新增 "3. 启用/禁用 Subagent 功能" 章节，包含：

- 功能说明
- 禁用理由（隐私、成本、简化）
- 交互式和命令行配置方式
- 配置文件和环境变量说明

### 2. CONFIGURE_CN.md

新增 "🔌 Subagent 功能说明" 章节（中文），包含：

- Subagent 简介
- 禁用理由
- 控制方式（交互/命令行/环境变量）

## 🧪 测试结果

所有功能均已测试通过：

✅ 禁用 Subagent

```bash
uv run configure.py --disable-subagent --skip-deps --skip-claude
# 结果: Status: DISABLED
```

✅ 启用 Subagent

```bash
uv run configure.py --enable-subagent --skip-deps --skip-claude
# 结果: Status: ENABLED
```

✅ 配置文件正确保存

```json
{
  "enable_subagent": true,
  "api_keys": { "anthropic": "..." },
  "api_bases": { "anthropic": "..." }
}
```

✅ 配置摘要正确显示状态

✅ 帮助信息包含新参数

## 🎨 用户体验改进

1. **灵活控制** - 用户可以选择是否使用外部 AI 服务
2. **隐私保护** - 明确告知数据将发送到外部 API
3. **成本意识** - 用户可以禁用以避免 API 费用
4. **清晰提示** - 配置状态一目了然
5. **多种方式** - 支持交互式、命令行、环境变量三种配置方式

## 📝 使用场景

### 场景 1: 隐私第一用户

只想使用本地 MCP 工具，不希望数据发送到外部：

```bash
uv run configure.py --disable-subagent
```

### 场景 2: 功能探索用户

先禁用，之后需要时再启用：

```bash
# 初始配置时禁用
uv run configure.py --disable-subagent

# 之后需要时启用并配置
uv run configure.py --enable-subagent --provider openai --api-key sk-xxx
```

### 场景 3: 完整功能用户

使用所有功能，启用 Subagent：

```bash
uv run configure.py --provider openai --api-key sk-xxx
# 自动启用 Subagent
```

### 场景 4: 临时禁用

通过环境变量临时禁用，无需修改配置文件：

```bash
$env:ENABLE_SUBAGENT = "false"
# 运行 MCP 服务器，Subagent 功能被禁用
```

## 🔄 兼容性

- ✅ 向后兼容：未设置 `enable_subagent` 时默认启用（保持原有行为）
- ✅ 不影响现有配置文件
- ✅ 环境变量优先级最高，便于临时调整

## 📦 相关文件

### 修改的文件：

1. `src/mcp_server/tools/subagent_config.py`
   - 新增 `get_enable_subagent()` 方法
   - 新增 `set_enable_subagent()` 方法

2. `configure.py`
   - 更新交互式配置流程（Stage 3）
   - 新增命令行参数 `--enable-subagent` / `--disable-subagent`
   - 更新 `show_config_summary()` 显示状态
   - 更新 `noninteractive_setup()` 处理新参数

3. `docs/SETUP_GUIDE.md`
   - 新增 "3. 启用/禁用 Subagent 功能" 章节
   - 更新配置步骤说明
   - 更新示例代码

4. `docs/CONFIGURE_CN.md`
   - 新增 "🔌 Subagent 功能说明" 章节
   - 更新配置流程说明
   - 新增中文使用示例

## ✨ 总结

此更新为 MCP Server 提供了更灵活的配置选项，用户可以根据自己的需求（隐私、成本、功能）选择是否启用 Subagent 功能，同时保持完全的向后兼容性。
