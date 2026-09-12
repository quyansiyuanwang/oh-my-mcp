# Setup Guide (Claude Desktop Configuration)

English | [中文](SETUP_GUIDE.zh.md)

Configure oh-my-mcp for your MCP client using `mcp_server.cli.config` —
three ways to choose from.

## Method 1: Install into Claude Desktop (recommended)

```bash
python -m mcp_server.cli.config --claude
```

Auto-detects the Claude Desktop config location, adds the oh-my-mcp server
entry, preserves existing MCP servers and creates missing directories.
Config locations: `%APPDATA%\Claude\claude_desktop_config.json` (Windows),
`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS),
`~/.config/claude/claude_desktop_config.json` (Linux).
Restart Claude Desktop afterwards.

## Method 2: HTTP configuration server

```bash
python -m mcp_server.cli.config --http-server            # port 8765
python -m mcp_server.cli.config --http-server --port 9000
```

| Endpoint | Function | Example |
|---|---|---|
| `GET /config` | MCP config JSON | `curl http://localhost:8765/config` |
| `GET /info` | server info and paths | `curl http://localhost:8765/info` |
| `GET /health` | health check | `curl http://localhost:8765/health` |

Useful for dynamic retrieval, sharing across machines, or config-management
tooling.

## Method 3: Generate a config file

```bash
python -m mcp_server.cli.config                       # writes mcp_config.json
python -m mcp_server.cli.config --output my_config.json
python -m mcp_server.cli.config --show-config
python -m mcp_server.cli.config --server-name my-mcp-tools --output config.json
```

Generated example:

```json
{
  "mcpServers": {
    "oh-my-mcp": {
      "command": "D:\\path\\to\\python.exe",
      "args": ["-m", "mcp_server.main"],
      "env": {},
      "description": "oh-my-mcp - MCP Server with 146 practical tools"
    }
  }
}
```

Copy the content into your MCP client's config file and restart the client.

## Complete workflow

```bash
cd oh-my-mcp
pip install -e .                              # 1. install
python -m mcp_server.cli.config --claude      # 2. configure
python -m mcp_server.main                     # 3. test-run the server
```

## All options

```
--server-name NAME    custom server name (default: oh-my-mcp)
--output FILE, -o     output file path (default: mcp_config.json)
--claude              install to Claude Desktop config
--http-server         run HTTP config server
--port PORT           HTTP server port (default: 8765)
--show-config         print config to terminal
--help, -h            show help
```

## Troubleshooting

- **Claude Desktop config not found** — run `--show-config` and add the
  entry manually.
- **Port already in use** — `--http-server --port 9000`.
- **Wrong Python path** — the config auto-detects the current venv's
  interpreter; edit the `"command"` field in the generated JSON if needed.
