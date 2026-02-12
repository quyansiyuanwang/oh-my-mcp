# MCP Server 项目结构

本文档详细说明 MCP Server 的项目组织结构。

## 📁 目录结构

```
mcp-server/
│
├── 📂 src/                          # 源代码目录
│   └── mcp_server/
│       ├── __init__.py              # 📦 包初始化（版本号）
│       ├── main.py                  # 🚀 服务器主入口
│       ├── utils.py                 # 🛠️ 共享工具和基础设施
│       ├── command_executor.py      # 🔒 安全命令执行器
│       │
│       ├── 📂 cli/                  # 命令行工具
│       │   ├── __init__.py
│       │   └── config.py            # ⚙️ 配置生成器
│       │
│       └── 📂 tools/                # 工具插件目录 (8 个类别)
│           ├── __init__.py          # 🔍 插件自动发现
│           ├── registry.py          # 📋 @tool_handler 装饰器与 ToolPlugin
│           ├── search_engine.py     # 🔎 搜索引擎后端
│           ├── subagent_config.py   # ⚙️ Subagent 配置管理器
│           │
│           ├── 📂 compression/      # 📦 压缩工具 (5 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 web/              # 🌐 网络工具 (18 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 file/             # 📁 文件系统 (12 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 data/             # 📊 数据处理 (15 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 text/             # 📝 文本处理 (9 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 system/           # 💻 系统工具 (8 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 utility/          # 🛠️ 实用工具 (10 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           └── 📂 subagent/         # 🤖 AI 编排 (6 tools)
│               ├── __init__.py
│               ├── config.yaml
│               └── handlers.py
│
├── 📂 docs/                         # 📚 文档目录
│   ├── README.md                    # 文档索引
│   ├── 📂 en/                       # 英文/通用文档
│   │   ├── ARCHITECTURE.md          # 架构设计
│   │   ├── BUILD.md                 # 构建指南
│   │   ├── CHANGELOG.md             # 更新日志
│   │   ├── CONTRIBUTING.md          # 贡献指南
│   │   ├── INSTALLATION.md          # 安装指南
│   │   └── PROJECT_STRUCTURE.md     # 项目结构（本文档）
│   └── 📂 zh/                       # 中文文档
│       ├── CONFIGURATION_GUIDE_CN.md # 配置指南
│       ├── SEARCH_ADVANCED.md       # 高级搜索
│       ├── SETUP_GUIDE.md           # 设置向导
│       ├── SUBAGENT_CONFIG.md       # Subagent 配置
│       └── SUBAGENT_GUIDE.md        # Subagent 使用指南
│
├── 📂 tests/                        # 🧪 测试套件
│   ├── conftest.py                  # pytest 配置
│   ├── test_*.py                    # 测试文件
│   └── fixtures/                    # 测试数据
│       ├── sample_archives/         # 压缩文件示例
│       └── sample_files/            # 文件示例
│
├── 📂 examples/                     # 💡 使用示例
│   ├── README.md                    # 示例说明
│   ├── basic_usage.py               # 基本使用
│   ├── file_operations_example.py   # 文件操作
│   ├── web_search_example.py        # 网络搜索
│   ├── subagent_usage_example.py    # Subagent 使用
│   └── subagent_config_example.py   # Subagent 配置
│
├── 📂 scripts/                      # 🔧 脚本工具
│   └── build/                       # 🏗️ 构建脚本
│       ├── build.py                 # 跨平台构建脚本
│       ├── build.bat                # Windows 构建
│       └── build.sh                 # Linux/macOS 构建
│
├── 🔧 配置文件
│   ├── pyproject.toml               # 📦 项目配置和依赖
│   ├── pytest.ini                   # 🧪 pytest 配置
│   ├── mcp-server.spec              # 📦 PyInstaller 配置
│   ├── uv.lock                      # 🔒 UV 依赖锁定
│   ├── .python-version              # 🐍 Python 版本
│   └── configure.py                 # ⚙️ 交互式配置向导
│
├── 📄 根目录文档
│   ├── README.md                    # 📖 项目主文档
│   ├── CLAUDE.md                    # 🤖 Claude Code 开发指南
│   └── LICENSE                      # ⚖️ MIT 许可证
│
└── 🔨 开发环境
    ├── .venv/                       # 虚拟环境（本地）
    ├── .git/                        # Git 仓库
    ├── .gitignore                   # Git 忽略配置
    ├── .ruff_cache/                 # Ruff linter 缓存
    └── .pytest_cache/               # pytest 缓存
```

## 📊 代码组织

### 核心模块

#### 1. **main.py** - 服务器入口

```python
# 功能：
- FastMCP 服务器初始化
- 通过 load_all_plugins() 自动发现并加载所有工具插件
- 调用 plugin.register_to_mcp(mcp) 注册工具
- 注册 MCP 资源
- 启动服务器
```

#### 2. **utils.py** - 基础设施

```python
# 提供：
- 日志系统配置
- 自定义异常类
- 输入验证工具
- 重试装饰器
- 安全文件操作
```

#### 3. **command_executor.py** - 命令执行

```python
# 功能：
- 命令白名单验证
- 参数安全检查
- 超时保护
- 输出大小限制
- 审计日志
```

### 工具插件

每个工具插件遵循统一结构：

```yaml
# config.yaml
category_name: "类别名称"
category_description: "简短描述"
enabled: true
```

```python
# handlers.py
from mcp_server.tools.registry import tool_handler

@tool_handler
def tool_name(param: str) -> str:
    """工具描述"""
    # 实现...
```

插件由 `tools/__init__.py` 自动发现——无需修改 `main.py`。

