# Browser Configuration Quick Start

English | [中文](BROWSER_CONFIG_QUICKSTART.zh.md)

Hitting browser driver download problems (especially in mainland China)?
Run the interactive wizard — it solves the common cases in one minute:

```bash
python examples/browser_config_wizard.py
```

## Typical problems

### 1. Chrome driver download failed

```
Failed to create Chrome driver. This is often caused by network issues...
```

- **Option A (recommended): use Edge** — set `default_browser` to `edge` in
  the wizard; EdgeDriver downloads are usually not blocked.
- **Option B: manual ChromeDriver** — check your Chrome version
  (Settings → About Chrome), download the matching driver from
  [chrome-for-testing](https://googlechromelabs.github.io/chrome-for-testing/)
  (CN mirror: [npmmirror](https://registry.npmmirror.com/binary.html?path=chromedriver/)),
  extract to a fixed directory and enter the path in the wizard.

### 2. Auto download timed out

```
error sending request for url (https://googlechromelabs.github.io/...)
```

Enable auto fallback, configure a proxy, or download manually (see above).

### 3. Version mismatch

```
ChromeDriver only supports Chrome version 114
```

A cached old driver is being used — download the driver matching your
current Chrome version and configure its path.

## Verify

```bash
uv run pytest tests/test_browser.py -v
uv run pytest tests/test_browser.py::TestBrowserConfig -v
```

In Claude Desktop:

```
browser_config_get()
browser_config_set("chrome_driver_path", "D:\\drivers\\chromedriver.exe")
browser_config_set("default_browser", "edge")
```

Config file: `~/.oh-my-mcp/browser_config.json` — see the full
[Browser Configuration Guide](BROWSER_CONFIG.md).
