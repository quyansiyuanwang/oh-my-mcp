"""
Computer use tool handlers.

Provides tools for AI-driven desktop control:
- Screen capture and inspection (screenshot, size, monitors, pixel color, image locate)
- Mouse control (move, click, drag, scroll, position)
- Keyboard input (typing, key presses, hotkey combinations)
- Clipboard access (read/write)
- Window management (list, focus, info, resize, move)
- Safety configuration (pause interval, failsafe, screenshot directory)

All hardware-touching libraries are accessed through the `computer_manager`
module (never via local imports) so tests can substitute fakes, and missing
dependencies produce actionable error payloads instead of crashing the server.
"""

import json
import time
from pathlib import Path
from typing import Any

from mcp_server.tools.computer import computer_manager as _lib
from mcp_server.tools.computer.computer_manager import (
    _check_mss_available,
    _check_pyautogui_available,
    _check_pyperclip_available,
    computer_manager,
)
from mcp_server.tools.registry import tool_handler
from mcp_server.utils import (
    ComputerUseError,
    ValidationError,
    error_json,
    logger,
    sanitize_path,
)


def _save_or_encode(image: Any, save_path: str, filename: str) -> dict[str, Any]:
    """Save a captured image to disk or encode it as base64 for inline return."""
    if save_path or computer_manager.screenshot_dir:
        if save_path:
            out = sanitize_path(save_path)
        else:
            directory = sanitize_path(computer_manager.screenshot_dir)
            directory.mkdir(parents=True, exist_ok=True)
            name = filename or f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
            out = directory / name
        if out.suffix.lower() != ".png":
            out = out.with_suffix(".png")
        out.parent.mkdir(parents=True, exist_ok=True)
        image.save(out, format="PNG")
        return {
            "saved_to": str(out),
            "size_bytes": out.stat().st_size,
            "width": image.size[0],
            "height": image.size[1],
        }
    return {
        "format": "png",
        "base64": computer_manager.image_to_base64(image),
        "width": image.size[0],
        "height": image.size[1],
    }


# ---------------------------------------------------------------------------
# Screen / capture tools
# ---------------------------------------------------------------------------


@tool_handler
def computer_screenshot(
    save_path: str = "",
    filename: str = "",
    region: str = "",
    monitor: int = 0,
) -> str:
    """
    Capture the screen and return it as a saved PNG file or base64-encoded PNG.

    Args:
        save_path: Full path to save the PNG. If empty, uses the configured
            screenshot_dir, or returns base64 when that is also empty.
        filename: File name to use when saving into screenshot_dir.
        region: Optional crop "[x, y, width, height]" on the primary display.
        monitor: 0 = primary display, or 1-based index of a specific display.

    Returns:
        JSON string with saved_to/size_bytes or format/base64
    """
    try:
        region_list: list[int] | None = None
        if region:
            try:
                region_list = [int(v) for v in json.loads(region)]
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                raise ValidationError('region must be a JSON list like "[0, 0, 800, 600]"') from e

        image = computer_manager.capture_image(region=region_list, monitor=monitor)
        payload = _save_or_encode(image, save_path, filename)
        result: dict[str, Any] = {"success": True}
        result.update(payload)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except (ValidationError, ComputerUseError) as e:
        logger.warning(f"computer_screenshot failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_screenshot unexpected error: {e}")
        return error_json(f"Screenshot failed: {e}")


@tool_handler
def computer_get_screen_size() -> str:
    """
    Get the size of the primary display in pixels.

    Returns:
        JSON string with width and height
    """
    try:
        _check_pyautogui_available()
        size = computer_manager.capture_image().size
        return json.dumps({"success": True, "width": size[0], "height": size[1]}, indent=2)
    except ComputerUseError as e:
        logger.warning(f"computer_get_screen_size failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_get_screen_size unexpected error: {e}")
        return error_json(f"Failed to get screen size: {e}")


@tool_handler
def computer_get_monitors() -> str:
    """
    List all connected displays with their geometry.

    Returns:
        JSON string with monitor list (index 0 is the virtual full desktop)
    """
    try:
        _check_mss_available()
        with _lib.mss.MSS() as sct:
            monitors = [{k: v for k, v in m.items() if k != "__handle__"} for m in sct.monitors]
        return json.dumps(
            {"success": True, "count": len(monitors) - 1, "monitors": monitors}, indent=2
        )
    except ComputerUseError as e:
        logger.warning(f"computer_get_monitors failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_get_monitors unexpected error: {e}")
        return error_json(f"Failed to list monitors: {e}")


