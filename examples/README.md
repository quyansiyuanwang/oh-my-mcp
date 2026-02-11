# MCP Server 示例

本目录包含 MCP Server 的使用示例。

## 示例列表

### 基础示例

- [basic_usage.py](basic_usage.py) - 基本使用方法和服务器启动

### 工具示例

- [web_search_example.py](web_search_example.py) - 网络搜索和页面抓取
- [file_operations_example.py](file_operations_example.py) - 文件读写和操作
- [subagent_usage_example.py](subagent_usage_example.py) - AI 任务委派和编排
- [subagent_config_example.py](subagent_config_example.py) - Subagent 配置管理

## 运行示例

每个示例都是独立的 Python 脚本，可以直接运行：

```bash
# 运行基本示例
python examples/basic_usage.py

# 运行网络搜索示例
python examples/web_search_example.py

# 运行 Subagent 示例
python examples/subagent_usage_example.py
```

## 前置要求

确保已安装 MCP Server：

```bash
pip install -e .
```

## 示例说明

### basic_usage.py

演示如何：

- 导入 MCP Server
- 创建服务器实例
- 注册工具
- 启动服务器

### web_search_example.py

演示如何：

- 使用 DuckDuckGo 搜索
- 抓取网页内容
- 解析 HTML
- 提取链接和标题

### file_operations_example.py

演示如何：

- 读写文件
- 搜索文件
- 比较文件
- 文件压缩和解压

### subagent_usage_example.py

演示如何：

- 委派任务到 AI 模型（OpenAI/Anthropic）
- 并行执行多个任务
- Token 使用追踪
- 成本计算

### subagent_config_example.py

演示如何：

- 管理 Subagent 配置
- 设置 API keys
- 配置默认模型
- 持久化配置

## 更多资源

- [完整文档](../docs/)
- [Subagent 指南](../docs/SUBAGENT_GUIDE.md)
- [API 参考](../docs/API_REFERENCE.md)
