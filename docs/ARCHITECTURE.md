# 架构概述

本文档描述 MCP Server 的架构设计和实现细节。

## 项目结构

```
mcp-server/
├── src/mcp_server/          # 源代码
│   ├── main.py              # 服务器入口点
│   ├── utils.py             # 共享工具和基础设施
│   ├── command_executor.py  # 安全命令执行
│   ├── tools/               # 工具模块
│   │   ├── compression.py   # 压缩工具
│   │   ├── web.py           # 网络工具
│   │   ├── file.py          # 文件系统工具
│   │   ├── data.py          # 数据处理工具
│   │   ├── text.py          # 文本处理工具
│   │   ├── system.py        # 系统工具
│   │   ├── utility.py       # 实用工具
│   │   ├── python.py        # Python 开发工具
│   │   ├── uv.py            # UV 包管理工具
│   │   └── pylance.py       # Pylance/Pyright 工具
│   └── cli/                 # 命令行工具
│       └── config.py        # 配置生成器
├── tests/                   # 测试套件
├── docs/                    # 文档
└── examples/                # 示例代码
```

## 核心组件

### 1. FastMCP 服务器 (main.py)

服务器入口点，负责：

- 初始化 FastMCP 实例
- 注册所有工具模块
- 提供 MCP 资源（config://tools, config://version）
- 启动服务器

### 2. 工具模块 (tools/)

每个工具模块遵循统一的模式：

```python
def register_tools(mcp):
    """注册模块中的所有工具"""

    @mcp.tool()
    def tool_name(param: str) -> str:
        """工具描述"""
        try:
            # 实现逻辑
            return json.dumps(result)
        except Exception as e:
            logger.error(f"Tool failed: {e}")
            return json.dumps({"error": str(e)})
```

**关键特性**：

- 使用 `@mcp.tool()` 装饰器注册
- 统一的错误处理模式
- 返回 JSON 字符串
- 记录日志

### 3. 基础设施 (utils.py)

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

### 4. 命令执行器 (command_executor.py)

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

### 1. 模块化

每个工具类别独立模块，便于：

- 维护和扩展
- 测试和调试
- 按需加载

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

1. 在合适的模块中添加函数
2. 使用 `@mcp.tool()` 装饰器
3. 遵循错误处理模式
4. 添加测试

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

## 未来扩展

计划中的改进：

- 更多工具类别
- 插件系统
- 配置文件支持
- 性能优化
- 更好的错误恢复
