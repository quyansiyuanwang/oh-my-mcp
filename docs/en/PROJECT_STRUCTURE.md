# Project Structure

English | [中文](../zh/PROJECT_STRUCTURE.md)

oh-my-mcp — an MCP server with **141 tools across 10 categories**.

```
oh-my-mcp/
├── pyproject.toml               # Dependencies & tool configuration
├── uv.lock                      # Locked dependency versions (CI reproducibility)
├── configure.py                 # Interactive setup wizard
├── README.md                    # Project documentation
│
├── 📂 src/                      # Source code
│   └── 📂 mcp_server/
│       ├── main.py              # Server entry point (FastMCP)
│       ├── utils.py             # Infrastructure: errors, paths, file IO, retry
│       ├── command_executor.py  # Hardened subprocess execution
│       ├── 📂 cli/              # Configuration generator CLI
│       │   ├── __init__.py
│       │   └── config.py        # Claude Desktop / HTTP config endpoints
│       └── 📂 tools/            # Tool plugins (10 categories, auto-discovered)
│           ├── __init__.py      # Plugin discovery (incl. frozen mode)
│           ├── registry.py      # @tool_handler decorator & ToolPlugin
│           ├── search_engine.py # Web search backend
│           ├── subagent_config.py # Subagent credential manager
│           ├── 📂 compression/  # 📦 Compression (5 tools)
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 web/          # 🌐 Web & Network (18 tools)
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 file/         # 📁 File System (13 tools)
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 data/         # 📊 Data Processing (15 tools)
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 text/         # 📝 Text Processing (9 tools)
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 system/       # 💻 System (8 tools)
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 utility/      # 🛠️ Utilities (10 tools)
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 subagent/     # 🤖 AI Orchestration (6 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   └── handlers.py
│           ├── 📂 browser/      # 🌐 Browser Automation (33 tools)
│           │   ├── __init__.py
│           │   ├── config.yaml
│           │   ├── browser_config.py
│           │   ├── session_manager.py
│           │   └── handlers.py
│           ├── 📂 computer/     # 🖥️ Computer Use (25 tools)
│           └── 📂 execution/    # Command Execution (4 tools)
│               ├── __init__.py
│               ├── config.yaml
│               ├── computer_manager.py
│               └── handlers.py
│
├── 📂 scripts/                  # Automation scripts
│   ├── 📂 build/                # PyInstaller packaging (build.py)
│   └── 📂 docs/                 # Documentation generator (generate_docs.py)
│
├── 📂 tests/                    # Pytest suite
│   ├── conftest.py              # Shared fixtures
│   ├── test_<category>.py       # Unit tests per plugin
│   ├── test_*_scenarios.py      # Complex scenario tests
│   └── test_docgen.py           # Documentation generator tests
│
├── 📂 docs/                     # Documentation (bilingual, see docs/README.md)
│   ├── 📂 en/                   # English docs
│   └── 📂 zh/                   # Chinese docs
│
├── 📂 examples/                 # Example scripts
└── 📂 .github/                  # CI workflows & release assets
    ├── 📂 workflows/            # lint.yml, tests.yml, build-release.yml
    └── 📂 assets/               # USAGE.md, RELEASE_NOTES.md templates
```

## Key conventions

- **Plugin discovery**: any `tools/` subdirectory with a `config.yaml` is a
  category; counts and docs are generated from it.
- **Tests**: unit tests per category use the `MockMCP` pattern; scenario suites
  cover security (zip-slip, zip bombs), malformed inputs and cross-platform
  behavior; all hardware interaction is mocked.
- **Generated docs**: content between `<!-- DOCGEN:...:start/end -->` markers
  must not be edited by hand — run `python scripts/docs/generate_docs.py --write`.
