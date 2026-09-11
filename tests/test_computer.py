#!/usr/bin/env python3
"""Tests for computer use tools (screen/mouse/keyboard/clipboard/windows).

All hardware-touching libraries are replaced with fakes patched onto the
`computer_manager` module, so the suite never moves a real mouse or reads
the real screen (and runs on headless CI).
"""

import base64
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import computer

LIB = "mcp_server.tools.computer.computer_manager"


class MockMCP:
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


MOCK_MCP = MockMCP()
computer.register_tools(MOCK_MCP)
T = MOCK_MCP.tools


class MockPoint:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class MockBox:
    def __init__(self, left: int, top: int, width: int, height: int) -> None:
        self.left = left
        self.top = top
        self.width = width
        self.height = height


class MockImage:
    def __init__(self, width: int = 800, height: int = 600) -> None:
        self.size = (width, height)
        self.saved_to: str | None = None

    def save(self, path: Any, format: str = "PNG") -> None:  # noqa: ARG002
        data = b"\x89PNG-mock-data"
        if hasattr(path, "write"):
            path.write(data)
        else:
            self.saved_to = str(path)
            Path(path).write_bytes(data)

    def getpixel(self, xy: tuple[int, int]) -> tuple[int, int, int, int]:
        return (10, 20, 30, 255)


class MockPyAutoGUI:
    KEYBOARD_KEYS = [
        "enter",
        "esc",
        "tab",
        "space",
        "shift",
        "ctrl",
        "alt",
        "a",
        "b",
        "c",
        "s",
        "f5",
    ]

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []
        self.pos = MockPoint(100, 200)
        self.FAILSAFE = True
        self.PAUSE = 0.1

    def _record(self, name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        self.calls.append((name, args, kwargs))

    def moveTo(self, x: int, y: int, duration: float = 0.0, **kw: Any) -> None:
        self._record("moveTo", (x, y), kw | {"duration": duration})
        self.pos = MockPoint(x, y)

    def moveRel(self, x: int, y: int, duration: float = 0.0, **kw: Any) -> None:
        self._record("moveRel", (x, y), kw | {"duration": duration})
        self.pos = MockPoint(self.pos.x + x, self.pos.y + y)

    def click(self, **kw: Any) -> None:
        self._record("click", (), kw)
        self.pos = MockPoint(kw.get("x", self.pos.x), kw.get("y", self.pos.y))

    def dragTo(self, x: int, y: int, duration: float = 0.0, button: str = "left") -> None:
        self._record("dragTo", (x, y), {"duration": duration, "button": button})
        self.pos = MockPoint(x, y)

    def scroll(self, amount: int, x: int | None = None, y: int | None = None) -> None:
        self._record("scroll", (amount,), {"x": x, "y": y})

    def hscroll(self, amount: int, x: int | None = None, y: int | None = None) -> None:
        self._record("hscroll", (amount,), {"x": x, "y": y})

    def typewrite(self, text: str, interval: float = 0.0) -> None:
        self._record("typewrite", (text,), {"interval": interval})

    def press(self, key: str, presses: int = 1, interval: float = 0.0) -> None:
        self._record("press", (key,), {"presses": presses, "interval": interval})

    def hotkey(self, *keys: str) -> None:
        self._record("hotkey", keys, {})

    def position(self) -> MockPoint:
        return self.pos

    def screenshot(self, region: tuple[int, int, int, int] | None = None, **kw: Any) -> MockImage:
        self._record("screenshot", (region,), kw)
        return MockImage()

    def locateOnScreen(
        self, path: str, confidence: float = 0.9, grayscale: bool = False
    ) -> MockBox | None:
        self._record("locateOnScreen", (path,), {"confidence": confidence, "grayscale": grayscale})
        if Path(path).name == "missing-on-screen.png":
            return None
        return MockBox(10, 20, 100, 50)

    def center(self, box: MockBox) -> MockPoint:
        return MockPoint(box.left + box.width // 2, box.top + box.height // 2)


class MockMSSHandle:
    def __init__(self) -> None:
        self.monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080},
        ]

    def __enter__(self) -> "MockMSSHandle":
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def grab(self, monitor: dict[str, int]) -> Any:
        class _Shot:
            size = (monitor["width"], monitor["height"])
            bgra = b"\x01\x02\x03\x04" * (monitor["width"] * monitor["height"])

        return _Shot()


