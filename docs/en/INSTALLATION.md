# Installation Guide

English | [中文](../zh/INSTALLATION.md)

## Requirements

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Install

### Option 1: From source with uv (recommended)

```bash
git clone https://github.com/quyansiyuanwang/oh-my-mcp.git
cd oh-my-mcp
uv sync --all-extras
```

### Option 2: With pip

```bash
git clone https://github.com/quyansiyuanwang/oh-my-mcp.git
cd oh-my-mcp
pip install -e .
```

## Verify the installation

```bash
# Show server version info
uv run python -m mcp_server.cli.config --show-config

# Start the MCP server (stdio transport)
uv run python -m mcp_server.main
```

The server registers **141 tools across 10 categories** on startup and logs
each loaded plugin.

## Configure Claude Desktop

### Automatic (recommended)

```bash
# Install the config into Claude Desktop directly
uv run python -m mcp_server.cli.config --claude

# Or start the HTTP config service
uv run python -m mcp_server.cli.config --http-server --port 8765
```

### Manual

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "oh-my-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/oh-my-mcp", "python", "-m", "mcp_server.main"]
    }
  }
}
```

For the interactive setup wizard, run `uv run configure.py`. Details:
[Setup Guide](SETUP_GUIDE.md) (中文).
