# 浏览器自动化配置指南

## 概述

浏览器自动化插件现已支持持久化配置管理，可以将驱动路径、默认浏览器等设置保存到配置文件中，无需每次手动指定环境变量。

## 配置文件位置

- **Windows**: `C:\Users\<用户名>\.oh-my-mcp\browser_config.json`
- **macOS**: `/Users/<用户名>/.oh-my-mcp/browser_config.json`
- **Linux**: `/home/<用户名>/.oh-my-mcp/browser_config.json`

## 配置选项

### 1. 驱动路径 (driver_paths)

手动下载的浏览器驱动可执行文件路径：

```json
{
  "driver_paths": {
    "chrome": "D:\\drivers\\chromedriver.exe",
    "edge": "D:\\drivers\\msedgedriver.exe"
  }
}
```

### 2. 默认浏览器 (default_browser)

默认使用的浏览器类型（`chrome` 或 `edge`）：

```json
{
  "default_browser": "edge"
}
```

### 3. 无头模式 (default_headless)

默认是否使用无头模式（不显示浏览器窗口）：

```json
{
  "default_headless": false
}
```

### 4. 代理服务器 (proxy)

HTTP/HTTPS 代理服务器地址：

```json
{
  "proxy": "http://proxy.example.com:8080"
}
```

### 5. 自动兜底 (auto_fallback)

当 Chrome 驱动获取失败时，自动切换到 Edge：

```json
{
  "auto_fallback": true
}
```

### 6. 截图保存目录 (screenshot_dir)

浏览器截图的默认保存目录。配置后，截图会自动保存到此目录，文件名含时间戳：

```json
{
  "screenshot_dir": "~/.oh-my-mcp/screenshots"
}
```

截图工具行为：
- 如果指定 `save_path`，保存到指定路径
- 如果指定 `filename` 且配置了 `screenshot_dir`，保存到 `{screenshot_dir}/{filename}`
- 如果只配置了 `screenshot_dir`，自动生成带时间戳的文件名（如 `screenshot_20260213_155800_123.png`）
- 如果都未配置，返回 base64 编码的图片数据

## 配置方式

### 方式1：交互式配置向导（推荐）

运行配置向导，按提示逐步输入配置：

```bash
cd d:\Developments\oh-my-mcp
python examples/browser_config_wizard.py
```

向导会引导您配置：
- Chrome 驱动路径
- Edge 驱动路径
- 默认浏览器
- 无头模式
- 代理服务器
- 自动兜底开关
- 截图保存目录

配置完成后会自动保存到 `~/.oh-my-mcp/browser_config.json`。

### 方式2：使用 MCP 工具配置

如果您已经在 Claude Desktop 中，可以直接使用配置工具：

```javascript
// 查看当前配置
browser_config_get()

// 查看特定配置项
browser_config_get("chrome_driver_path")

// 设置 Chrome 驱动路径
browser_config_set("chrome_driver_path", "D:\\drivers\\chromedriver.exe")

// 设置默认浏览器
browser_config_set("default_browser", "edge")

// 设置代理
browser_config_set("proxy", "http://proxy:8080")

// 设置截图保存目录
browser_config_set("screenshot_dir", "~/.oh-my-mcp/screenshots")

// 重置所有配置
browser_config_reset()
```

### 方式3：手动编辑配置文件

直接创建或编辑 `~/.oh-my-mcp/browser_config.json`：

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

### 方式4：使用环境变量（临时配置）

环境变量优先级**高于配置文件**，适合临时调整：

```bash
# Windows PowerShell
$env:CHROME_DRIVER_PATH = "D:\drivers\chromedriver.exe"
$env:EDGE_DRIVER_PATH = "D:\drivers\msedgedriver.exe"
$env:HTTPS_PROXY = "http://proxy:8080"

# Linux / macOS
export CHROME_DRIVER_PATH="/usr/local/bin/chromedriver"
export EDGE_DRIVER_PATH="/usr/local/bin/msedgedriver"
export HTTPS_PROXY="http://proxy:8080"
```

## 驱动获取策略

驱动获取按以下**优先级顺序**尝试：

1. **自定义路径**（环境变量 > 配置文件）
   - 如果配置了 `CHROME_DRIVER_PATH` 或 `driver_paths.chrome`，直接使用

