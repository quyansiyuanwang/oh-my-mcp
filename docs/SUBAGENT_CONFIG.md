# Subagent Configuration Management

English | [中文](SUBAGENT_CONFIG.zh.md)

Persistent configuration for the subagent feature: API keys and custom
endpoints are stored once and survive restarts.

## Config file

`~/.subagent_config.json` (Windows: `C:\Users\<username>\.subagent_config.json`):

```json
{
  "api_keys": {
    "openai": "sk-xxxxxxxxxxxxxxxxxxxx",
    "anthropic": "sk-ant-xxxxxxxxxxxx"
  },
  "api_bases": {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com/v1"
  }
}
```

## Precedence (high → low)

1. Environment variables: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
   `OPENAI_API_BASE`, `ANTHROPIC_API_BASE`
2. Config file: `~/.subagent_config.json`
3. Defaults: each provider's official API endpoint

Design intent: keep the usual keys in the file, override temporarily via env
vars (the query tools show which `source` won).

## Management tools

```python
from mcp_server.tools.subagent import (
    subagent_config_set,
    subagent_config_get,
    subagent_config_list,
)

subagent_config_set("openai", "sk-proj-xxxxxxxxxxxx")
subagent_config_set("openai", "sk-xxx", "https://api.openai-proxy.com/v1")  # custom base
subagent_config_set("anthropic", "sk-ant-xxxxxxxxxxxx")

subagent_config_get("openai")    # masked preview, source, config_file
subagent_config_list()           # all providers, masked
```

## Usage patterns

- **Custom endpoints** — proxies or Azure OpenAI:
  `subagent_config_set("openai", "key", "https://your-resource.openai.azure.com/openai/deployments")`
- **Temporary switch** — set `os.environ["OPENAI_API_KEY"]` to override the
  file for the current session; `subagent_config_get("openai")["source"]`
  will report `environment`.
- **Multi-project** — `SubagentConfig(config_path="./project_a_config.json")`
  keeps per-project files.
- **Delete a provider** — remove the entry from the JSON file manually, or
  `config.remove_api_key("openai")` via `get_config()`.

## Security best practices

1. File permissions are auto-set to `600` on Unix/Linux/macOS.
2. Never commit config files — add `*.subagent_config.json` to `.gitignore`.
3. In CI/CD use environment variables / secrets instead of files.
4. Rotate keys regularly (`subagent_config_set` then verify with
   `subagent_config_get`).
5. No encryption at rest — rely on OS-level encryption (BitLocker/FileVault)
   or a secrets manager for sensitive environments.