class MockMSS:
    def __init__(self) -> None:
        self.handle = MockMSSHandle()

    def mss(self) -> MockMSSHandle:
        return self.handle


class MockPyperclip:
    def __init__(self) -> None:
        self._text = ""

    def paste(self) -> str:
        return self._text

    def copy(self, text: str) -> None:
        self._text = text


class MockWinBox:
    left, top, width, height = 0, 0, 640, 480


class MockWindow:
    def __init__(self, title: str) -> None:
        self.title = title
        self.box = MockWinBox()
        self.isActive = False
        self.isMinimized = False
        self.isMaximized = False
        self.actions: list[str] = []

    def activate(self) -> None:
        self.actions.append("activate")

    def resizeTo(self, w: int, h: int) -> None:
        self.actions.append(f"resize:{w}x{h}")

    def moveTo(self, x: int, y: int) -> None:
        self.actions.append(f"move:{x},{y}")


class MockGW:
    def __init__(self) -> None:
        self.windows = [
            MockWindow("Editor - main.py"),
            MockWindow("Chrome - example.com"),
        ]

    def getAllWindows(self) -> list[MockWindow]:
        return self.windows


@pytest.fixture
def pag() -> MockPyAutoGUI:
    mock = MockPyAutoGUI()
    with (
        patch(f"{LIB}.pyautogui", mock),
        patch(f"{LIB}._pyautogui_available", True),
    ):
        yield mock


@pytest.fixture
def mss_mod() -> MockMSS:
    mock = MockMSS()
    with patch(f"{LIB}.mss", mock), patch(f"{LIB}._mss_available", True):
        yield mock


@pytest.fixture
def clip() -> MockPyperclip:
    mock = MockPyperclip()
    with patch(f"{LIB}.pyperclip", mock), patch(f"{LIB}._pyperclip_available", True):
        yield mock


@pytest.fixture
def gw_mod() -> MockGW:
    mock = MockGW()
    with patch(f"{LIB}.gw", mock), patch(f"{LIB}._pygetwindow_available", True):
        yield mock


@pytest.fixture(autouse=True)
def reset_singleton():
    yield
    from mcp_server.tools.computer.computer_manager import computer_manager

    computer_manager.screenshot_dir = ""


