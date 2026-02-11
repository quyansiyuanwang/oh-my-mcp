# MCP Server 示例

本目录包含 MCP Server 的使用示例。

## 示例列表

### 基础示例
- [basic_usage.py](basic_usage.py) - 基本使用方法和服务器启动

### 工具示例
- [web_search_example.py](web_search_example.py) - 网络搜索和页面抓取
- [file_operations_example.py](file_operations_example.py) - 文件读写和操作
- [data_processing_example.py](data_processing_example.py) - JSON/CSV/YAML 数据处理
- [python_tools_example.py](python_tools_example.py) - Python 代码执行和分析

## 运行示例

每个示例都是独立的 Python 脚本，可以直接运行：

```bash
# 运行基本示例
python examples/basic_usage.py

# 运行网络搜索示例
python examples/web_search_example.py
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

### data_processing_example.py
演示如何：
- 解析 JSON/CSV/YAML
- 数据格式转换
- 数据查询和过滤
- 数据验证

### python_tools_example.py
演示如何：
- 执行 Python 代码
- 验证语法
- 分析 AST
- 格式化代码

## 更多资源

- [完整文档](../docs/)
- [API 参考](../docs/API_REFERENCE.md)
- [使用指南](../docs/USAGE.md)
