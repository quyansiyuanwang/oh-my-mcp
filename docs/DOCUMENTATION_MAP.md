# 📚 快速文档导航

快速找到您需要的文档！

## 🎯 我想...

### 开始使用

- **首次安装** → [SETUP_GUIDE.md](SETUP_GUIDE.md) - 交互式配置向导
- **快速安装** → [INSTALLATION.md](INSTALLATION.md) - 基本安装步骤
- **配置 Claude Desktop** → [CONFIGURATION_GUIDE_CN.md](CONFIGURATION_GUIDE_CN.md)
- **查看所有工具** → [README.md](../README.md#工具列表) - 104+ 工具说明

### 打包部署

- **打包为可执行文件** → [BUILD.md](BUILD.md) - Windows/Linux 打包指南
- **使用构建脚本** → `python build.py --help`
- **分发部署** → [BUILD.md#分发](BUILD.md#分发)

### 高级功能

- **使用 AI Subagent** → [SUBAGENT_GUIDE.md](SUBAGENT_GUIDE.md) - AI 编排功能
- **配置 AI 提供商** → [SUBAGENT_CONFIG.md](SUBAGENT_CONFIG.md)
- **集成智谱 AI** → [ZHIPUAI_GUIDE.md](ZHIPUAI_GUIDE.md)
- **搜索功能增强** → [SEARCH_UPGRADE.md](SEARCH_UPGRADE.md)

### 开发相关

- **了解项目结构** → [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **架构设计** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **贡献代码** → [CONTRIBUTING.md](CONTRIBUTING.md)
- **运行测试** → [TEST_REPORT.md](TEST_REPORT.md)

### 问题排查

- **查看日志** → `mcp_server.log` 文件
- **配置问题** → [CONFIGURATION_GUIDE_CN.md](docs/CONFIGURATION_GUIDE_CN.md)
- **构建问题** → [BUILD.md#故障排除](BUILD.md#故障排除)
- **提交问题** → [GitHub Issues](https://github.com/quyansiyuanwang/mcp-server/issues)

## 📂 按文档类型

### 用户文档（中文）

📁 **docs/** 目录

- [README.md](docs/README.md) - 文档索引
- [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - 设置指南
- [CONFIGURATION_GUIDE_CN.md](docs/CONFIGURATION_GUIDE_CN.md) - 完整配置
- [CONFIGURE_CN.md](docs/CONFIGURE_CN.md) - configure.py 使用
- [INSTALLATION.md](docs/INSTALLATION.md) - 安装说明

### 开发文档（中英混合）

📄 **根目录**

- [README.md](../README.md) - 项目主文档（英文）

📁 **docs/** 目录

- [BUILD.md](BUILD.md) - 构建指南（中英）
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南

### 技术文档（中文）

📁 **docs/** 目录

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 项目结构
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构设计
- [TEST_REPORT.md](docs/TEST_REPORT.md) - 测试报告

### 功能文档（中文）

📁 **docs/** 目录

- [SUBAGENT_GUIDE.md](docs/SUBAGENT_GUIDE.md) - Subagent 使用
- [SUBAGENT_CONFIG.md](docs/SUBAGENT_CONFIG.md) - Subagent 配置
- [ZHIPUAI_GUIDE.md](docs/ZHIPUAI_GUIDE.md) - 智谱 AI
- [SEARCH_UPGRADE.md](docs/SEARCH_UPGRADE.md) - 搜索升级
- [SEARCH_ADVANCED.md](docs/SEARCH_ADVANCED.md) - 高级搜索

## 🔍 按使用场景

### 场景 1: 我是新用户

1. 阅读 [README.md](README.md) 了解项目
2. 运行 `uv run configure.py` 交互式配置
3. 参考 [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) 详细步骤
4. 查看 [README.md#工具列表](README.md) 了解可用工具

### 场景 2: 我想打包部署

1. 查看 [BUILD.md](BUILD.md) 构建指南
2. 运行 `python build.py` 或 `python build.py --onefile`
3. 测试构建的可执行文件
4. 参考 BUILD.md 配置 Claude Desktop

### 场景 3: 我想使用 AI 功能

1. 阅读 [SUBAGENT_GUIDE.md](SUBAGENT_GUIDE.md) 了解功能
2. 配置 API 密钥 [SUBAGENT_CONFIG.md](SUBAGENT_CONFIG.md)
3. 查看示例 `examples/subagent_usage_example.py`
4. （可选）集成智谱 AI [ZHIPUAI_GUIDE.md](ZHIPUAI_GUIDE.md)

### 场景 4: 我想开发新功能

1. 了解项目结构 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
2. 阅读架构设计 [ARCHITECTURE.md](ARCHITECTURE.md)
3. 参考贡献指南 [CONTRIBUTING.md](CONTRIBUTING.md)
4. 运行测试 `pytest tests/`

### 场景 5: 我遇到了问题

1. 检查 `mcp_server.log` 日志文件
2. 查看相关文档的"故障排除"部分
3. 搜索 [GitHub Issues](https://github.com/quyansiyuanwang/mcp-server/issues)
4. 提交新的 Issue（包含日志和错误信息）

## 📊 文档完整列表

### 根目录文档

```
README.md                      # 主文档（英文）
LICENSE                        # MIT 许可证
```

### docs/ 目录文档

```
README.md                      # 文档索引（中文）
PROJECT_STRUCTURE.md           # 项目结构
DOCUMENTATION_MAP.md           # 文档导航（本文档）
ARCHITECTURE.md                # 架构设计
BUILD.md                       # 构建指南
CHANGELOG.md                   # 更新日志
CONTRIBUTING.md                # 贡献指南
INSTALLATION.md                # 安装指南
SETUP_GUIDE.md                 # 设置指南
CONFIGURATION_GUIDE_CN.md      # 完整配置
CONFIGURE_CN.md                # configure.py 使用
CONFIG_UPDATE.md               # 配置更新
SUBAGENT_CONFIG.md             # Subagent 配置
SUBAGENT_GUIDE.md              # Subagent 使用
SUBAGENT_ENABLE_UPDATE.md      # Subagent 启用更新
ZHIPUAI_GUIDE.md               # 智谱 AI 指南
SEARCH_UPGRADE.md              # 搜索升级
SEARCH_ADVANCED.md             # 高级搜索
TEST_REPORT.md                 # 测试报告
CLEANUP_2026-02-11.md          # 根目录整理总结
PROJECT_REORGANIZATION.md      # 项目重整总结
```

## 🎯 推荐阅读路径

### 路径 1: 快速上手（15分钟）

1. README.md → 项目概览
2. SETUP_GUIDE.md → 配置向导
3. 运行 configure.py
4. 开始使用！

### 路径 2: 完整了解（1小时）

1. README.md → 项目概览
2. PROJECT_STRUCTURE.md → 项目组织
3. ARCHITECTURE.md → 架构设计
4. CONFIGURATION_GUIDE_CN.md → 详细配置
5. 工具文档各个模块

### 路径 3: 开发者（2小时）

1. README.md → 项目概览
2. PROJECT_STRUCTURE.md → 项目结构
3. ARCHITECTURE.md → 架构设计
4. 示例代码 examples/
5. 测试代码 tests/

### 路径 4: 部署者（30分钟）

1. BUILD.md → 构建指南
2. 运行 build.py
3. 测试构建
4. 配置 Claude Desktop

## 💡 文档使用技巧

1. **⌨️ 快捷键**: 在 GitHub 上按 `T` 快速搜索文件
2. **🔍 搜索**: 使用仓库搜索功能查找关键词
3. **📱 移动端**: 文档使用 Markdown，移动端友好
4. **🌐 在线浏览**: 访问 GitHub 仓库在线阅读
5. **📥 离线阅读**: 克隆仓库本地查看

## 🔗 相关链接

- [GitHub 仓库](https://github.com/quyansiyuanwang/mcp-server)
- [问题追踪](https://github.com/quyansiyuanwang/mcp-server/issues)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [MCP 协议](https://modelcontextprotocol.io/)

---

**提示**: 如果找不到需要的文档，可以：

1. 查看 [docs/README.md](docs/README.md) 文档索引
2. 搜索 GitHub 仓库
3. 提交 Issue 询问

**最后更新**: 2026-02-11
