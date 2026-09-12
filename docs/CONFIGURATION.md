# Configuration Guide

English | [中文](CONFIGURATION.zh.md)

This guide covers configuring the oh-my-mcp environment with the
`configure.py` script.

## Quick start

### Interactive configuration (recommended)

```bash
uv run configure.py
# or: python configure.py
```

Wizard steps:

1. **Environment check** — verifies Python version (3.12+) and package manager
2. **Install dependencies** — installs project packages automatically
3. **Enable/disable Subagent** — choose whether to enable AI task delegation
4. **Configure Subagent API** — set provider API keys (if enabled)
5. **Claude Desktop integration** — point Claude Desktop at this MCP server

### Non-interactive configuration

```bash
# Enable/disable subagent without prompts
uv run configure.py --enable-subagent --skip-deps --skip-claude
uv run configure.py --disable-subagent --skip-deps --skip-claude

# Configure a provider (auto-enables the subagent)
uv run configure.py --provider openai --api-key sk-xxx

# Multiple providers — keep --provider/--api-key/--api-base in matching order
uv run configure.py --provider openai --api-key sk-xxx \
    --provider anthropic --api-key sk-ant-xxx
```

Add `--skip-deps` to skip dependency installation and `--skip-claude` to skip
Claude Desktop configuration.

## Subagent: enable or disable?

The subagent lets Claude delegate complex tasks to external AI models
(OpenAI GPT, Anthropic Claude). Disable it if you want privacy (no data sent
to external AI), cost control, or local-only tools.

The state is stored in the config file as `enable_subagent` (bool) plus
`api_keys` and `api_bases` maps. Environment variable override (higher
priority than the file): `ENABLE_SUBAGENT=true` / `false`.

## Subagent API keys

| Provider | Models | Key format | Docs |
|---|---|---|---|
| OpenAI | GPT-4, GPT-3.5, ... | `sk-...` | https://platform.openai.com/docs |
| Anthropic | Claude models | `sk-ant-...` | https://docs.anthropic.com |

Config file location: `~/.subagent_config.json`
(Windows: `C:\Users\<username>\.subagent_config.json`).

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

## Claude Desktop integration

The wizard auto-detects the Claude Desktop config at
`%APPDATA%\Claude\claude_desktop_config.json` (Windows) or
`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS).
Manual alternative: `python -m mcp_server.cli.config --claude`.
Restart Claude Desktop afterwards.

## CLI options

| Flag | Description |
|---|---|
| `--provider` | AI provider (`openai`, `anthropic`) |
| `--api-key` | provider API key |
| `--api-base` | custom API base URL |
| `--skip-deps` | skip dependency installation |
| `--skip-claude` | skip Claude Desktop configuration |
| `--no-color` | disable colored output |

## Config precedence (high → low)

1. Environment variables: `OPENAI_API_KEY`, `OPENAI_API_BASE`,
   `ANTHROPIC_API_KEY`, `ANTHROPIC_API_BASE`
2. Config file: `~/.subagent_config.json`
3. Defaults

## Verify

1. The wizard prints a configuration summary when done.
2. `python examples/subagent_config_example.py`
3. Start the server: `oh-my-mcp` (or `python -m mcp_server.main`).

## FAQ

- **Python too old** — 3.12+ required; upgrade or use pyenv/conda.
- **uv vs pip** — the script prefers uv and falls back to pip.
  Install uv: `irm https://astral.sh/uv/install.ps1 | iex` (Windows) or
  `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux).
- **Change saved config** — re-run the script or edit `~/.subagent_config.json`.
- **File permissions** — the config file is set to `0o600` on Unix automatically.
- **Claude Desktop not picking it up** — check the config path, validate JSON
  (`python -m json.tool`), restart Claude Desktop.
- **Get API keys** —
  [OpenAI](https://platform.openai.com/api-keys) /
  [Anthropic](https://console.anthropic.com/settings/keys).

## Troubleshooting

- Dependency install fails: `pip cache purge` or `uv cache clean`, then
  install manually with `pip install -e .` / `uv pip install -e .`.
- Import errors: re-run `uv run configure.py` without `--skip-deps`.
- Unix permission error: `chmod 600 ~/.subagent_config.json`.
- Windows encoding issues: use `--no-color`.
