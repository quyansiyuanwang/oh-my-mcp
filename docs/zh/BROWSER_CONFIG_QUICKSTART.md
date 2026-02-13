# 浏览器配置快速开始

## 一分钟快速配置

如果您遇到浏览器驱动下载问题（尤其是在中国大陆），运行配置向导：

```bash
cd d:\Developments\oh-my-mcp
python examples/browser_config_wizard.py
```

## 典型问题及解决方案

### 问题1：Chrome 驱动下载失败

**错误信息**：
```
Failed to create Chrome driver. This is often caused by network issues...
```

**解决方案A - 使用 Edge 浏览器（推荐）**：

配置向导中设置默认浏览器为 `edge`，Edge 驱动通常不受网络限制影响。

**解决方案B - 手动下载 ChromeDriver**：

1. 查看 Chrome 版本：Chrome → 设置 → 关于 Chrome
2. 下载对应版本：https://googlechromelabs.github.io/chrome-for-testing/
   - 国内镜像：https://registry.npmmirror.com/binary.html?path=chromedriver/
3. 解压到固定目录（如 `D:\drivers\chromedriver.exe`）
4. 配置向导中输入路径

### 问题2：自动下载失败（网络超时）

**错误信息**：
```
error sending request for url (https://googlechromelabs.github.io/...)
```

**解决方案**：

1. **启用自动兜底**（配置向导中选择 `yes`）
   - Chrome 失败时自动切换到 Edge

2. **配置代理**（如有可用代理）：
   ```bash
   python examples/browser_config_wizard.py
   ```
   在 "代理服务器" 输入代理地址

3. **手动下载驱动**（见问题1解决方案B）

### 问题3：版本不匹配

**错误信息**：
```
ChromeDriver only supports Chrome version 114
```

**原因**：缓存的旧版本驱动

**解决方案**：

手动下载与当前 Chrome 版本匹配的驱动并配置路径。

## 配置验证

运行测试验证配置：

```bash
# 测试浏览器功能
uv run pytest tests/test_browser.py -v

# 测试配置管理
uv run pytest tests/test_browser.py::TestBrowserConfig -v
```

## MCP 工具使用

在 Claude Desktop 中直接使用配置工具：

```javascript
// 查看当前配置
browser_config_get()

// 设置驱动路径
browser_config_set("chrome_driver_path", "D:\\drivers\\chromedriver.exe")

// 切换默认浏览器
browser_config_set("default_browser", "edge")
```

## 配置文件示例

`~/.oh-my-mcp/browser_config.json`：

```json
{
  "driver_paths": {
    "chrome": "D:\\drivers\\chromedriver.exe",
    "edge": "D:\\drivers\\msedgedriver.exe"
  },
  "default_browser": "edge",
  "default_headless": false,
  "proxy": "",
  "auto_fallback": true,
  "screenshot_dir": "~/.oh-my-mcp/screenshots"
}
```

## 更多信息

详细配置指南：[BROWSER_CONFIG_GUIDE.md](BROWSER_CONFIG_GUIDE.md)
