# Browser Automation Configuration

English | [中文](BROWSER_CONFIG.zh.md)

The browser automation plugin supports persistent configuration: driver
paths, default browser, headless mode, proxy, auto-fallback and screenshot
directory — saved to a config file so env vars are not needed every time.

## Config file

`~/.oh-my-mcp/browser_config.json`:

```json
{
  "driver_paths": {
    "chrome": "D:\\drivers\\chromedriver.exe",
    "edge": "D:\\drivers\\msedgedriver.exe"
  },
  "default_browser": "edge",
  "default_headless": false,
  "proxy": "http://proxy.example.com:8080",
  "auto_fallback": true,
  "screenshot_dir": "~/.oh-my-mcp/screenshots"
}
```

Screenshot resolution order: explicit `save_path` → `screenshot_dir` +
`filename` (or an auto timestamped name) → base64 data when neither is set.

## Configuration methods

1. **Interactive wizard (recommended)**:
   `python examples/browser_config_wizard.py`
2. **MCP tools**: `browser_config_get()`, `browser_config_set(key, value)`
   (e.g. `browser_config_set("default_browser", "edge")`),
   `browser_config_reset()`
3. **Manual edit** of the JSON file above
4. **Environment variables (temporary, override the file)**:
   `CHROME_DRIVER_PATH`, `EDGE_DRIVER_PATH`, `HTTPS_PROXY`

## Driver acquisition strategy (high → low)

1. Custom path (env var > config file)
2. Selenium Manager (built into Selenium 4.6+; downloads the matching driver)
3. webdriver-manager fallback download
4. Auto fallback Chrome → Edge (when `auto_fallback: true` and all Chrome
   attempts fail)

## Mainland China network notes

Selenium Manager may fail to reach `googlechromelabs.github.io`. Options:

1. Manually download the driver matching your Chrome version from
   [chrome-for-testing](https://googlechromelabs.github.io/chrome-for-testing/)
   (CN mirror: [npmmirror](https://registry.npmmirror.com/binary.html?path=chromedriver/))
   and configure its path.
2. Use Edge (`default_browser: "edge"`) — EdgeDriver downloads usually work.
3. Configure a proxy.
4. Enable auto fallback (recommended).

## Verify

```bash
uv run pytest tests/test_browser.py -v                        # all browser tests
uv run pytest tests/test_browser.py::TestBrowserConfig -v     # config only
```

```python
from mcp_server.tools.browser.browser_config import get_browser_config
print(get_browser_config().get_all_settings())
```

## FAQ

- **Where is the config?** `browser_config_get()` shows `config_file`.
- **Config not taking effect?** Environment variables override the file.
- **Chrome always fails?** Ensure `auto_fallback: true`, or set a manual
  driver path, or switch to Edge.