@tool_handler
def computer_get_pixel_color(x: int, y: int) -> str:
    """
    Get the RGB color of a pixel on the primary display.

    Args:
        x: X coordinate
        y: Y coordinate

    Returns:
        JSON string with rgb list and hex color
    """
    try:
        _check_pyautogui_available()
        pixel = computer_manager.capture_image().getpixel((x, y))
        rgb = list(pixel[:3])
        return json.dumps(
            {
                "success": True,
                "x": x,
                "y": y,
                "rgb": rgb,
                "hex": f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
            },
            indent=2,
        )
    except ComputerUseError as e:
        logger.warning(f"computer_get_pixel_color failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_get_pixel_color unexpected error: {e}")
        return error_json(f"Failed to get pixel color: {e}")


@tool_handler
def computer_locate_on_screen(
    image_path: str, confidence: float = 0.9, grayscale: bool = False
) -> str:
    """
    Locate an image on the screen and return its center coordinates.

    Useful for finding UI elements by a reference screenshot. Confidence
    matching requires opencv-python; without it, exact pixel matching is used.

    Args:
        image_path: Path to a small reference PNG to search for
        confidence: Matching confidence 0-1 (default 0.9, needs opencv-python)
        grayscale: Match in grayscale for speed (default False)

    Returns:
        JSON string with center x/y and the bounding box
    """
    try:
        _check_pyautogui_available()
        ref = sanitize_path(image_path)
        if not ref.is_file():
            raise ValidationError(f"Reference image not found: {image_path}")

        box, note = _locate_once(ref, confidence, grayscale)
        if box is None:
            return json.dumps(
                {"success": False, "found": False, "message": "Image not found on screen"}
            )

        center = _lib.pyautogui.center(box)
        result: dict[str, Any] = {
            "success": True,
            "found": True,
            "center": {"x": center.x, "y": center.y},
            "box": {
                "left": box.left,
                "top": box.top,
                "width": box.width,
                "height": box.height,
            },
        }
        if note:
            result["note"] = note
        return json.dumps(result, indent=2)
    except (ValidationError, ComputerUseError) as e:
        logger.warning(f"computer_locate_on_screen failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_locate_on_screen unexpected error: {e}")
        return error_json(
            f"Image location failed: {e}. Note: confidence matching may require opencv-python."
        )


# ---------------------------------------------------------------------------
# Mouse tools
# ---------------------------------------------------------------------------


@tool_handler
def computer_mouse_move(x: int, y: int, duration: float = 0.25, relative: bool = False) -> str:
    """
    Move the mouse cursor.

    Args:
        x: Target X (or X offset when relative=True)
        y: Target Y (or Y offset when relative=True)
        duration: Seconds the movement takes (default 0.25)
        relative: Move relative to the current position (default False)

    Returns:
        JSON string with the resulting cursor position
    """
    try:
        _check_pyautogui_available()
        if relative:
            _lib.pyautogui.moveRel(x, y, duration=duration)
        else:
            _lib.pyautogui.moveTo(x, y, duration=duration)
        pos = _lib.pyautogui.position()
        return json.dumps({"success": True, "x": pos.x, "y": pos.y}, indent=2)
    except ComputerUseError as e:
        logger.warning(f"computer_mouse_move failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_mouse_move unexpected error: {e}")
        return error_json(f"Mouse move failed: {e}")


@tool_handler
def computer_mouse_click(
    x: int = -1, y: int = -1, button: str = "left", clicks: int = 1, interval: float = 0.1
) -> str:
    """
    Click a mouse button, optionally after moving to a position.

    Args:
        x: X coordinate to move to first (-1 = click at current position)
        y: Y coordinate to move to first (-1 = click at current position)
        button: left, right, or middle (default left)
        clicks: Number of clicks; 2 for double-click (default 1)
        interval: Seconds between clicks (default 0.1)

    Returns:
        JSON string with the click details
    """
    try:
        _check_pyautogui_available()
        if button not in ("left", "right", "middle"):
            raise ValidationError(f"Invalid button: {button}. Use left, right, or middle.")
        if clicks < 1:
            raise ValidationError("clicks must be >= 1")

        kwargs: dict[str, Any] = {"button": button, "clicks": clicks, "interval": interval}
        if x >= 0 and y >= 0:
            kwargs["x"] = x
            kwargs["y"] = y
        _lib.pyautogui.click(**kwargs)
        pos = _lib.pyautogui.position()
        return json.dumps(
            {"success": True, "button": button, "clicks": clicks, "x": pos.x, "y": pos.y},
            indent=2,
        )
    except (ValidationError, ComputerUseError) as e:
        logger.warning(f"computer_mouse_click failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_mouse_click unexpected error: {e}")
        return error_json(f"Mouse click failed: {e}")


