# 架构概述

本文档描述 MCP Server 的架构设计和实现细节。

## 项目结构

```
mcp-server/
├── src/mcp_server/              # 源代码
│   ├── main.py                  # 服务器入口点
│   ├── utils.py                 # 共享工具和基础设施
│   ├── command_executor.py      # 安全命令执行
│   ├── tools/                   # 工具插件目录
│   │   ├── __init__.py          # 插件自动发现
│   │   ├── registry.py          # @tool_handler 装饰器与 ToolPlugin 类
│   │   ├── search_engine.py     # 搜索引擎后端
│   │   ├── subagent_config.py   # Subagent 配置管理器
│   │   ├── compression/         # 压缩工具 (5 tools)
│   │   │   ├── config.yaml
│   │   │   └── handlers.py
│   │   ├── web/                 # 网络工具 (18 tools)
│   │   │   ├── config.yaml
│   │   │   └── handlers.py
│   │   ├── file/                # 文件系统 (12 tools)
│   │   │   ├── config.yaml
│   │   │   └── handlers.py
│   │   ├── data/                # 数据处理 (15 tools)
│   │   │   ├── config.yaml
│   │   │   └── handlers.py
│   │   ├── text/                # 文本处理 (9 tools)
│   │   │   ├── config.yaml
│   │   │   └── handlers.py
│   │   ├── system/              # 系统工具 (8 tools)
│   │   │   ├── config.yaml
│   │   │   └── handlers.py
│   │   ├── utility/             # 实用工具 (10 tools)
│   │   │   ├── config.yaml
│   │   │   └── handlers.py
│   │   └── subagent/            # AI 编排 (6 tools)
│   │       ├── config.yaml
│   │       └── handlers.py
│   └── cli/                     # 命令行工具
│       └── config.py            # 配置生成器
├── tests/                       # 测试套件
├── docs/                        # 文档
└── examples/                    # 示例代码
```

## 核心组件

### 1. FastMCP 服务器 (main.py)

服务器入口点，负责：

- 初始化 FastMCP 实例
- 通过 `load_all_plugins()` 自动发现并加载所有工具插件
- 调用 `plugin.register_to_mcp(mcp)` 注册工具
- 提供 MCP 资源（config://tools, config://version）
- 启动服务器

### 2. 插件注册框架 (tools/registry.py)

提供工具插件的注册基础设施：

- `@tool_handler` 装饰器：标记函数为工具处理器，自动注册到全局注册表
- `ToolPlugin` 类：表示一个工具插件，管理配置和处理器
- `load_plugin_config()`：加载插件的 `config.yaml` 配置

### 3. 工具插件 (tools/*/handlers.py)

每个工具插件遵循统一的模式：

```python
from mcp_server.tools.registry import tool_handler

@tool_handler
def tool_name(param: str) -> str:
    """工具描述"""
    try:
        # 实现逻辑
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        return json.dumps({"error": str(e)})
```

每个插件目录包含：

- `config.yaml` — 插件元数据（类别名、描述、启用状态）
- `handlers.py` — 使用 `@tool_handler` 装饰的工具函数
- `__init__.py` — 包标记

**关键特性**：

- 使用 `@tool_handler` 装饰器自动注册
- 统一的错误处理模式
- 返回 JSON 字符串
- 记录日志

### 4. 插件自动发现 (tools/__init__.py)

- `discover_tool_plugins()` — 扫描 tools/ 目录寻找含 `config.yaml` 的子目录
- `load_all_plugins()` — 加载所有启用的插件、导入 handlers 模块、返回 ToolPlugin 列表
- 支持 PyInstaller 打包模式

### 5. 基础设施 (utils.py)

提供共享功能：

**日志系统**：

- 双输出：控制台 + mcp_server.log
- INFO 级别日志
- 结构化日志格式

**自定义异常**：

- ValidationError
- NetworkError
- FileOperationError
- DataProcessingError
- CommandExecutionError
- SecurityError

**重试逻辑**：

- `@retry` 装饰器
- 网络操作自动重试（3次）
- 指数退避

**验证和安全**：

- URL 验证
- 路径清理
- 文件大小限制
- ZIP 炸弹防护
- 路径遍历防护

### 6. 命令执行器 (command_executor.py)

安全执行外部命令：

**CommandValidator**：

- 命令白名单（python, uv, pyright）
- 参数验证
- 危险模式检测

**CommandExecutor**：

- 使用 subprocess.run()（shell=False）
- 超时保护（默认 30s）
- 输出大小限制（10MB）
- 审计日志

## 设计原则

### 1. 插件化架构

每个工具类别是独立插件目录，便于：

- 维护和扩展
- 测试和调试
- 按需启用/禁用（config.yaml 中设置 enabled: false）
- 自动发现，无需修改 main.py

### 2. 安全性

多层安全措施：

- 命令白名单
- 参数验证
- 路径清理
- 资源限制
- 审计日志

### 3. 错误处理

统一的错误处理策略：

- Try-except 包装
- 详细错误日志
- 用户友好的错误消息
- JSON 格式返回

### 4. 可扩展性

易于添加新工具：

1. 创建新插件目录 `tools/new_category/`
2. 添加 `config.yaml`、`__init__.py`、`handlers.py`
3. 使用 `@tool_handler` 装饰器
4. 无需修改 main.py（自动发现）

## 数据流

```
用户请求 → FastMCP → 工具函数 → 业务逻辑 → 返回结果
                ↓
            日志记录
                ↓
            错误处理
```

## 性能考虑

- **缓存**: WebFetch 使用 15 分钟缓存
- **限制**: 文件大小、输出大小、超时限制
- **异步**: 使用 FastMCP 的异步支持
- **资源管理**: 自动清理临时文件

## 测试策略

- **单元测试**: 每个工具独立测试
- **集成测试**: 端到端场景测试
- **Fixtures**: 共享测试数据和配置
- **覆盖率**: 目标 > 80%
