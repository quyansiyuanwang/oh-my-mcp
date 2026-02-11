# Subagent AI Orchestration Guide

## 概述

Subagent 是一个强大的 AI 编排工具模块，允许您在 MCP 服务器中委派子任务给外部 AI 模型（OpenAI 和 Anthropic）。支持并行任务执行、条件分支决策、token 使用统计和自定义模型。

## 核心功能

- ✅ **多 AI 接入商支持**：OpenAI (GPT-3.5/4)、Anthropic (Claude-3)
- ✅ **自定义 API 端点**：支持私有部署和自定义 API 基础 URL
- ✅ **持久化配置**：API 密钥自动保存，无需每次重新配置
- ✅ **并行任务执行**：使用线程池同时执行多个独立子任务
- ✅ **条件分支决策**：基于 AI 判断动态选择执行路径
- ✅ **Token 统计**：实时计算输入/输出 token 使用量
- ✅ **自定义模型支持**：支持使用任意自定义模型名称
- ✅ **无状态设计**：每次调用独立，无需维护会话状态
- ✅ **自动重试**：网络失败时自动重试（最多 3 次）
- ✅ **安全保障**：API 密钥自动脱敏，环境变量管理

## 快速开始

### 方式 1: 使用持久化配置（推荐）

使用配置管理工具永久保存 API 密钥：

```python
from mcp_server.tools.subagent import subagent_config_set

# 设置 OpenAI (一次配置，永久生效)
subagent_config_set("openai", "sk-proj-xxxxxxxxxxxx")

# 设置 Anthropic
subagent_config_set("anthropic", "sk-ant-xxxxxxxxxxxx")

# 设置自定义端点
subagent_config_set("openai", "sk-xxx", "https://api.openai-proxy.com/v1")
```

配置将保存到 `~/.subagent_config.json`，下次启动自动加载。

**查看配置:**

```python
from mcp_server.tools.subagent import subagent_config_list
print(subagent_config_list())
```

📚 **详细配置文档**: [Subagent 配置管理指南](./SUBAGENT_CONFIG.md)

### 方式 2: 使用环境变量

在环境变量中设置您的 API 密钥（临时，每次会话有效）：

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Windows PowerShell:**

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

### 2. 自定义 API 端点（可选）

如果您使用私有部署或自定义端点：

```bash
# 自定义 OpenAI 端点
export OPENAI_API_BASE="https://your-custom-endpoint.com/v1"

# 自定义 Anthropic 端点
export ANTHROPIC_API_BASE="https://your-custom-endpoint.com/v1"
```

### 3. 使用工具

配置完成后，MCP 服务器会自动加载 Subagent 工具。您可以在 Claude Desktop 或任何 MCP 客户端中使用这些工具。

## 工具详解

### 1. `subagent_call` - 单次 AI 调用

委派单个子任务给 AI 模型处理。

**参数：**

| 参数          | 类型   | 必需 | 描述                                        |
| ------------- | ------ | ---- | ------------------------------------------- |
| `provider`    | string | ✓    | AI 提供商：`"openai"` 或 `"anthropic"`      |
| `model`       | string | ✓    | 模型名称（见下方支持的模型列表）            |
| `messages`    | string | ✓    | JSON 格式的消息列表                         |
| `max_tokens`  | int    | ✗    | 最大生成 token 数（默认：自动，上限 32000） |
| `temperature` | float  | ✗    | 温度参数 0.0-2.0（默认：0.7）               |

**返回：**

```json
{
  "result": "AI 生成的响应文本",
  "usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "model": "gpt-4",
  "provider": "openai",
  "elapsed_time": 2.34,
  "status": "success"
}
```

**示例：**

```python
# 基础用例：询问问题
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is quantum computing?"}
]

result = subagent_call(
    provider="openai",
    model="gpt-3.5-turbo",
    messages=json.dumps(messages),
    max_tokens=500,
    temperature=0.7
)
```

```python
# 使用 Claude 进行长文本处理
messages = [
    {"role": "user", "content": "Summarize this document: [long text...]"}
]

result = subagent_call(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    messages=json.dumps(messages),
    max_tokens=4096
)
```