@tool_handler
def computer_mouse_drag(
    start_x: int = -1,
    start_y: int = -1,
    end_x: int = 0,
    end_y: int = 0,
    duration: float = 0.5,
    button: str = "left",
) -> str:
    """
    Drag from one position to another (or drag the current position).

    Args:
        start_x: X to move to and press down (-1 = drag from current position)
        start_y: Y to move to and press down (-1 = drag from current position)
        end_x: X to drag to
        end_y: Y to drag to
        duration: Seconds the drag takes (default 0.5)
        button: Mouse button to hold (default left)

    Returns:
        JSON string with start and end positions
    """
    try:
        _check_pyautogui_available()
        if button not in ("left", "right", "middle"):
            raise ValidationError(f"Invalid button: {button}. Use left, right, or middle.")

        if start_x >= 0 and start_y >= 0:
            _lib.pyautogui.moveTo(start_x, start_y, duration=0.1)
        else:
            pos = _lib.pyautogui.position()
            start_x, start_y = pos.x, pos.y
        _lib.pyautogui.dragTo(end_x, end_y, duration=duration, button=button)
        return json.dumps(
            {
                "success": True,
                "start": {"x": start_x, "y": start_y},
                "end": {"x": end_x, "y": end_y},
                "button": button,
            },
            indent=2,
        )
    except (ValidationError, ComputerUseError) as e:
        logger.warning(f"computer_mouse_drag failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_mouse_drag unexpected error: {e}")
        return error_json(f"Mouse drag failed: {e}")


@tool_handler
def computer_mouse_scroll(amount: int, x: int = -1, y: int = -1, horizontal: bool = False) -> str:
    """
    Scroll the mouse wheel.

    Args:
        amount: Clicks to scroll; positive scrolls up/right, negative down/left
        x: X coordinate to move to first (-1 = scroll at current position)
        y: Y coordinate to move to first (-1 = scroll at current position)
        horizontal: Perform horizontal scroll instead of vertical (default False)

    Returns:
        JSON string confirming the scroll
    """
    try:
        _check_pyautogui_available()
        kwargs: dict[str, Any] = {}
        if x >= 0:
            kwargs["x"] = x
        if y >= 0:
            kwargs["y"] = y
        if horizontal:
            _lib.pyautogui.hscroll(amount, **kwargs)
        else:
            _lib.pyautogui.scroll(amount, **kwargs)
        return json.dumps({"success": True, "amount": amount, "horizontal": horizontal}, indent=2)
    except ComputerUseError as e:
        logger.warning(f"computer_mouse_scroll failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_mouse_scroll unexpected error: {e}")
        return error_json(f"Mouse scroll failed: {e}")


@tool_handler
def computer_mouse_get_position() -> str:
    """
    Get the current mouse cursor position.

    Returns:
        JSON string with x and y
    """
    try:
        _check_pyautogui_available()
        pos = _lib.pyautogui.position()
        return json.dumps({"success": True, "x": pos.x, "y": pos.y}, indent=2)
    except ComputerUseError as e:
        logger.warning(f"computer_mouse_get_position failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_mouse_get_position unexpected error: {e}")
        return error_json(f"Failed to get mouse position: {e}")


# ---------------------------------------------------------------------------
# Keyboard tools
# ---------------------------------------------------------------------------


@tool_handler
def computer_type_text(text: str, interval: float = 0.0) -> str:
    """
    Type text into the currently focused window.

    Args:
        text: Text to type (into the focused window's input field)
        interval: Seconds to wait between keystrokes (default 0)

    Returns:
        JSON string with the character count typed
    """
    try:
        _check_pyautogui_available()
        _lib.pyautogui.typewrite(text, interval=interval)
        return json.dumps({"success": True, "characters": len(text)}, indent=2)
    except ComputerUseError as e:
        logger.warning(f"computer_type_text failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_type_text unexpected error: {e}")
        return error_json(f"Typing failed: {e}")


