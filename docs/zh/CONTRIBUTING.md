# Contributing to MCP Server

感谢您对 MCP Server 项目的关注！我们欢迎各种形式的贡献。

## 开发环境设置

### 前置要求

- Python 3.12 或更高版本
- Git
- UV（推荐）或 pip

### 安装开发环境

```bash
# 克隆仓库
git clone https://github.com/quyansiyuanwang/oh-my-mcp.git
cd oh-my-mcp

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"
```

## 代码风格

我们使用以下工具来保持代码质量：

- **isort**: 导入排序（兼容 Black）
- **Black**: 代码格式化（行长度 100）
- **Ruff**: 代码检查
- **mypy**: 静态类型检查（严格模式）
- **pytest**: 测试框架

### 运行代码检查

```bash
# 排序导入
isort src/ tests/

# 格式化代码
black src/ tests/

# 运行代码检查
ruff check src/ tests/

# 类型检查
mypy src/

# 运行测试
pytest tests/ -v

# 仅检查导入顺序（不修改）
isort --check-only --diff src/ tests/
```

## 测试要求

所有新功能和 bug 修复都应该包含测试：

1. 在 `tests/` 目录下创建或更新测试文件
2. 确保测试覆盖率不降低
3. 运行完整测试套件确保通过

```bash
# 运行测试并生成覆盖率报告
pytest tests/ --cov=mcp_server --cov-report=html
```

## Pull Request 流程

1. Fork 项目并创建新分支
2. 进行修改并添加测试
3. 确保所有测试通过
4. 提交 Pull Request

### PR 检查清单

- [ ] 代码通过所有测试
- [ ] 添加了必要的测试
- [ ] 代码符合风格指南
- [ ] 更新了相关文档
- [ ] 更新了 CHANGELOG.md

## 添加新工具

如果要添加新工具，请遵循以下步骤：

1. 在 `src/mcp_server/tools/` 中选择合适的插件目录
2. 在插件的 `handlers.py` 文件中添加工具
3. 使用 `@tool_handler` 装饰器
4. 遵循错误处理模式（try/except with logger.error）
5. 返回 JSON 字符串
6. 在 `tests/` 中添加测试

如果要添加新工具类别：

1. 创建新插件目录 `src/mcp_server/tools/new_category/`
2. 添加 `__init__.py`（空文件）
3. 添加 `config.yaml`（类别名、描述、启用状态）
4. 添加 `handlers.py`（使用 `@tool_handler` 装饰器）
5. 无需修改 `main.py`——插件会自动发现

## 问题报告

发现 bug？请创建 issue 并包含：

- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（Python 版本、操作系统等）

## 行为准则

请保持友好和专业的态度，尊重所有贡献者。