```python
# 使用 Anthropic Claude 处理中文任务
messages = [
    {"role": "user", "content": "请解释什么是人工智能"}
]

result = subagent_call(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    messages=json.dumps(messages),
    max_tokens=500,
    temperature=0.7
)
```

### 2. `subagent_parallel` - 并行任务执行

同时执行多个独立的 AI 任务，适合需要并发处理的场景。

**参数：**

| 参数          | 类型   | 必需 | 描述                           |
| ------------- | ------ | ---- | ------------------------------ |
| `tasks`       | string | ✓    | JSON 格式的任务列表            |
| `max_workers` | int    | ✗    | 最大并发数（默认：3，上限 10） |

**任务格式：**

```json
[
  {
    "name": "task1",
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "messages": [{ "role": "user", "content": "..." }],
    "max_tokens": 500,
    "temperature": 0.7
  },
  {
    "name": "task2",
    "provider": "anthropic",
    "model": "claude-3-haiku-20240307",
    "messages": [{ "role": "user", "content": "..." }]
  }
]
```

**返回：**

```json
{
  "results": [
    {
      "task_name": "task1",
      "task_index": 0,
      "result": "...",
      "usage": {...},
      "status": "success"
    },
    {
      "task_name": "task2",
      "task_index": 1,
      "result": "...",
      "usage": {...},
      "status": "success"
    }
  ],
  "summary": {
    "total_tasks": 2,
    "successful": 2,
    "failed": 0,
    "total_input_tokens": 234,
    "total_output_tokens": 567,
    "total_tokens": 801,
    "elapsed_time": 3.45
  }
}
```

**示例：**

```python
# 并行执行多个独立分析任务
tasks = [
    {
        "name": "analyze_sentiment",
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Analyze sentiment: [text]"}]
    },
    {
        "name": "extract_keywords",
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Extract keywords: [text]"}]
    },
    {
        "name": "summarize",
        "provider": "anthropic",
        "model": "claude-3-haiku-20240307",
        "messages": [{"role": "user", "content": "Summarize: [text]"}]
    }
]

result = subagent_parallel(
    tasks=json.dumps(tasks),
    max_workers=3
)

# 访问各个任务结果
for task_result in result["results"]:
    print(f"{task_result['task_name']}: {task_result['result']}")
```

```python
# 多语言翻译并行处理
tasks = [
    {
        "name": "to_chinese",
        "provider": "openai",
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Translate to Chinese: Hello world"}]
    },
    {
        "name": "to_french",
        "provider": "openai",
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Translate to French: Hello world"}]
    },
    {
        "name": "to_spanish",
        "provider": "openai",
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "Translate to Spanish: Hello world"}]
    }
]

result = subagent_parallel(tasks=json.dumps(tasks), max_workers=3)
```

### 3. `subagent_conditional` - 条件分支决策

先让 AI 评估条件，然后根据结果执行不同的分支任务。

**参数：**

| 参数             | 类型   | 必需 | 描述                         |
| ---------------- | ------ | ---- | ---------------------------- |
| `condition_task` | string | ✓    | 用于评估条件的任务（JSON）   |
| `true_task`      | string | ✓    | 条件为真时执行的任务（JSON） |
| `false_task`     | string | ✓    | 条件为假时执行的任务（JSON） |

**返回：**

```json
{
  "condition_result": {
    "text": "true",
    "evaluated_as": true,
    "usage": {...}
  },
  "branch_taken": "true_branch",
  "final_result": {
    "result": "...",
    "usage": {...},
    "status": "success"
  },
  "total_usage": {
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  },
  "status": "success"
}
```

**示例：**

```python
# 根据文本长度选择处理策略
condition_task = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "messages": [{
        "role": "user",
        "content": "Is this text longer than 1000 words? [text]. Reply only 'true' or 'false'"
    }],
    "max_tokens": 10,
    "temperature": 0.1
}

true_task = {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "messages": [{
        "role": "user",
        "content": "Create a detailed summary with sections: [text]"
    }],
    "max_tokens": 2000
}

false_task = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "messages": [{
        "role": "user",
        "content": "Create a brief summary: [text]"
    }],
    "max_tokens": 500
}

result = subagent_conditional(
    condition_task=json.dumps(condition_task),
    true_task=json.dumps(true_task),
    false_task=json.dumps(false_task)
)

print(f"Condition evaluated as: {result['condition_result']['evaluated_as']}")
print(f"Branch taken: {result['branch_taken']}")
```