@tool_handler
def computer_press_key(key: str, presses: int = 1, interval: float = 0.1) -> str:
    """
    Press a keyboard key (e.g. enter, esc, tab, f5, space, a).

    Args:
        key: Key name per pyautogui KEYBOARD_KEYS (e.g. enter, esc, tab)
        presses: Number of presses (default 1)
        interval: Seconds between presses (default 0.1)

    Returns:
        JSON string confirming the key press
    """
    try:
        _check_pyautogui_available()
        if key not in _lib.pyautogui.KEYBOARD_KEYS:
            raise ValidationError(
                f"Unknown key: {key}. See pyautogui.KEYBOARD_KEYS for valid names."
            )
        if presses < 1:
            raise ValidationError("presses must be >= 1")
        _lib.pyautogui.press(key, presses=presses, interval=interval)
        return json.dumps({"success": True, "key": key, "presses": presses}, indent=2)
    except (ValidationError, ComputerUseError) as e:
        logger.warning(f"computer_press_key failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_press_key unexpected error: {e}")
        return error_json(f"Key press failed: {e}")


@tool_handler
def computer_hotkey(keys: str) -> str:
    """
    Press a hotkey combination (e.g. "ctrl+c", "ctrl+shift+esc", "alt+f4").

    Args:
        keys: Plus-separated key combination, pressed in order and released in reverse

    Returns:
        JSON string confirming the combination
    """
    try:
        _check_pyautogui_available()
        combo = [k.strip() for k in keys.split("+") if k.strip()]
        if not combo:
            raise ValidationError("keys must be a plus-separated combination like ctrl+c")
        invalid = [k for k in combo if k not in _lib.pyautogui.KEYBOARD_KEYS]
        if invalid:
            raise ValidationError(
                f"Unknown key(s): {', '.join(invalid)}. See pyautogui.KEYBOARD_KEYS."
            )
        _lib.pyautogui.hotkey(*combo)
        return json.dumps({"success": True, "keys": combo}, indent=2)
    except (ValidationError, ComputerUseError) as e:
        logger.warning(f"computer_hotkey failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_hotkey unexpected error: {e}")
        return error_json(f"Hotkey failed: {e}")


# ---------------------------------------------------------------------------
# Clipboard tools
# ---------------------------------------------------------------------------


@tool_handler
def computer_clipboard_read() -> str:
    """
    Read the current clipboard text content.

    Returns:
        JSON string with the clipboard text
    """
    try:
        _check_pyperclip_available()
        content = _lib.pyperclip.paste()
        return json.dumps(
            {"success": True, "content": content, "length": len(content or "")},
            indent=2,
            ensure_ascii=False,
        )
    except ComputerUseError as e:
        logger.warning(f"computer_clipboard_read failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_clipboard_read unexpected error: {e}")
        return error_json(f"Clipboard read failed: {e}")


@tool_handler
def computer_clipboard_write(text: str) -> str:
    """
    Write text to the clipboard.

    Args:
        text: Text to place on the clipboard

    Returns:
        JSON string confirming the write
    """
    try:
        _check_pyperclip_available()
        _lib.pyperclip.copy(text)
        return json.dumps({"success": True, "length": len(text)}, indent=2)
    except ComputerUseError as e:
        logger.warning(f"computer_clipboard_write failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_clipboard_write unexpected error: {e}")
        return error_json(f"Clipboard write failed: {e}")


# ---------------------------------------------------------------------------
# Window management tools
# ---------------------------------------------------------------------------


@tool_handler
def computer_list_windows(title_filter: str = "") -> str:
    """
    List open windows with title, geometry, and state.

    Args:
        title_filter: Only list windows whose title contains this substring
            (case-insensitive; empty lists all)

    Returns:
        JSON string with the window list
    """
    try:
        windows = computer_manager.list_windows(title_filter)
        return json.dumps(
            {"success": True, "count": len(windows), "windows": windows},
            indent=2,
            ensure_ascii=False,
        )
    except ComputerUseError as e:
        logger.warning(f"computer_list_windows failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_list_windows unexpected error: {e}")
        return error_json(f"Failed to list windows: {e}")


@tool_handler
def computer_focus_window(title: str) -> str:
    """
    Bring a window to the foreground by title substring.

    Args:
        title: Substring of the window title to activate (case-insensitive)

    Returns:
        JSON string confirming activation
    """
    try:
        window = computer_manager.find_window(title)
        window.activate()
        return json.dumps({"success": True, "focused": window.title}, indent=2)
    except ComputerUseError as e:
        logger.warning(f"computer_focus_window failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_focus_window unexpected error: {e}")
        return error_json(f"Failed to focus window: {e}")


