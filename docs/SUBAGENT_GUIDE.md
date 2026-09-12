# Subagent AI Orchestration Guide

English | [中文](SUBAGENT_GUIDE.zh.md)

The subagent module delegates subtasks to external AI models (OpenAI,
Anthropic) from inside the MCP server: single calls, parallel execution,
conditional branching, token statistics and custom model support.

## Features

- Multi-provider: OpenAI (GPT-3.5/4/4o) and Anthropic (Claude 3 family)
- Custom API endpoints/base URLs (proxies, Azure OpenAI)
- Persistent configuration (keys saved once, auto-loaded)
- Parallel execution via thread pool (up to 10 tasks)
- Conditional branch decisions with cheap models
- Real-time token usage stats (no billing estimates — see changelog)
- Auto-retry on transient failures (3 retries, exponential backoff)
- Secrets are masked in all output

## Configuration

### Option 1: persistent config (recommended)

```python
from mcp_server.tools.subagent import subagent_config_set

subagent_config_set("openai", "sk-proj-xxxxxxxxxxxx")
subagent_config_set("anthropic", "sk-ant-xxxxxxxxxxxx")
# custom endpoint:
subagent_config_set("openai", "sk-xxx", "https://api.openai-proxy.com/v1")
```

Saved to `~/.subagent_config.json` and auto-loaded on restart. Inspect with
`subagent_config_list()`. See [SUBAGENT_CONFIG.md](SUBAGENT_CONFIG.md).

### Option 2: environment variables (temporary)

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_BASE="https://..."     # optional custom endpoints
export ANTHROPIC_API_BASE="https://..."
```

## Tools

### `subagent_call` — single AI call

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `provider` | str | yes | `"openai"` or `"anthropic"` |
| `model` | str | yes | any model name, e.g. `gpt-4o`, `claude-3-5-sonnet-20241022` |
| `messages` | str | yes | JSON message list `[{"role": "user", "content": "..."}]` |
| `max_tokens` | int | no | default auto, cap 32000 |
| `temperature` | float | no | 0.0–2.0, default 0.7 |

Returns `result`, `usage` (`prompt_tokens`, `completion_tokens`,
`total_tokens`), `model`, `provider`, `elapsed_time`, `status`.

### `subagent_parallel` — parallel execution

`tasks` (JSON task list; each with `name`, `provider`, `model`, `messages`,
optional `max_tokens`/`temperature`) and `max_workers` (default 3, cap 10).
Returns per-task `results` and a `summary` with aggregated token totals.

### `subagent_conditional` — branching

`condition_task`, `true_task`, `false_task` (all JSON task strings). The
condition runs first; its `evaluated_as` boolean picks the branch. Returns
`condition_result`, `branch_taken`, `final_result`, `total_usage`. Tip: use a
cheap fast model for the condition.

### Config tools

`subagent_config_set(provider, api_key, api_base?)`,
`subagent_config_get(provider)` (masked key, shows `source`:
`environment`/`config_file`), `subagent_config_list()`.

## Supported models (examples)

| OpenAI | Context | Best for |
|---|---|---|
| `gpt-3.5-turbo` | 16K | fast, economical |
| `gpt-4` | 8K | complex reasoning |
| `gpt-4-turbo` | 128K | long text |
| `gpt-4o` | 128K | latest multimodal |
| `gpt-4o-mini` | 128K | cheapest |

| Anthropic | Context | Best for |
|---|---|---|
| `claude-3-haiku-20240307` | 200K | fast, simple |
| `claude-3-5-haiku-20241022` | 200K | upgraded haiku |
| `claude-3-5-sonnet-20241022` | 200K | strongest general |
| `claude-3-opus-20240229` | 200K | highest quality |

Prices change — check provider pricing pages. Custom/fine-tuned model names
are supported (no preset pricing table since v0.2.0).

## Error handling

| Error | Fix |
|---|---|
| `OPENAI_API_KEY environment variable not set` | configure keys |
| `Invalid OpenAI/Anthropic API key` | check the key |
| `API rate limit exceeded` | lower `max_workers`, retry later |
| `API timeout after 300s` | reduce `max_tokens`, check network |
| `max_tokens cannot exceed 32000` | shorten input or use a bigger-context model |

Retries: 3 attempts, 1s initial delay, 2.0 exponential backoff, on timeouts
and transient network/503 errors.

## Cost optimization

1. Match the model to the task (haiku/3.5-turbo for simple work).
2. Always set `max_tokens`.
3. Parallelize independent tasks instead of sequential calls.
4. Use conditional branching so expensive models only run when needed.
5. Monitor `usage` fields and provider consoles
   ([OpenAI](https://platform.openai.com/usage) /
   [Anthropic](https://console.anthropic.com/settings/usage)).

## Security

- Keys via env vars or config file — never hardcode.
- All output auto-masks anything matching
  `PASSWORD|SECRET|TOKEN|KEY|CREDENTIAL|API_KEY`.
- HTTPS for every call; token cap 32000; max 10 parallel tasks.

## Limitations

32,000 token cap per call · max 10 parallel tasks · stateless (no
cross-call history) · no streaming · subject to provider rate limits.

## Troubleshooting

Logs go to `mcp_server.log`:

```bash
tail -f mcp_server.log | grep -i subagent
```

Verify keys directly:

```bash
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
curl https://api.anthropic.com/v1/messages -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" -H "content-type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","messages":[{"role":"user","content":"Hi"}],"max_tokens":10}'
```