### 4. `subagent_config_set` - 设置配置

持久化保存 API 密钥和端点配置到配置文件。

**参数：**

| 参数       | 类型   | 必需 | 描述                                    |
| ---------- | ------ | ---- | ------------------------------------------ |
| `provider` | string | ✓    | 提供商：`"openai"` `"anthropic"` |
| `api_key`  | string | ✓    | API 密钥                              |
| `api_base` | string | ✗    | API 基础 URL（可选）                         |

**返回：**

```json
{
  "provider": "openai",
  "api_key_set": true,
  "api_key_preview": "sk-proj-...xxxx",
  "api_base": "https://api.openai.com/v1",
  "config_file": "/home/user/.subagent_config.json",
  "status": "success"
}
```

**示例：**

```python
# 设置 OpenAI API
subagent_config_set("openai", "sk-proj-xxxxxxxxxxxx")

# 设置自定义端点
subagent_config_set("openai", "sk-xxx", "https://api.openai-proxy.com/v1")

# 设置 Anthropic
subagent_config_set("anthropic", "sk-ant-xxxxxxxxxxxx")
```

### 5. `subagent_config_get` - 查询配置

获取指定提供商的配置信息（密钥已脱敏）。

**参数：**

| 参数       | 类型   | 必需 | 描述       |
| ---------- | ------ | ---- | ---------- |
| `provider` | string | ✓    | 提供商名称 |

**返回：**

```json
{
  "provider": "openai",
  "configured": true,
  "api_key": "sk-proj-...xxxx",
  "api_base": "https://api.openai.com/v1",
  "source": "config_file",
  "config_file": "/home/user/.subagent_config.json",
  "status": "success"
}
```

**示例：**

```python
# 查询 OpenAI 配置
config = subagent_config_get("openai")
print(f"OpenAI 配置来源: {config['source']}")
```

### 6. `subagent_config_list` - 列出所有配置

列出所有已配置的 AI 提供商及其状态。

**返回：**

```json
{
  "providers": {
    "openai": {
      "api_key": "sk-proj-...xxxx",
      "api_base": "https://api.openai.com/v1",
      "source": "config_file"
    },
    "anthropic": {
      "api_key": "sk-ant-...eQhJ",
      "api_base": "https://api.anthropic.com/v1",
      "source": "environment"
    }
  },
  "total_configured": 2,
  "config_file": "/home/user/.subagent_config.json",
  "status": "success"
}
```

**示例：**

```python
# 列出所有配置
providers = subagent_config_list()
print(f"已配置 {providers['total_configured']} 个提供商")
```

📚 **完整配置管理文档**: [Subagent 配置管理指南](./SUBAGENT_CONFIG.md)
print(f"Final result: {result['final_result']['result']}")

````

