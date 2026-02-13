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
- [browser_usage_example.py](browser_usage_example.py) - 浏览器自动化使用示例
- [browser_config_wizard.py](browser_config_wizard.py) - 浏览器配置向导（交互式）

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

### browser_usage_example.py

演示浏览器自动化功能：

- 打开浏览器并导航
- 页面交互（点击、输入、滚动）
- 截图和页面信息提取
- JavaScript 执行
- Cookie 和网络日志管理
- 多标签页操作

### browser_config_wizard.py

交互式配置浏览器驱动和设置：

- Chrome/Edge 驱动路径配置
- 默认浏览器选择
- 无头模式设置
- 代理服务器配置
- 自动兜底开关

**运行方式**：

```bash
python examples/browser_config_wizard.py
```

按提示输入各项配置，完成后自动保存到 `~/.browser_config.json`。

**适用场景**：
- 首次使用浏览器自动化功能
- Chrome 驱动自动下载失败（网络问题）
- 需要使用代理访问网络
- 中国大陆等有网络限制的环境

详细说明参见：[浏览器配置指南](../docs/zh/BROWSER_CONFIG_GUIDE.md)

## 更多资源

- [完整文档](../docs/)
- [Subagent 指南](../docs/zh/SUBAGENT_GUIDE.md)
- [浏览器配置指南](../docs/zh/BROWSER_CONFIG_GUIDE.md)
- [架构文档](../docs/en/ARCHITECTURE.md)
