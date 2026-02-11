# MCP Server 文档

欢迎来到 MCP Server 文档！这里包含了项目的完整文档。

## 📚 文档导航

### 🚀 快速开始

- [**设置指南**](SETUP_GUIDE.md) - 交互式配置向导，推荐初次使用
- [**安装指南**](INSTALLATION.md) - 详细的安装步骤
- [**配置指南（中文）**](CONFIGURATION_GUIDE_CN.md) - 完整配置说明
- [**构建指南**](../BUILD.md) - 打包为可执行文件（Windows/Linux）

### 🔧 配置与部署

- [**配置向导（中文）**](CONFIGURE_CN.md) - configure.py 使用说明
- [**Subagent 配置**](SUBAGENT_CONFIG.md) - AI 子任务配置指南
- [**Subagent 使用指南**](SUBAGENT_GUIDE.md) - AI 编排功能详解
- [**智谱 AI 指南**](ZHIPUAI_GUIDE.md) - 智谱 AI (GLM) 集成

### 📖 深入了解

- [**架构概述**](ARCHITECTURE.md) - 项目架构和设计理念
- [**测试报告**](TEST_REPORT.md) - 测试覆盖率和结果

### 🔍 高级功能

- [**搜索引擎升级**](SEARCH_UPGRADE.md) - 搜索功能增强
- [**高级搜索**](SEARCH_ADVANCED.md) - 搜索引擎高级用法
- [**配置更新**](CONFIG_UPDATE.md) - 配置系统更新说明
- [**Subagent 启用更新**](../SUBAGENT_ENABLE_UPDATE.md) - Subagent 功能启用

## 🛠️ 工具分类

MCP Server 提供 **86 个实用工具**，分为 **8 个类别**：

> **注意：** Python Development、UV Package Manager 和 Pylance/Pyright 工具已从打包版本中移除，因为它们需要外部的Python解释器和包管理器。所有剩余工具均完全独立工作。

### 1. 📦 压缩工具 (5 工具)

- ZIP/TAR 压缩和解压缩
- 安全特性：ZIP 炸弹防护、路径遍历防护
- 支持多种压缩级别

### 2. 🌐 Web & Network (15 工具)

- DuckDuckGo 新闻搜索（无需 API key）
- 网页抓取和 HTML 解析
- HTTP 客户端和 API 请求
- DNS 查询和网络诊断
- 文件下载

### 3. 📁 File System (12 工具)

- 文件读写、追加操作
- 目录管理和搜索
- 文件比较和 diff
- 安全的路径处理

### 4. 📊 Data Processing (15 工具)

- JSON：解析、格式化、查询、合并
- CSV：解析和转换
- XML/YAML/TOML：多格式支持
- 数据验证和转换

### 5. 📝 Text Processing (9 工具)

- 正则表达式操作
- Base64 编码/解码
- 邮件和 URL 提取
- 文本相似度分析
- 文本摘要

### 6. 💻 System (8 工具)

- 系统信息获取
- CPU/内存/磁盘监控
- 环境变量管理
- 进程列表
- 网络接口信息

### 7. 🛠️ Utilities (10 工具)

- UUID 和随机字符串生成
- 密码生成和强度检查
- 哈希计算（MD5/SHA1/SHA256/SHA512）
- 数学表达式求值
- 日期时间操作

### 8. 🤖 Subagent AI Orchestration (6 工具) ⭐ NEW

- AI 任务委派（OpenAI/Anthropic/ZhipuAI）
- 并行任务执行
- 条件分支决策
- Token 使用追踪
- 成本估算
- 持久化配置管理

## 📂 项目结构

```
mcp-server/
├── src/mcp_server/          # 源代码
│   ├── main.py              # 服务器入口
│   ├── utils.py             # 共享工具
│   ├── command_executor.py  # 命令执行器
│   ├── cli/                 # 命令行工具
│   │   └── config.py        # 配置生成器
│   └── tools/               # 工具模块
│       ├── compression.py   # 压缩工具
│       ├── web.py           # 网络工具
│       ├── file.py          # 文件工具
│       ├── data.py          # 数据处理
│       ├── text.py          # 文本处理
│       ├── system.py        # 系统工具
│       ├── utility.py       # 实用工具
│       ├── subagent.py      # AI 编排
│       └── subagent_config.py # Subagent 配置
├── docs/                    # 文档目录（本目录）
├── tests/                   # 测试套件
├── examples/                # 使用示例
├── build.py                 # 跨平台构建脚本
├── build.bat                # Windows 构建脚本
├── build.sh                 # Linux/macOS 构建脚本
├── configure.py             # 交互式配置向导
├── pyproject.toml           # 项目配置
└── README.md                # 项目主文档
```

## 🔗 快速链接

### 仓库

- [GitHub 仓库](https://github.com/quyansiyuanwang/mcp-server)
- [问题追踪](https://github.com/quyansiyuanwang/mcp-server/issues)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)

### 外部资源

- [FastMCP 框架](https://github.com/jlowin/fastmcp)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/)

## 💡 使用提示

1. **首次使用**：运行 `uv run configure.py` 进行交互式配置
2. **打包部署**：使用 `python scripts/build/build.py` 构建可执行文件
3. **开发调试**：查看 [ARCHITECTURE.md](ARCHITECTURE.md) 了解项目架构
4. **AI 功能**：参考 [SUBAGENT_GUIDE.md](SUBAGENT_GUIDE.md) 配置 AI 子任务
5. **问题排查**：检查 `mcp_server.log` 日志文件

## 📞 获取帮助

- 📖 查看相关文档
- 🐛 [提交 Issue](https://github.com/quyansiyuanwang/mcp-server/issues)
- 💬 查看已有的问题和讨论
- 📧 联系维护者：qysyw-team@qq.com
