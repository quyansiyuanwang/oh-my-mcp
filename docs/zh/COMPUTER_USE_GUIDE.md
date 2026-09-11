# Computer Use 使用指南 | AI 桌面控制

oh-my-mcp 的 **Computer Use** 类别让 AI 可以安全地接管电脑:截屏观察屏幕、控制鼠标键盘、操作剪贴板和管理窗口,共 **22 个工具**。

## 目录

- [安装依赖](#安装依赖)
- [工具总览](#工具总览)
- [典型工作流](#典型工作流)
- [安全机制](#安全机制)
- [常见问题](#常见问题)

## 安装依赖

Computer Use 依赖以下库(oh-my-mcp 核心依赖已包含):

```bash
pip install pyautogui mss pyperclip pygetwindow pillow
# 或
pip install oh-my-mcp[computer]
```

如果依赖缺失,工具会返回带安装提示的错误信息,不会导致服务崩溃。
Linux 无显示环境(如 CI/headless 服务器)下导入会自动降级为不可用状态。

## 工具总览

### 截屏与屏幕信息(5 个)

| 工具 | 说明 |
|------|------|
| `computer_screenshot` | 截取全屏/区域/指定显示器,保存为 PNG 文件或返回 base64 |
| `computer_get_screen_size` | 获取主显示器分辨率 |
| `computer_get_monitors` | 列出所有显示器及其几何信息 |
| `computer_get_pixel_color` | 获取某坐标像素的 RGB/十六进制颜色 |
| `computer_locate_on_screen` | 在屏幕上查找参考图片,返回中心坐标(视觉定位的关键) |

### 鼠标控制(5 个)

| 工具 | 说明 |
|------|------|
| `computer_mouse_move` | 移动光标(绝对坐标或相对偏移) |
| `computer_mouse_click` | 单击/双击,支持左/右/中键 |
| `computer_mouse_drag` | 从一个位置拖拽到另一个位置 |
| `computer_mouse_scroll` | 垂直/水平滚轮滚动 |
| `computer_mouse_get_position` | 获取当前光标位置 |

### 键盘输入(3 个)

| 工具 | 说明 |
|------|------|
| `computer_type_text` | 向当前聚焦窗口输入文本 |
| `computer_press_key` | 按键(enter、esc、tab、f5 等) |
| `computer_hotkey` | 组合键,如 `ctrl+c`、`ctrl+shift+esc` |

### 剪贴板(2 个)

| 工具 | 说明 |
|------|------|
| `computer_clipboard_read` | 读取剪贴板文本 |
| `computer_clipboard_write` | 写入文本到剪贴板 |

### 窗口管理(5 个)

| 工具 | 说明 |
|------|------|
| `computer_list_windows` | 列出打开的窗口(标题/位置/大小/状态) |
| `computer_focus_window` | 按标题子串激活窗口 |
| `computer_get_window_info` | 查询窗口详细信息 |
| `computer_resize_window` | 调整窗口大小 |
| `computer_move_window` | 移动窗口位置 |

### 安全配置(2 个)

| 工具 | 说明 |
|------|------|
| `computer_config_get` | 查看配置及各依赖可用性 |
| `computer_config_set` | 设置动作间隔(PAUSE)、紧急停止开关(FAILSAFE)、截图保存目录 |

## 典型工作流

AI 操作桌面通常遵循 **观察 → 定位 → 操作 → 验证** 循环:

```
1. computer_screenshot                  # 截屏观察当前界面
2. computer_locate_on_screen(按钮图片)  # 定位目标元素坐标
3. computer_mouse_click(x=600, y=350)   # 点击
4. computer_type_text("hello")          # 输入内容
5. computer_press_key("enter")          # 提交
6. computer_screenshot                  # 再次截屏验证结果
```

窗口操作示例:

```
1. computer_list_windows                 # 查看有哪些窗口
2. computer_focus_window("记事本")        # 激活目标窗口
3. computer_resize_window("记事本", 1024, 768)
4. computer_type_text("由 AI 输入的内容")
```

剪贴板粘贴大段文本(比逐键输入更快更可靠):

```
1. computer_clipboard_write("长文本...")
2. computer_hotkey("ctrl+v")
```

## 安全机制

- **FAILSAFE 紧急停止(默认开启)**:自动化过程中把鼠标猛甩到屏幕**左上角 (0,0)**,pyautogui 会立即抛出异常中止后续动作,防止 AI 失控。可通过 `computer_config_set(failsafe=False)` 关闭,但不建议。
- **动作间隔**:每个 pyautogui 动作后默认暂停 0.1 秒(`computer_config_set(pause=0.3)` 可调),给系统和人留出反应时间。
- **主开关**:在 `src/mcp_server/tools/computer/config.yaml` 中设置 `enabled: false` 可整体禁用该类别。
- **路径安全**:截图保存路径经过 sanitize_path 处理,防止路径遍历。

## 常见问题

**Q: 提示 "pyautogui is not installed"?**
A: 运行 `pip install pyautogui mss pyperclip pygetwindow pillow` 或 `pip install oh-my-mcp[computer]`。

**Q: Linux 服务器上工具不可用?**
A: pyautogui 需要 X 显示环境(暂不支持 Wayland)。headless 环境下依赖导入会自动降级,工具会返回不可用提示。

**Q: `computer_locate_on_screen` 找图失败?**
A: 参考图应来自相同分辨率/缩放下的截图。confidence 匹配(< 1.0)需要安装 `opencv-python`。

**Q: 截图想直接保存文件而不是 base64?**
A: 传 `save_path` 参数;或先用 `computer_config_set(screenshot_dir="D:/shots")` 设定默认目录,之后只传 `filename`。
