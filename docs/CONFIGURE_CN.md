# MCP Server 快速配置 (configure.py)

快速配置 MCP 服务器环境的交互式向导。

## 🚀 快速开始

### 一键配置（推荐）

```bash
uv run configure.py
```

### 或使用 Python

```bash
python configure.py
```

## 📋 配置内容

脚本会帮你自动完成：

1. ✅ **环境检查** - 验证 Python 3.12+ 和包管理器
2. 📦 **安装依赖** - 自动安装所有必需的包
3. 🔑 **配置 API** - 设置 AI 提供商密钥
   - OpenAI (GPT-4/3.5)
   - Anthropic (Claude)
   - ZhipuAI (智谱 AI)
4. 🔧 **Claude Desktop** - 自动集成到 Claude Desktop

## 💡 使用方式

### 交互式配置

直接运行，按提示操作：

```bash
uv run configure.py
```

### 命令行配置

如果已有 API Key，可以直接指定：

```bash
# 配置 OpenAI
uv run configure.py --provider openai --api-key sk-xxx

# 配置多个提供商
uv run configure.py \
  --provider openai --api-key sk-xxx \
  --provider anthropic --api-key sk-ant-xxx

# 跳过依赖安装
uv run configure.py --skip-deps

# 跳过 Claude Desktop 配置
uv run configure.py --skip-claude
```

## 📖 支持的 AI 提供商

| 提供商 | 说明 | 获取 API Key |
|--------|------|-------------|
| **OpenAI** | GPT-4, GPT-3.5 | [platform.openai.com](https://platform.openai.com/api-keys) |
| **Anthropic** | Claude 系列 | [console.anthropic.com](https://console.anthropic.com/settings/keys) |
| **ZhipuAI** | 智谱 AI (GLM) | [open.bigmodel.cn](https://open.bigmodel.cn) |

## 🔧 配置文件位置

- **Windows**: `C:\Users\你的用户名\.subagent_config.json`
- **macOS/Linux**: `~/.subagent_config.json`

## ✅ 验证配置

配置完成后，运行测试：

```bash
python examples/subagent_config_example.py
```

## 🔄 重新配置

要修改现有配置，重新运行脚本即可：

```bash
uv run configure.py
```

会覆盖之前的配置。

## ❓ 常见问题

### Python 版本不够？

项目需要 Python 3.12+。使用以下命令创建新环境：

```bash
# 使用 uv（推荐）
uv venv
.venv\Scripts\activate

# 或使用 conda
conda create -n mcp-server python=3.12
conda activate mcp-server
```

### 没有安装 uv？

两种方式：

1. **安装 uv（推荐）**:
   ```powershell
   # Windows PowerShell
   irm https://astral.sh/uv/install.ps1 | iex
   ```

2. **使用 Python 直接运行**:
   ```bash
   python configure.py
   ```

### 配置后 Claude Desktop 不生效？

确保：
1. ✅ 配置文件已正确生成
2. ✅ **重启了 Claude Desktop**（重要！）
3. ✅ Claude Desktop 版本支持 MCP

## 📚 完整文档

- [详细配置指南](./SETUP_GUIDE.md)（英文）
- [Subagent 使用指南](./SUBAGENT_GUIDE.md)
- [更多示例](../examples/)

## 🎯 下一步

1. 运行配置脚本
2. 测试配置
3. 重启 Claude Desktop
4. 开始使用 MCP 服务器！

---

**需要帮助？** 查看 [完整配置指南](./SETUP_GUIDE.md) 或 [Subagent 文档](./SUBAGENT_GUIDE.md)