@tool_handler
def computer_get_window_info(title: str) -> str:
    """
    Get detailed information about a window by title substring.

    Args:
        title: Substring of the window title (case-insensitive)

    Returns:
        JSON string with title, geometry, and state
    """
    try:
        window = computer_manager.find_window(title)
        box = window.box
        return json.dumps(
            {
                "success": True,
                "title": window.title,
                "left": box.left,
                "top": box.top,
                "width": box.width,
                "height": box.height,
                "is_active": window.isActive,
                "is_minimized": window.isMinimized,
                "is_maximized": window.isMaximized,
            },
            indent=2,
            ensure_ascii=False,
        )
    except ComputerUseError as e:
        logger.warning(f"computer_get_window_info failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_get_window_info unexpected error: {e}")
        return error_json(f"Failed to get window info: {e}")


@tool_handler
def computer_resize_window(title: str, width: int, height: int) -> str:
    """
    Resize a window by title substring.

    Args:
        title: Substring of the window title (case-insensitive)
        width: New outer width in pixels (includes borders/title bar, so the
            client area will be slightly smaller)
        height: New outer height in pixels

    Returns:
        JSON string confirming the new size
    """
    try:
        if width <= 0 or height <= 0:
            raise ValidationError("width and height must be positive")
        window = computer_manager.find_window(title)
        window.resizeTo(width, height)
        return json.dumps(
            {"success": True, "title": window.title, "width": width, "height": height},
            indent=2,
            ensure_ascii=False,
        )
    except (ValidationError, ComputerUseError) as e:
        logger.warning(f"computer_resize_window failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_resize_window unexpected error: {e}")
        return error_json(f"Failed to resize window: {e}")


@tool_handler
def computer_move_window(title: str, x: int, y: int) -> str:
    """
    Move a window by title substring to a new position.

    Args:
        title: Substring of the window title (case-insensitive)
        x: New left position in pixels
        y: New top position in pixels

    Returns:
        JSON string confirming the new position
    """
    try:
        window = computer_manager.find_window(title)
        window.moveTo(x, y)
        return json.dumps(
            {"success": True, "title": window.title, "x": x, "y": y},
            indent=2,
            ensure_ascii=False,
        )
    except ComputerUseError as e:
        logger.warning(f"computer_move_window failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_move_window unexpected error: {e}")
        return error_json(f"Failed to move window: {e}")


@tool_handler
def computer_minimize_window(title: str) -> str:
    """
    Minimize a window by title substring.

    Args:
        title: Substring of the window title (case-insensitive)

    Returns:
        JSON string confirming the minimization
    """
    try:
        window = computer_manager.find_window(title)
        window.minimize()
        return json.dumps({"success": True, "minimized": window.title}, indent=2)
    except ComputerUseError as e:
        logger.warning(f"computer_minimize_window failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_minimize_window unexpected error: {e}")
        return error_json(f"Failed to minimize window: {e}")


@tool_handler
def computer_maximize_window(title: str) -> str:
    """
    Maximize a window by title substring.

    Args:
        title: Substring of the window title (case-insensitive)

    Returns:
        JSON string confirming the maximization
    """
    try:
        window = computer_manager.find_window(title)
        window.maximize()
        return json.dumps({"success": True, "maximized": window.title}, indent=2)
    except ComputerUseError as e:
        logger.warning(f"computer_maximize_window failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_maximize_window unexpected error: {e}")
        return error_json(f"Failed to maximize window: {e}")


@tool_handler
def computer_wait(duration: float) -> str:
    """
    Wait for a given number of seconds (useful between UI actions while
    applications render or load).

    Args:
        duration: Seconds to wait, 0-60

    Returns:
        JSON string confirming the wait
    """
    try:
        if duration < 0:
            raise ValidationError("duration must be >= 0")
        if duration > 60:
            raise ValidationError("duration must be at most 60 seconds")
        time.sleep(duration)
        return json.dumps({"success": True, "waited": duration}, indent=2)
    except (ValidationError, ComputerUseError) as e:
        logger.warning(f"computer_wait failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_wait unexpected error: {e}")
        return error_json(f"Wait failed: {e}")


# ---------------------------------------------------------------------------
# Configuration tools
# ---------------------------------------------------------------------------