class TestScreenshot:
    def test_screenshot_base64(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_screenshot"]())
        assert result["success"] is True
        assert result["format"] == "png"
        raw = base64.b64decode(result["base64"])
        assert raw.startswith(b"\x89PNG")
        assert result["width"] == 800 and result["height"] == 600

    def test_screenshot_save_path(self, pag: MockPyAutoGUI, tmp_path: Path) -> None:
        out = tmp_path / "shot.png"
        result = json.loads(T["computer_screenshot"](save_path=str(out)))
        assert result["success"] is True
        assert result["saved_to"] == str(out)
        assert result["size_bytes"] > 0
        assert out.exists()

    def test_screenshot_forces_png_suffix(self, pag: MockPyAutoGUI, tmp_path: Path) -> None:
        out = tmp_path / "shot.jpg"
        result = json.loads(T["computer_screenshot"](save_path=str(out)))
        assert result["saved_to"].endswith(".png")

    def test_screenshot_screenshot_dir(self, pag: MockPyAutoGUI, tmp_path: Path) -> None:
        from mcp_server.tools.computer.computer_manager import computer_manager

        computer_manager.screenshot_dir = str(tmp_path)
        result = json.loads(T["computer_screenshot"](filename="named.png"))
        assert "saved_to" in result
        assert result["saved_to"].endswith("named.png")

    def test_screenshot_region(self, pag: MockPyAutoGUI) -> None:
        T["computer_screenshot"](region="[10, 20, 300, 400]")
        name, args, _ = pag.calls[-1]
        assert name == "screenshot"
        assert args[0] == (10, 20, 300, 400)

    def test_screenshot_invalid_region(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_screenshot"](region="not-json"))
        assert "error" in result

    def test_screenshot_monitor_uses_mss(self, pag: MockPyAutoGUI, mss_mod: MockMSS) -> None:
        result = json.loads(T["computer_screenshot"](monitor=1))
        assert result["success"] is True
        assert result["width"] == 1920

    def test_screenshot_monitor_out_of_range(self, pag: MockPyAutoGUI, mss_mod: MockMSS) -> None:
        result = json.loads(T["computer_screenshot"](monitor=9))
        assert "error" in result
        assert "out of range" in result["error"]

    def test_screenshot_pyautogui_unavailable(self) -> None:
        with patch(f"{LIB}._pyautogui_available", False):
            result = json.loads(T["computer_screenshot"]())
            assert "error" in result
            assert "pyautogui is not installed" in result["error"]


class TestScreenInfo:
    def test_get_screen_size(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_get_screen_size"]())
        assert result == {"success": True, "width": 800, "height": 600}

    def test_get_monitors(self, mss_mod: MockMSS) -> None:
        result = json.loads(T["computer_get_monitors"]())
        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["monitors"]) == 3

    def test_get_monitors_unavailable(self) -> None:
        with patch(f"{LIB}._mss_available", False):
            result = json.loads(T["computer_get_monitors"]())
            assert "mss is not installed" in result["error"]

    def test_get_pixel_color(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_get_pixel_color"](10, 20))
        assert result["rgb"] == [10, 20, 30]
        assert result["hex"] == "#0a141e"

    def test_locate_on_screen_found(self, pag: MockPyAutoGUI, tmp_path: Path) -> None:
        ref = tmp_path / "ref.png"
        ref.write_bytes(b"\x89PNG")
        result = json.loads(T["computer_locate_on_screen"](str(ref)))
        assert result["found"] is True
        assert result["center"] == {"x": 60, "y": 45}
        assert result["box"]["width"] == 100

    def test_locate_on_screen_not_found(self, pag: MockPyAutoGUI, tmp_path: Path) -> None:
        ref = tmp_path / "missing-on-screen.png"
        ref.write_bytes(b"\x89PNG")
        result = json.loads(T["computer_locate_on_screen"](str(ref)))
        assert result["found"] is False
        assert result["success"] is False

    def test_locate_on_screen_missing_file(self, pag: MockPyAutoGUI, tmp_path: Path) -> None:
        result = json.loads(T["computer_locate_on_screen"](str(tmp_path / "nope.png")))
        assert "error" in result


class TestMouse:
    def test_move_absolute(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_mouse_move"](300, 400))
        assert result == {"success": True, "x": 300, "y": 400}
        assert pag.calls[0][0] == "moveTo"

    def test_move_relative(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_mouse_move"](50, -25, relative=True))
        assert result["x"] == 150 and result["y"] == 175
        assert pag.calls[0][0] == "moveRel"

    def test_click_default_position(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_mouse_click"]())
        assert result["success"] is True
        _, _, kwargs = pag.calls[0]
        assert kwargs == {"button": "left", "clicks": 1, "interval": 0.1}

    def test_click_double_right(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_mouse_click"](500, 300, button="right", clicks=2))
        assert result["button"] == "right" and result["clicks"] == 2
        _, _, kwargs = pag.calls[0]
        assert kwargs["x"] == 500 and kwargs["y"] == 300

    def test_click_invalid_button(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_mouse_click"](button="side"))
        assert "error" in result

    def test_drag_from_start(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_mouse_drag"](0, 0, 800, 600))
        assert result["start"] == {"x": 0, "y": 0}
        assert result["end"] == {"x": 800, "y": 600}
        assert pag.calls[-1][0] == "dragTo"

    def test_drag_from_current(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_mouse_drag"](end_x=5, end_y=5))
        assert result["start"] == {"x": 100, "y": 200}

    def test_drag_invalid_button(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_mouse_drag"](button="side"))
        assert "error" in result

    def test_scroll_vertical(self, pag: MockPyAutoGUI) -> None:
        T["computer_mouse_scroll"](-5)
        name, args, _ = pag.calls[0]
        assert name == "scroll" and args[0] == -5

    def test_scroll_horizontal(self, pag: MockPyAutoGUI) -> None:
        T["computer_mouse_scroll"](3, horizontal=True)
        assert pag.calls[0][0] == "hscroll"

    def test_get_position(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_mouse_get_position"]())
        assert result == {"success": True, "x": 100, "y": 200}


class TestKeyboard:
    def test_type_text(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_type_text"]("hello world"))
        assert result["success"] is True
        assert result["characters"] == 11
        assert pag.calls[0][1][0] == "hello world"

    def test_press_key(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_press_key"]("enter", presses=2))
        assert result["key"] == "enter" and result["presses"] == 2
        assert pag.calls[0][0] == "press"

    def test_press_key_unknown(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_press_key"]("hyper"))
        assert "error" in result

    def test_press_key_invalid_count(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_press_key"]("enter", presses=0))
        assert "error" in result

    def test_hotkey(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_hotkey"]("ctrl+shift+s"))
        assert result["keys"] == ["ctrl", "shift", "s"]
        assert pag.calls[0][1] == ("ctrl", "shift", "s")

    def test_hotkey_unknown_key(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_hotkey"]("ctrl+bogus"))
        assert "bogus" in result["error"]

    def test_hotkey_empty(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_hotkey"]("+"))
        assert "error" in result


class TestClipboard:
    def test_roundtrip(self, clip: MockPyperclip) -> None:
        T["computer_clipboard_write"]("some text")
        result = json.loads(T["computer_clipboard_read"]())
        assert result["content"] == "some text"
        assert result["length"] == 9

    def test_read_empty(self, clip: MockPyperclip) -> None:
        result = json.loads(T["computer_clipboard_read"]())
        assert result["content"] == ""

    def test_unavailable(self) -> None:
        with patch(f"{LIB}._pyperclip_available", False):
            result = json.loads(T["computer_clipboard_read"]())
            assert "pyperclip is not installed" in result["error"]


class TestWindows:
    def test_list_windows(self, gw_mod: MockGW) -> None:
        result = json.loads(T["computer_list_windows"]())
        assert result["count"] == 2
        titles = [w["title"] for w in result["windows"]]
        assert "Editor - main.py" in titles

    def test_list_windows_filter(self, gw_mod: MockGW) -> None:
        result = json.loads(T["computer_list_windows"]("chrome"))
        assert result["count"] == 1
        assert "Chrome" in result["windows"][0]["title"]

    def test_focus_window(self, gw_mod: MockGW) -> None:
        result = json.loads(T["computer_focus_window"]("editor"))
        assert result["focused"] == "Editor - main.py"
        assert gw_mod.windows[0].actions == ["activate"]

    def test_focus_window_not_found(self, gw_mod: MockGW) -> None:
        result = json.loads(T["computer_focus_window"]("nonexistent"))
        assert "error" in result
        assert "computer_list_windows" in result["error"]

    def test_get_window_info(self, gw_mod: MockGW) -> None:
        result = json.loads(T["computer_get_window_info"]("chrome"))
        assert result["width"] == 640
        assert result["is_active"] is False

    def test_resize_window(self, gw_mod: MockGW) -> None:
        result = json.loads(T["computer_resize_window"]("editor", 1024, 768))
        assert result["success"] is True
        assert gw_mod.windows[0].actions == ["resize:1024x768"]

    def test_resize_window_invalid_size(self, gw_mod: MockGW) -> None:
        result = json.loads(T["computer_resize_window"]("editor", 0, 768))
        assert "error" in result

    def test_move_window(self, gw_mod: MockGW) -> None:
        result = json.loads(T["computer_move_window"]("editor", 100, 50))
        assert result["x"] == 100
        assert gw_mod.windows[0].actions == ["move:100,50"]

    def test_windows_unavailable(self) -> None:
        with patch(f"{LIB}._pygetwindow_available", False):
            result = json.loads(T["computer_list_windows"]())
            assert "pygetwindow is not installed" in result["error"]


class TestConfig:
    def test_config_get(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_config_get"]())
        assert result["success"] is True
        assert result["failsafe"] is True
        assert result["pyautogui_available"] is True

    def test_config_set_pause_and_failsafe(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_config_set"](pause=0.5, failsafe=False))
        assert result["pause"] == 0.5
        assert result["failsafe"] is False
        assert pag.PAUSE == 0.5
        assert pag.FAILSAFE is False

    def test_config_set_negative_pause(self, pag: MockPyAutoGUI) -> None:
        result = json.loads(T["computer_config_set"](pause=-1.0))
        assert "error" in result
        assert "pause must be >= 0" in result["error"]

    def test_config_set_screenshot_dir(self, pag: MockPyAutoGUI, tmp_path: Path) -> None:
        from mcp_server.tools.computer.computer_manager import computer_manager

        result = json.loads(T["computer_config_set"](screenshot_dir=str(tmp_path)))
        assert result["screenshot_dir"] == str(tmp_path)
        assert computer_manager.screenshot_dir == str(tmp_path)


class TestRegistration:
    def test_22_tools_registered(self) -> None:
        assert len(T) == 22

    def test_tool_naming(self) -> None:
        assert all(name.startswith("computer_") for name in T)