```python
# 根据情感分析结果选择响应方式
condition_task = {
    "provider": "openai",
    "model": "gpt-4",
    "messages": [{
        "role": "user",
        "content": "Is this customer feedback positive? '[feedback]'. Reply only 'true' or 'false'"
    }]
}

true_task = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "messages": [{
        "role": "user",
        "content": "Generate a thank you response for positive feedback: [feedback]"
    }]
}

false_task = {
    "provider": "openai",
    "model": "gpt-4",
    "messages": [{
        "role": "user",
        "content": "Generate an empathetic response and solution for negative feedback: [feedback]"
    }]
}

result = subagent_conditional(
    condition_task=json.dumps(condition_task),
    true_task=json.dumps(true_task),
    false_task=json.dumps(false_task)
)
````

## 支持的模型

### OpenAI 模型

| 模型            | 输入价格    | 输出价格   | 上下文窗口 | 适用场景             |
| --------------- | ----------- | ---------- | ---------- | -------------------- |
| `gpt-3.5-turbo` | $0.0015/1K  | $0.002/1K  | 16K        | 快速、经济的通用任务 |
| `gpt-4`         | $0.03/1K    | $0.06/1K   | 8K         | 复杂推理、高质量输出 |
| `gpt-4-turbo`   | $0.01/1K    | $0.03/1K   | 128K       | 长文本处理           |
| `gpt-4o`        | $0.005/1K   | $0.015/1K  | 128K       | 最新多模态模型       |
| `gpt-4o-mini`   | $0.00015/1K | $0.0006/1K | 128K       | 最经济的小型模型     |

### Anthropic Claude 模型

| 模型                         | 输入价格    | 输出价格    | 上下文窗口 | 适用场景           |
| ---------------------------- | ----------- | ----------- | ---------- | ------------------ |
| `claude-3-haiku-20240307`    | $0.00025/1K | $0.00125/1K | 200K       | 快速响应、简单任务 |
| `claude-3-5-haiku-20241022`  | $0.001/1K   | $0.005/1K   | 200K       | 升级版 Haiku       |
| `claude-3-sonnet-20240229`   | $0.003/1K   | $0.015/1K   | 200K       | 平衡性能和成本     |
| `claude-3-5-sonnet-20241022` | $0.003/1K   | $0.015/1K   | 200K       | 最新最强 Claude    |
| `claude-3-opus-20240229`     | $0.015/1K   | $0.075/1K   | 200K       | 最高质量推理       |

> **注意**：价格可能会随时调整，以官方最新定价为准。

## Token 计数算法

Subagent 使用字符近似算法估算 token 数量：

- **英文文本**：约 4 个字符 = 1 token
- **中文文本**：约 2 个字符 = 1 token
- **消息开销**：每条消息额外 4 tokens（role + 分隔符）

**准确性**：误差约 ±10%，足够用于成本预估。

**示例**：

```python
text = "Hello world, this is a test."  # 29 characters
# 估算: 29 / 4 ≈ 7 tokens

text_cn = "你好世界，这是测试。"  # 10 characters
# 估算: 10 / 2 = 5 tokens
```

如需精确 token 计数，建议使用：

- OpenAI: `tiktoken` 库
- Anthropic: `anthropic-tokenizer` 库

## 成本优化建议

### 1. 选择合适的模型

- **简单任务**：使用 `gpt-3.5-turbo` 或 `claude-3-haiku`
- **复杂推理**：使用 `gpt-4` 或 `claude-3-5-sonnet`
- **长文本处理**：使用 `claude-3-5-sonnet`（200K 上下文）

### 2. 设置 `max_tokens` 限制

```python
# 避免不必要的长输出
result = subagent_call(
    provider="openai",
    model="gpt-4",
    messages=messages,
    max_tokens=500  # 限制输出长度
)
```

### 3. 使用并行任务提高效率

```python
# 不推荐：顺序执行
result1 = subagent_call(...)
result2 = subagent_call(...)
result3 = subagent_call(...)

# 推荐：并行执行
result = subagent_parallel(tasks=[task1, task2, task3])
```

### 4. 条件分支避免冗余调用

```python
# 只在必要时调用昂贵的模型
result = subagent_conditional(
    condition_task={...},  # 用便宜的模型判断
    true_task={...},       # 用贵的模型处理
    false_task={...}       # 跳过或用便宜的模型
)
```

### 5. Token 使用监控

所有工具都返回 `usage` 字段，定期查看 token 使用情况：

```python
result = subagent_call(...)
print(f"Tokens used: {result['usage']['total_tokens']}")
print(f"Input tokens: {result['usage']['prompt_tokens']}")
print(f"Output tokens: {result['usage']['completion_tokens']}")

