# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-02-11

### Added

- **Persistent Configuration Management**: New configuration system for API credentials
  - `SubagentConfig` class for persistent credential storage (~/.subagent_config.json)
  - Three new MCP tools: `subagent_config_set`, `subagent_config_get`, `subagent_config_list`
  - Automatic file permissions (600) for config file on Unix/Linux/macOS
  - Configuration priority: Environment Variables > Config File > Defaults
  - Sensitive data masking in all output
  - Support for custom config file paths
  - Per-project configuration support

### Changed

- Updated Subagent tools from 3 to 6 total tools
- Enhanced all AI client classes (OpenAI, Anthropic, ZhipuAI) to use config manager
- Updated SUBAGENT_GUIDE.md with persistent configuration examples
- Updated README.md tool count from 74+ to 77+ tools

### Documentation

- New guide: `docs/SUBAGENT_CONFIG.md` - Complete configuration management guide
- New example: `examples/subagent_config_example.py` - 8 configuration examples
- Updated existing guides with configuration management information

## [0.1.0] - 2026-02-11

### Added

- Initial release of MCP Server
- 95+ practical tools across 10 categories:
  - Compression (5 tools): ZIP/TAR compression and extraction
  - Web & Network (15 tools): web search, page fetching, HTML parsing, downloads
  - File System (12 tools): read, write, search files and directories
  - Data Processing (15 tools): JSON, CSV, XML, YAML, TOML parsing
  - Text Processing (9 tools): regex, encoding, email/URL extraction
  - System (8 tools): system info, CPU/memory monitoring
  - Utilities (10 tools): UUID, hashing, date/time, passwords
  - Python Development (8 tools): code execution, syntax validation
  - UV Package Manager (9 tools): fast package management
  - Pylance/Pyright (4 tools): type checking and diagnostics
- Modular architecture with separate tool modules
- Comprehensive error handling and logging
- Configuration generator for Claude Desktop
- HTTP server for configuration management
- Complete test suite
- Documentation and examples

[0.1.0]: https://github.com/quyansiyuanwang/mcp-server/releases/tag/v0.1.0