@tool_handler
def computer_config_get() -> str:
    """
    Get the computer use module configuration.

    Returns:
        JSON string with pause interval, failsafe flag, screenshot_dir,
        and dependency availability
    """
    try:
        config = computer_manager.get_config()
        return json.dumps({"success": True, **config}, indent=2)
    except Exception as e:
        logger.error(f"computer_config_get unexpected error: {e}")
        return error_json(f"Failed to get config: {e}")


@tool_handler
def computer_config_set(
    pause: float | None = None,
    failsafe: bool | None = None,
    screenshot_dir: str | None = None,
) -> str:
    """
    Update the computer use module configuration.

    Args:
        pause: Seconds to pause after each pyautogui action (>= 0);
            omit to leave unchanged
        failsafe: Whether moving the mouse to the top-left corner aborts
            automation (safety feature); omit to leave unchanged
        screenshot_dir: Default directory for saving screenshots;
            omit to leave unchanged

    Returns:
        JSON string with the updated configuration
    """
    try:
        config = computer_manager.set_config(
            pause=pause, failsafe=failsafe, screenshot_dir=screenshot_dir
        )
        return json.dumps({"success": True, **config}, indent=2)
    except ComputerUseError as e:
        logger.warning(f"computer_config_set failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_config_set unexpected error: {e}")
        return error_json(f"Failed to set config: {e}")


def _locate_once(image_path: Path, confidence: float, grayscale: bool) -> tuple[Any, str | None]:
    """Single locateOnScreen attempt; returns (box, note)."""
    note = None
    if _lib.opencv_available():
        box = _lib.pyautogui.locateOnScreen(
            str(image_path), confidence=confidence, grayscale=grayscale
        )
    else:
        # Exact pixel match; confidence matching needs OpenCV
        box = _lib.pyautogui.locateOnScreen(str(image_path), grayscale=grayscale)
        note = (
            "OpenCV not installed; used exact pixel matching (confidence ignored). "
            "Install opencv-python for fuzzy matching."
        )
    return box, note


@tool_handler
def computer_wait_for_image(
    image_path: str,
    timeout_seconds: float = 10.0,
    poll_interval: float = 0.5,
    confidence: float = 0.9,
    grayscale: bool = False,
) -> str:
    """
    Poll the screen until a reference image appears (or the timeout expires).

    Useful after clicking a button or launching an app: wait for the expected
    UI state instead of guessing a sleep duration. Confidence matching
    requires opencv-python; without it, exact pixel matching is used.

    Args:
        image_path: Path to a small reference PNG to wait for
        timeout_seconds: Give up after this many seconds (0.5-120, default 10)
        poll_interval: Seconds between attempts (0.1-10, default 0.5)
        confidence: Matching confidence 0-1 (default 0.9, needs opencv-python)
        grayscale: Match in grayscale for speed (default False)

    Returns:
        JSON string with found, center/box (when found), waited seconds and
        the elapsed/timeout outcome
    """
    try:
        _check_pyautogui_available()
        ref = sanitize_path(image_path)
        if not ref.is_file():
            raise ValidationError(f"Reference image not found: {image_path}")
        if not 0.5 <= timeout_seconds <= 120:
            raise ValidationError("timeout_seconds must be between 0.5 and 120")
        if not 0.1 <= poll_interval <= 10:
            raise ValidationError("poll_interval must be between 0.1 and 10")

        started = time.monotonic()
        note = None
        while True:
            box, locate_note = _locate_once(ref, confidence, grayscale)
            note = locate_note
            if box is not None:
                break
            if time.monotonic() - started >= timeout_seconds:
                return json.dumps(
                    {
                        "success": False,
                        "found": False,
                        "timed_out": True,
                        "waited": round(time.monotonic() - started, 2),
                        "message": (f"Image did not appear within {timeout_seconds} seconds"),
                    },
                    indent=2,
                )
            time.sleep(poll_interval)

        center = _lib.pyautogui.center(box)
        result: dict[str, Any] = {
            "success": True,
            "found": True,
            "waited": round(time.monotonic() - started, 2),
            "center": {"x": center.x, "y": center.y},
            "box": {
                "left": box.left,
                "top": box.top,
                "width": box.width,
                "height": box.height,
            },
        }
        if note:
            result["note"] = note
        return json.dumps(result, indent=2)
    except (ValidationError, ComputerUseError) as e:
        logger.warning(f"computer_wait_for_image failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"computer_wait_for_image unexpected error: {e}")
        return error_json(f"Wait for image failed: {e}")
