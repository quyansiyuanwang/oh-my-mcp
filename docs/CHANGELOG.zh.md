# 更新日志

[English](CHANGELOG.md) | 中文

本文档记录本项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
版本号遵循 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。
英文原版以 [CHANGELOG.md](CHANGELOG.md) 为准。

## [Unreleased]

### 新增

- **Command Execution 类别**(4 个工具):此前闲置的 `command_executor` 安全执行基础设施现以 MCP 工具形式开放
  - `run_command`:执行白名单命令(shell=False、参数清洗、超时上限、输出限长)
  - `list_allowed_commands` / `add_allowed_commands` / `remove_allowed_commands`
    管理持久化白名单(~/.oh-my-mcp/execution_config.json)
- `grep_files`(File System,现为 13 个工具):目录树内容搜索,支持正则/纯文本、
  行号定位、二进制文件跳过(扩展名 + NUL 嗅探)与 2MB 单文件上限
- **文档双语重组**:中文正文文档从 docs/en/ 移至 docs/zh/,英文版全新撰写;
  docgen 现可刷新项目结构树与指南引用中的各类别计数
- Computer Use 核心文档的英文版:INSTALLATION、CONTRIBUTING、BUILD、ARCHITECTURE、
  PROJECT_STRUCTURE、COMPUTER_USE_GUIDE

### 变更

- 工具数量 141 → 146,类别 10 → 11
- `compress_zip`/`compress_tar` 支持目录递归打包并保留层级
  (此前一律扁平化为 basename / 直接拒绝目录)
- 提交 `uv.lock` —— 此前被 gitignore,导致 CI 自由解析到新版工具链
  (ruff 0.16 更严格的默认规则)而构建失败
- 构建:从 PyInstaller 排除列表移除 PIL(computer use 截图必需)
- 新增 `computer` 可选依赖组与桌面控制核心依赖

### 修复

- `read_file`/`write_file`/`append_file`:换行符翻译在 Windows 上把 `\r\n`
  写成 `\r\r\n`(现通过 `newline=""` 逐字节保真)
- `copy_file` 目标为已存在目录时静默把文件复制进目录内部
- `flatten_json` 丢弃空 dict/list 值
- `validate_json_schema` 把布尔值报告为 number
- 51 处错误响应将路径直接拼入 JSON 模板,在 Windows 路径上产生非法 JSON
  (统一改用 `error_json()` 助手)
- `extract_tar` 加固:`filter="data"`(兼容 Python 3.14,防符号链接逃逸)
- `calculate_expression` 拒绝了文档声称支持的数学函数;标识符白名单现允许
  sqrt/sin/abs/max/... 同时保持 eval 沙箱化
- `date_to_timestamp` 忽略 `timezone="utc"` 参数
- `locate_on_screen` 在无 OpenCV 时完全不可用(优雅降级为精确像素匹配)
- `diff_files`/`diff_text` 返回 "Object of type function is not JSON
  serializable"(diff 载荷引用了同名函数而非 diff 文本)

## [0.1.1] - 2026-02-11

### 新增

- **持久化配置管理**:Subagent API 凭据的配置系统
  - `SubagentConfig` 类,凭据持久化存储(~/.subagent_config.json)
  - 三个 MCP 工具:`subagent_config_set`、`subagent_config_get`、`subagent_config_list`
  - Unix/Linux/macOS 上自动设置 0o600 文件权限
  - 配置优先级:环境变量 > 配置文件 > 默认值
  - 查询输出中的敏感数据自动脱敏
- Subagent 工具从 3 个增至 6 个
- OpenAI / Anthropic 客户端类全部改用配置管理器

完整英文条目见 [CHANGELOG.md](CHANGELOG.md)。