### CLI 工具

#### config.py

- 生成 MCP 配置 JSON
- HTTP 配置服务器
- 自动检测 Claude Desktop
- 配置合并和验证

## 📦 依赖管理

### 核心依赖

```toml
dependencies = [
    "fastmcp>=2.14.5",      # MCP 服务器框架
    "requests>=2.31.0",     # HTTP 客户端
    "beautifulsoup4>=4.12.0", # HTML 解析
    "ddgs>=1.0.0",          # DuckDuckGo 搜索
    "python-dateutil>=2.8.2", # 日期时间
    "psutil>=5.9.0",        # 系统监控
    "lxml>=5.0.0",          # XML 处理
    "pyyaml>=6.0",          # YAML 支持
    "tomli>=2.0.0",         # TOML 支持
    "pyinstaller>=6.18.0",  # 打包工具
]
```

### 开发依赖

```toml
dev = [
    "pytest>=7.0",          # 测试框架
    "pytest-cov>=4.0",      # 代码覆盖率
    "black>=23.0",          # 代码格式化
    "ruff>=0.1.0",          # Linting
    "isort>=5.12.0",        # 导入排序
    "mypy>=1.0.0",          # 静态类型检查
]
```

## 🔨 构建系统

### 构建流程

```bash
# 1. 清理旧文件
python scripts/build/build.py --clean

# 2. 构建
python scripts/build/build.py

# 3. 单文件构建
python scripts/build/build.py --onefile

# 4. 测试构建
./dist/mcp-server/mcp-server
```

## 📝 文档组织

### 文档类型

| 文档                     | 用途     | 位置       |
| ------------------------ | -------- | ---------- |
| README.md                | 项目概览 | 根目录     |
| CLAUDE.md                | 开发指南 | 根目录     |
| docs/en/ARCHITECTURE.md  | 架构设计 | docs/en/   |
| docs/en/BUILD.md         | 构建指南 | docs/en/   |
| docs/en/INSTALLATION.md  | 安装说明 | docs/en/   |
| docs/zh/SETUP_GUIDE.md   | 配置向导 | docs/zh/   |
| docs/zh/SUBAGENT_GUIDE.md| AI 功能  | docs/zh/   |

## 🧪 测试结构

```
tests/
├── conftest.py              # 共享 fixtures
├── test_compression.py      # 压缩工具测试
├── test_web.py              # 网络工具测试
├── test_file.py             # 文件工具测试
├── test_text.py             # 文本处理测试
├── test_system.py           # 系统工具测试
├── test_utility.py          # 实用工具测试
├── test_subagent.py         # Subagent 测试
└── test_subagent_no_billing.py # Subagent 无计费测试
```

## 💡 使用场景

### 开发场景

1. **添加新工具** → 在 `src/mcp_server/tools/<category>/handlers.py` 中添加 `@tool_handler` 函数
2. **添加新类别** → 创建 `src/mcp_server/tools/new_category/` 目录（含 config.yaml + handlers.py）
3. **修改配置** → 编辑 `pyproject.toml` 或 `configure.py`
4. **运行测试** → `pytest tests/`
5. **格式化代码** → `black src/ tests/`

### 部署场景

1. **本地开发** → `python -m mcp_server.main`
2. **Claude Desktop** → `python -m mcp_server.cli.config --claude`
3. **打包分发** → `python scripts/build/build.py --onefile`
4. **HTTP 服务** → `python -m mcp_server.cli.config --http-server`

## 🔍 查找文件

### 按功能查找

| 需求     | 位置                                                                          |
| -------- | ----------------------------------------------------------------------------- |
| 工具实现 | `src/mcp_server/tools/*/handlers.py`                                          |
| 插件配置 | `src/mcp_server/tools/*/config.yaml`                                          |
| 配置脚本 | `configure.py`, `src/mcp_server/cli/config.py`                                |
| 构建脚本 | `scripts/build/build.py`, `scripts/build/build.bat`, `scripts/build/build.sh` |
| 测试文件 | `tests/test_*.py`                                                             |
| 示例代码 | `examples/*.py`                                                               |

### 按任务查找

| 任务       | 查看文件                                         |
| ---------- | ------------------------------------------------ |
| 快速开始   | `README.md`, `docs/zh/SETUP_GUIDE.md`            |
| 配置向导   | `configure.py`, `docs/zh/CONFIGURATION_GUIDE_CN.md` |
| 打包部署   | `docs/en/BUILD.md`, `scripts/build/build.py`     |
| 开发新功能 | `CLAUDE.md`, `docs/en/ARCHITECTURE.md`           |
| AI 集成    | `docs/zh/SUBAGENT_GUIDE.md`                      |
| 故障排查   | `mcp_server.log`, 测试文件                       |

## 🎯 最佳实践

### 代码组织

- ✅ 每个工具类别一个插件目录
- ✅ 统一的错误处理模式
- ✅ 完整的类型注解
- ✅ 详细的文档字符串

### 文档维护

- ✅ 代码变动时更新文档
- ✅ 新功能必须有示例
- ✅ 关键文档提供双语
- ✅ 保持文档同步

### 测试覆盖

- ✅ 每个工具有对应测试
- ✅ 测试成功和失败场景
- ✅ 使用 fixtures 共享数据
- ✅ 保持测试独立性

## 📚 相关文档

- [README.md](../../README.md) - 项目主文档
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计
- [BUILD.md](BUILD.md) - 构建指南
- [docs/README.md](../README.md) - 文档索引

---

**最后更新**: 2026-02-12
**版本**: 0.1.0