result = subagent_parallel(...)
print(f"Total tokens: {result['summary']['total_tokens']}")
print(f"Tasks completed: {result['summary']['successful']}/{result['summary']['total_tasks']}")
```

**成本查询**: 可以通过 API provider 的官方控制台查看实际成本：
- **OpenAI**: https://platform.openai.com/usage
- **Anthropic**: https://console.anthropic.com/settings/usage

## 错误处理

### 常见错误及解决方法

#### 1. API 密钥未设置

**错误**：`OPENAI_API_KEY environment variable not set`

**解决**：

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

#### 2. API 密钥无效

**错误**：`Invalid OpenAI API key` 或 `Invalid Anthropic API key`

**解决**：检查 API 密钥是否正确，是否已过期。

#### 3. 速率限制

**错误**：`API rate limit exceeded`

**解决**：

- 减少并发数：`max_workers=1`
- 等待后重试
- 升级 API 套餐

#### 4. 超时

**错误**：`API timeout after 300s`

**解决**：

- 减少 `max_tokens` 以加快生成
- 检查网络连接
- 使用更快的模型（如 `gpt-3.5-turbo`）

#### 5. Token 超限

**错误**：`max_tokens cannot exceed 32000`

**解决**：

- 减少输入文本长度
- 分批处理长文本
- 使用支持更大上下文的模型

### 重试机制

Subagent 自动重试失败的 API 调用（最多 3 次）：

- **重试次数**：3
- **初始延迟**：1 秒
- **退避系数**：2.0（指数退避）

重试场景：

- 网络超时
- 503 服务不可用
- 临时性网络错误

## 安全性

### API 密钥保护

1. **环境变量存储**：密钥不硬编码到代码中
2. **自动脱敏**：日志中的 API 密钥自动隐藏
3. **传输加密**：所有 API 调用使用 HTTPS

### 敏感词过滤

以下关键词在日志中自动脱敏：

- `PASSWORD`
- `SECRET`
- `TOKEN`
- `KEY`
- `CREDENTIAL`
- `API_KEY`

### 输入验证

- **消息格式验证**：确保 `messages` 格式正确
- **Token 上限**：单次调用不超过 32000 tokens
- **并发限制**：最多 10 个并行任务

## 高级用例

### 1. 多轮对话代理

```python
def multi_turn_conversation(user_query):
    """多轮对话示例"""

    # 第一轮：分析用户意图
    intent_task = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": f"Analyze user intent: '{user_query}'"
        }]
    }

    intent_result = subagent_call(**intent_task)
    intent = intent_result["result"]

    # 第二轮：根据意图生成响应
    response_task = {
        "provider": "openai",
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": f"Detected intent: {intent}"},
            {"role": "user", "content": "Provide a detailed response."}
        ]
    }

    return subagent_call(**response_task)
```

### 2. 文档分析流水线

```python
def analyze_document(document_text):
    """并行分析文档的多个维度"""

    tasks = [
        {
            "name": "extract_entities",
            "provider": "openai",
            "model": "gpt-4",
            "messages": [{
                "role": "user",
                "content": f"Extract all named entities: {document_text}"
            }]
        },
        {
            "name": "summarize",
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "messages": [{
                "role": "user",
                "content": f"Summarize this document: {document_text}"
            }]
        },
        {
            "name": "key_points",
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "messages": [{
                "role": "user",
                "content": f"List key points: {document_text}"
            }]
        },
        {
            "name": "sentiment",
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "messages": [{
                "role": "user",
                "content": f"Analyze sentiment: {document_text}"
            }]
        }
    ]

    result = subagent_parallel(
        tasks=json.dumps(tasks),
        max_workers=4
    )

    return result
