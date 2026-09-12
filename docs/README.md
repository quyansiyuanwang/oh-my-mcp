# MCP Server Documentation | MCP 服务器文档

oh-my-mcp — **141 tools across 10 categories** | **141 个工具，10 个类别**

## 📚 Documentation by Topic | 按主题浏览

| Topic 主题 | English | 中文 |
|---|---|---|
| Installation 安装 | [en/INSTALLATION.md](en/INSTALLATION.md) | [zh/INSTALLATION.md](zh/INSTALLATION.md) |
| Setup Wizard 配置向导 | — | [zh/SETUP_GUIDE.md](zh/SETUP_GUIDE.md) |
| Configuration 配置 | — | [zh/CONFIGURATION_GUIDE_CN.md](zh/CONFIGURATION_GUIDE_CN.md) |
| Tool Reference 工具参考 | [en/TOOL_REFERENCE.md](en/TOOL_REFERENCE.md) 🤖 auto-generated | — |
| Computer Use 桌面控制 | [en/COMPUTER_USE_GUIDE.md](en/COMPUTER_USE_GUIDE.md) | [zh/COMPUTER_USE_GUIDE.md](zh/COMPUTER_USE_GUIDE.md) |
| Subagent Guide AI 编排 | — | [zh/SUBAGENT_GUIDE.md](zh/SUBAGENT_GUIDE.md) |
| Subagent Config AI 配置 | — | [zh/SUBAGENT_CONFIG.md](zh/SUBAGENT_CONFIG.md) |
| Browser Config 浏览器配置 | — | [zh/BROWSER_CONFIG_GUIDE.md](zh/BROWSER_CONFIG_GUIDE.md) / [Quickstart](zh/BROWSER_CONFIG_QUICKSTART.md) |
| Advanced Search 高级搜索 | — | [zh/SEARCH_ADVANCED.md](zh/SEARCH_ADVANCED.md) |
| Architecture 架构 | [en/ARCHITECTURE.md](en/ARCHITECTURE.md) | [zh/ARCHITECTURE.md](zh/ARCHITECTURE.md) |
| Project Structure 结构 | [en/PROJECT_STRUCTURE.md](en/PROJECT_STRUCTURE.md) | [zh/PROJECT_STRUCTURE.md](zh/PROJECT_STRUCTURE.md) |
| Build 打包 | [en/BUILD.md](en/BUILD.md) | [zh/BUILD.md](zh/BUILD.md) |
| Contributing 贡献 | [en/CONTRIBUTING.md](en/CONTRIBUTING.md) | [zh/CONTRIBUTING.md](zh/CONTRIBUTING.md) |
| Changelog 更新日志 | [en/CHANGELOG.md](en/CHANGELOG.md) | — |

> Entries marked "—" have no translation yet; contributions are welcome.
> 标注 "—" 的条目暂无翻译，欢迎贡献。

> 🤖 Auto-generated: tool counts and one-line descriptions in these docs are
> produced by `scripts/docs/generate_docs.py` from the code. After adding or
> removing tools, run it with `--write`; CI verifies freshness with `--check`.
> 🤖 自动生成：文档中的工具数量与描述由脚本从代码生成，增删工具后请运行
> `python scripts/docs/generate_docs.py --write`，CI 会用 `--check` 校验。

---

## 🚀 Quick Start | 快速开始

### 中文用户
1. 阅读 [设置指南](zh/SETUP_GUIDE.md)
2. 运行 `python configure.py` 进行配置
3. 查看 [Subagent 使用指南](zh/SUBAGENT_GUIDE.md) 使用 AI 功能

### English Users
1. Read [Installation Guide](en/INSTALLATION.md)
2. Run `python configure.py` for setup
3. Check the [Tool Reference](en/TOOL_REFERENCE.md) for the full tool list

---

## 📊 Tool Categories | 工具分类

<!-- DOCGEN:docs-categories:start -->
**141 practical tools across 10 categories:**

- **Browser Automation** (33 tools): Selenium-based browser automation
- **Compression** (5 tools): ZIP/TAR compression and extraction with security features
- **Computer Use** (25 tools): AI desktop control
- **Data Processing** (15 tools): JSON, CSV, XML, YAML, TOML parsing and manipulation
- **File System** (12 tools): Read, write, search files and directories, file comparison
- **Subagent AI Orchestration** (6 tools): Delegate subtasks to external AI models with parallel execution and cost tracking
- **System** (8 tools): System info, CPU/memory monitoring, environment variables
- **Text Processing** (9 tools): Regex, encoding, email/URL extraction, text similarity
- **Utilities** (10 tools): UUID, hashing, date/time operations, math, password generation
- **Web & Network** (18 tools): Web search, page fetching, HTML parsing, downloads, HTTP API client, DNS lookup
<!-- DOCGEN:docs-categories:end -->

---

## 📖 Documentation Structure | 文档结构

```
docs/
├── en/                              # English docs
│   ├── ARCHITECTURE.md                 # Architecture
│   ├── BUILD.md                        # Build guide
│   ├── CHANGELOG.md                    # Changelog
│   ├── COMPUTER_USE_GUIDE.md           # Computer use guide
│   ├── CONTRIBUTING.md                 # Contributing
│   ├── INSTALLATION.md                 # Installation
│   ├── PROJECT_STRUCTURE.md            # Project structure
│   └── TOOL_REFERENCE.md               # Tool reference (auto-generated)
├── zh/                              # 中文文档
│   ├── ARCHITECTURE.md                 # 架构概述
│   ├── BROWSER_CONFIG_GUIDE.md         # 浏览器配置指南
│   ├── BROWSER_CONFIG_QUICKSTART.md    # 浏览器配置快速开始
│   ├── BUILD.md                        # 构建指南
│   ├── COMPUTER_USE_GUIDE.md           # Computer Use 指南
│   ├── CONFIGURATION_GUIDE_CN.md       # 配置指南
│   ├── CONTRIBUTING.md                 # 贡献指南
│   ├── INSTALLATION.md                 # 安装指南
│   ├── PROJECT_STRUCTURE.md            # 项目结构
│   ├── SEARCH_ADVANCED.md              # 高级搜索
│   ├── SETUP_GUIDE.md                  # 设置指南
│   ├── SUBAGENT_CONFIG.md              # Subagent 配置
│   └── SUBAGENT_GUIDE.md               # Subagent 使用
└── README.md                        # This index file
```

---

## 🔗 External Links | 外部链接

- [GitHub Repository](https://github.com/quyansiyuanwang/oh-my-mcp)
- [MCP Protocol](https://modelcontextprotocol.io)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
