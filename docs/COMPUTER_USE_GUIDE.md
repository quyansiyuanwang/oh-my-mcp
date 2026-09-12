# Computer Use Guide | AI Desktop Control

English | [中文](COMPUTER_USE_GUIDE.zh.md)

The **Computer Use** category lets an AI safely take over a computer: observe
the screen, control mouse and keyboard, use the clipboard and manage windows —
**25 tools** in total.

## Contents

- [Install dependencies](#install-dependencies)
- [Tool overview](#tool-overview)
- [Typical workflow](#typical-workflow)
- [Safety mechanisms](#safety-mechanisms)
- [FAQ](#faq)

## Install dependencies

oh-my-mcp already ships these as core dependencies; the extra exists for
documentation parity:

```bash
pip install pyautogui mss pyperclip pygetwindow pillow
# or
pip install oh-my-mcp[computer]
```

If a dependency is missing, tools return an actionable error instead of
crashing the server. On headless Linux (no display) the libraries fail to
import and the tools gracefully report unavailability.

## Tool overview

### Screen & capture (5)

| Tool | Description |
|------|-------------|
| `computer_screenshot` | Capture full screen / region / specific monitor, save as PNG or return base64 |
| `computer_get_screen_size` | Primary display resolution |
| `computer_get_monitors` | List all displays with geometry |
| `computer_get_pixel_color` | RGB/hex color at a coordinate |
| `computer_locate_on_screen` | Find a reference image on screen, return center coordinates |

### Mouse (5)

| Tool | Description |
|------|-------------|
| `computer_mouse_move` | Move cursor (absolute or relative) |
| `computer_mouse_click` | Single/double click, left/right/middle button |
| `computer_mouse_drag` | Drag from one position to another |
| `computer_mouse_scroll` | Vertical/horizontal wheel scroll |
| `computer_mouse_get_position` | Current cursor position |

### Keyboard (3)

| Tool | Description |
|------|-------------|
| `computer_type_text` | Type text into the focused window |
| `computer_press_key` | Press a key (enter, esc, tab, f5, ...) |
| `computer_hotkey` | Press a combination, e.g. `ctrl+shift+esc` |

### Clipboard (2)

| Tool | Description |
|------|-------------|
| `computer_clipboard_read` | Read clipboard text |
| `computer_clipboard_write` | Write text to the clipboard |

### Window management (7)

| Tool | Description |
|------|-------------|
| `computer_list_windows` | List visible windows (title/geometry/state) |
| `computer_focus_window` | Activate a window by title substring |
| `computer_get_window_info` | Detailed window information |
| `computer_resize_window` | Resize a window (outer size incl. title bar) |
| `computer_move_window` | Move a window |
| `computer_minimize_window` | Minimize a window |
| `computer_maximize_window` | Maximize a window |

### Utility & configuration (3)

| Tool | Description |
|------|-------------|
| `computer_wait` | Wait 0-60 seconds between UI actions |
| `computer_config_get` | Pause/failsafe/screenshot_dir and dependency availability |
| `computer_config_set` | Update safety configuration |

## Typical workflow

AI desktop control follows an **observe → locate → act → verify** loop:

```
1. computer_screenshot                  # observe the current UI
2. computer_locate_on_screen(button.png) # locate the target element
3. computer_mouse_click(x=600, y=350)   # act
4. computer_type_text("hello")
5. computer_press_key("enter")
6. computer_screenshot                  # verify the result
```

For large text, paste via clipboard instead of typing:

```
1. computer_clipboard_write("long text...")
2. computer_hotkey("ctrl+v")
```

## Safety mechanisms

- **FAILSAFE (on by default)**: slam the mouse into the top-left corner (0,0)
  during automation to abort it immediately. Disable with
  `computer_config_set(failsafe=False)` — not recommended.
- **Action pause**: 0.1s pause after each pyautogui action by default
  (`computer_config_set(pause=0.3)` to increase).
- **Master switch**: set `enabled: false` in
  `src/mcp_server/tools/computer/config.yaml` to disable the whole category.
- **Path safety**: screenshot output paths go through `sanitize_path`.
- **Coordinate semantics**: pyautogui and screenshots share the same logical
  coordinate space; `computer_resize_window` sets the outer window size, so
  the client area is slightly smaller.

## FAQ

**Q: "pyautogui is not installed"?**
A: `pip install pyautogui mss pyperclip pygetwindow pillow` or
`pip install oh-my-mcp[computer]`.

**Q: Tools unavailable on a Linux server?**
A: pyautogui requires an X display (Wayland is not supported). Headless
environments degrade gracefully.

**Q: `computer_locate_on_screen` fails to find the image?**
A: The reference image must come from the same resolution/scaling. Confidence
matching (< 1.0) requires `opencv-python`; without it the tool falls back to
exact pixel matching and says so in the response.

**Q: Save screenshots to files instead of base64?**
A: Pass `save_path`, or set a default directory once with
`computer_config_set(screenshot_dir="D:/shots")` and then pass `filename`.