```

### 3. 智能路由决策

```python
def smart_routing(user_message):
    """根据消息复杂度选择模型"""

    # 评估消息复杂度
    condition_task = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": f"""Is this question complex and requires deep reasoning?
            Question: '{user_message}'
            Reply only 'true' or 'false'"""
        }],
        "temperature": 0.1
    }

    # 复杂问题用 GPT-4
    complex_task = {
        "provider": "openai",
        "model": "gpt-4",
        "messages": [{"role": "user", "content": user_message}],
        "max_tokens": 2000
    }

    # 简单问题用 GPT-3.5
    simple_task = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_message}],
        "max_tokens": 500
    }

    result = subagent_conditional(
        condition_task=json.dumps(condition_task),
        true_task=json.dumps(complex_task),
        false_task=json.dumps(simple_task)
    )

    return result
```

### 4. 自我验证和改进

```python
def self_improving_generation(prompt):
    """生成 -> 评估 -> 改进循环"""

    # 第一步：生成初稿
    draft_task = {
        "provider": "openai",
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}]
    }

    draft_result = subagent_call(**draft_task)
    draft = draft_result["result"]

    # 第二步：评估质量
    eval_task = {
        "provider": "openai",
        "model": "gpt-4",
        "messages": [{
            "role": "user",
            "content": f"""Evaluate this response quality (1-10):
            Prompt: {prompt}
            Response: {draft}
            Reply with only a number."""
        }],
        "temperature": 0.1
    }

    eval_result = subagent_call(**eval_task)
    score = float(eval_result["result"].strip())

    # 第三步：如果质量不够，要求改进
    if score < 7:
        improve_task = {
            "provider": "openai",
            "model": "gpt-4",
            "messages": [{
                "role": "user",
                "content": f"""Improve this response:
                Original prompt: {prompt}
                Current response: {draft}
                Quality score: {score}/10
                Provide an improved version."""
            }]
        }

        return subagent_call(**improve_task)

    return draft_result
```

## 故障排查

### 检查日志

MCP 服务器会记录详细的调用日志到 `mcp_server.log`：

```bash
tail -f mcp_server.log | grep -i subagent
```

日志包含：

- API 调用详情
- Token 使用统计
- 错误信息
- 重试记录

### 测试连接

使用简单的测试调用验证配置：

```python
messages = [{"role": "user", "content": "Say 'Hello'"}]

# 测试 OpenAI
result = subagent_call(
    provider="openai",
    model="gpt-3.5-turbo",
    messages=json.dumps(messages),
    max_tokens=10
)

# 测试 Anthropic
result = subagent_call(
    provider="anthropic",
    model="claude-3-haiku-20240307",
    messages=json.dumps(messages),
    max_tokens=10
)
```

### 验证 API 密钥

```bash
# 测试 OpenAI 密钥
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 测试 Anthropic 密钥
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","messages":[{"role":"user","content":"Hi"}],"max_tokens":10}'
```

## 性能优化

### 1. 并发调优

```python
# 根据 API 速率限制调整并发数
# OpenAI Tier 1: max_workers=3
# OpenAI Tier 2+: max_workers=5-10
result = subagent_parallel(tasks=tasks, max_workers=3)
```

### 2. 降低温度提高速度

```python
# 温度越低，生成越快（但创造性降低）
result = subagent_call(
    provider="openai",
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.1  # 更确定的输出
)
```

### 3. 使用流式响应（未来功能）

当前版本使用批量响应。未来版本将支持流式响应以提升用户体验。

## 最佳实践

1. **始终设置 `max_tokens`**：避免意外的长输出
2. **使用并行处理**：独立任务应并行执行以节省时间
3. **监控 Token 使用**：定期检查 `usage` 字段，通过 API provider 控制台查看成本
4. **选择合适的模型**：简单任务用便宜模型，复杂任务用高级模型
5. **优雅降级**：检查 `status` 字段，处理失败情况
6. **环境变量管理**：使用 `.env` 文件或密钥管理服务
7. **日志审查**：定期检查日志以发现问题
8. **自定义模型支持**：可以使用任意模型名称，包括自定义微调模型

## 限制和约束

- **单次调用 token 上限**：32000 tokens
- **并行任务上限**：10 个
- **无状态**：不维护跨调用的对话历史
- **无流式输出**：仅支持批量响应
- **API 速率限制**：受各 AI 提供商限制约束

## 相关资源

- [OpenAI API 文档](https://platform.openai.com/docs)
- [Anthropic API 文档](https://docs.anthropic.com)
- [MCP 协议规范](https://modelcontextprotocol.io)
- [FastMCP 框架](https://github.com/jlowin/fastmcp)

## 更新日志

### v0.2.0 (2026-02-12)

- ✅ **移除计费功能**: 不再返回 `cost` 字段，简化代码结构
- ✅ **自定义模型支持**: 支持使用任意模型名称，无需预先配置价格
- ✅ **移除 MODEL_PRICING**: 不再维护硬编码的价格表
- ✅ **移除 CostCalculator**: 删除成本计算逻辑
- ✅ **Token 统计保留**: 仍然返回 `usage` 字段用于监控
- 📝 **文档更新**: 更新示例和最佳实践

⚠️ **破坏性更改**: 返回值不再包含 `cost` 字段

### v0.1.0 (2026-02-11)

- ✅ 初始版本发布
- ✅ 支持 OpenAI 和 Anthropic API
- ✅ 实现 `subagent_call`, `subagent_parallel`, `subagent_conditional`
- ✅ Token 统计和成本追踪
- ✅ 自定义 API 端点支持
- ✅ 自动重试机制
- ✅ 完整的测试覆盖

## 反馈和支持

如有问题或建议，请提交 Issue 或 Pull Request。

---

**Happy AI Orchestration! 🤖✨**
