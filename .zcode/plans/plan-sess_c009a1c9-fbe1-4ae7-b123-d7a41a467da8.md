# CI 修复 + 文档自动生成系统(dogen)

## 一、修复 CI(两个 workflow 都红)

1. **Lint**:CI 用 `uv run` 锁定的新版 ruff,规则集(UP006 等)比本地 venv 旧版严格,报 495 错误。
   - 用 `uv run ruff check src/ tests/ --statistics` 枚举规则分布;
   - `uv run ruff check --fix`(+安全的 unsafe-fixes)批量修复(大部分是 `Dict`→`dict`、`Optional`→`| None`);
   - 剩余手工修复,直到 `uv run ruff check src/ tests/` 本地复现干净;
   - 同时验证 `uv run ruff format`、`uv run mypy src/`(CI 也跑 mypy --strict,用 uv 版本对齐)。
2. **Tests**:`test_search_case_insensitive_and_pattern` 在 Linux 失败——glob 大小写敏感性是平台行为,测试改用同大小写文件名,大小写不敏感断言只针对工具自己实现的 `name_contains`。
3. 全部用 `uv run` 对齐 CI 环境验证后提交,推送并 `gh run watch` 确认绿。

## 二、文档自动生成系统(scripts/docs/generate_docs.py)

**数据来源(AST 分析,单一事实源)**:
- 扫描 `src/mcp_server/tools/*/`:AST 解析 `handlers.py`,提取每个 `@tool_handler` 函数的名称、docstring(首行为短描述)、参数(名/类型/默认值);从 `config.yaml` 读 category_name、category_description;给每个 `config.yaml` 增加 `emoji` 字段作为展示元数据。
- 汇总为:每类工具数、总工具数、类别数、每个工具的名称+描述。

**生成规则(markers 局部替换,不碰手写内容)**:
- 在以下文档中插入 `<!-- DOCGEN:xxx:start --> ... <!-- DOCGEN:xxx:end -->` 标记,脚本只重写标记之间:
  - `README.md` Features 类别列表
  - `CLAUDE.md` 概览计数与类别列表
  - `docs/README.md` Tool Categories 段
  - `docs/en/TOOL_REFERENCE.md` 全部 10 个类别的工具章节(工具名 + docstring 首行描述,风格与现有一致)
- `pyproject.toml` description 与 `main.py` docstring 的计数用正则替换(带错误提示,找不到时报清晰错误)。
- 工具的详细用法/参数说明仍保持手写;生成内容只覆盖"工具名+一句话描述+计数"这类必然随代码漂移的部分。

**脚本接口**:
- `python scripts/docs/generate_docs.py --write` 重新生成并写回;
- `--check` 内容不一致时 exit 1 并打印差异文件(CI 用);
- 纯 stdlib(ast/yaml/pyyaml 已有),mypy strict 合规。

## 三、CI 集成

- `.github/workflows/lint.yml` 增加步骤:
  `uv run python scripts/docs/generate_docs.py --check`
  —— 任何增删工具/改 docstring 而没跑 `--write` 的 PR 都会红。
- README Development 区块加一句"增删工具后运行 `python scripts/docs/generate_docs.py`"。

## 四、验证与提交

1. `uv run` 下全绿:ruff check/format、mypy --strict、pytest;
2. 生成脚本本身加冒烟测试 `tests/test_docgen.py`(解析样例函数、片段替换的幂等性);
3. 提交拆分:fix(lint+test 平台假设)、feat(dogen 脚本+markers+CI)、docs(重新生成的文档);
4. 推送并用 `gh run watch` 确认两个 workflow 全绿。