2. **Selenium Manager**（Selenium 4.6+ 内置）
   - 自动检测浏览器版本并下载匹配的驱动
   - 失败原因：网络问题、防火墙、无法访问 `googlechromelabs.github.io`

3. **webdriver-manager**（第三方库）
   - 备选方案，从不同源下载驱动
   - 也可能因网络问题失败

4. **自动兜底**（仅 Chrome → Edge）
   - 如果 `auto_fallback: true` 且 Chrome 驱动全部失败
   - 自动切换到 Edge 浏览器（Edge 驱动通常更易获取）

## 中国大陆网络环境配置

### 问题：ChromeDriver 下载失败

在中国大陆，Selenium Manager 可能无法访问 `googlechromelabs.github.io` 下载 ChromeDriver。

### 解决方案

**方案1：手动下载并配置路径**

1. 查看 Chrome 版本：打开 Chrome → 设置 → 关于 Chrome → 记录版本号（如 144.0.7559.133）

2. 下载匹配的 ChromeDriver：
   - 官方：https://googlechromelabs.github.io/chrome-for-testing/
   - 国内镜像：https://registry.npmmirror.com/binary.html?path=chromedriver/

3. 解压到固定目录（如 `D:\drivers\chromedriver.exe`）

4. 运行配置向导：
   ```bash
   python examples/browser_config_wizard.py
   ```
   在 "Chrome 驱动路径" 输入：`D:\drivers\chromedriver.exe`

**方案2：使用 Edge 浏览器**

Edge 浏览器的驱动下载通常不受影响：

```bash
python examples/browser_config_wizard.py
```

设置 "默认浏览器" 为 `edge`。

**方案3：配置代理**

如果有可用的 HTTP(S) 代理：

```bash
python examples/browser_config_wizard.py
```

在 "代理服务器" 输入代理地址（如 `http://proxy.example.com:8080`）。

或设置环境变量：

```bash
# Windows PowerShell
$env:HTTPS_PROXY = "http://proxy:8080"

# Linux / macOS
export HTTPS_PROXY="http://proxy:8080"
```

**方案4：启用自动兜底（推荐）**

配置向导中确保 "自动兜底" 设置为 `yes`。这样即使 Chrome 失败，也会自动尝试 Edge。

## 配置优先级

完整的配置优先级链（从高到低）：

```
环境变量 (CHROME_DRIVER_PATH, EDGE_DRIVER_PATH, HTTPS_PROXY)
    ↓
配置文件 (~/.oh-my-mcp/browser_config.json)
    ↓
Selenium Manager 自动下载
    ↓
webdriver-manager 自动下载
    ↓
自动兜底（Chrome → Edge）
```

## 验证配置

运行测试以验证浏览器配置是否正常：

```bash
# 运行所有浏览器测试
uv run pytest tests/test_browser.py -v

# 仅测试配置功能
uv run pytest tests/test_browser.py::TestBrowserConfig -v
```

或在 Python 中测试：

```python
from mcp_server.tools.browser.browser_config import get_browser_config

config = get_browser_config()
print("当前配置:")
print(config.get_all_settings())
```

## 示例代码

参考示例文件：
- **配置向导**：`examples/browser_config_wizard.py`
- **使用示例**：`examples/browser_usage_example.py`

## 常见问题

### Q: 配置文件在哪里？

A: 运行 `browser_config_get()` 可以看到 `config_file` 路径。

### Q: 为什么配置不生效？

A: 检查环境变量是否覆盖了配置文件。环境变量优先级更高。

### Q: 如何临时禁用配置？

A: 使用环境变量覆盖，或运行 `browser_config_reset()` 重置。

### Q: Chrome 总是失败，怎么办？

A: 
1. 确认 `auto_fallback: true`（自动切换 Edge）
2. 或手动下载 ChromeDriver 并配置路径
3. 或直接使用 Edge 浏览器

### Q: 配置文件权限问题？

A: Unix/Linux/macOS 系统下，配置文件自动设置为 `600`（仅所有者可读写）。Windows 无此限制。

## 技术细节

- **配置格式**：JSON
- **编码**：UTF-8（支持中文）
- **配置类**：`BrowserConfig`（单例模式）
- **测试覆盖**：51项测试全部通过
- **向后兼容**：配置可选，未配置时自动下载驱动
