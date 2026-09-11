"""
Computer use resource management.

Centralizes:
- Lazy imports and availability guards for optional hardware libraries
  (pyautogui, mss, pyperclip, pygetwindow)
- Safety configuration (FAILSAFE, action pause interval)
- Screen capture helpers (multi-monitor via mss, base64 or file output)
- Window lookup helpers (pygetwindow)

A module-level singleton `computer_manager` is shared by all handlers,
mirroring the browser module's session_manager pattern.
"""

import base64
import io
import time
from typing import Any, Optional

from mcp_server.utils import ComputerUseError, logger

# Explicit re-exports: handlers access hardware libraries through this module
# so tests can patch them in one place.
__all__ = [
    "ComputerManager",
    "computer_manager",
    "pyautogui",
    "mss",
    "pyperclip",
    "gw",
    "_check_pyautogui_available",
    "_check_mss_available",
    "_check_pyperclip_available",
    "_check_pygetwindow_available",
    "_opencv_available",
]

# Lazy imports to allow graceful errors when libraries are not installed or
# no display is available (headless Linux raises non-ImportError exceptions).
# Each flag is read at call time so tests can patch the module attributes.
pyautogui: Any = None
mss: Any = None
pyperclip: Any = None
gw: Any = None

_pyautogui_available = False
try:
    import pyautogui as _pyautogui_mod

    pyautogui = _pyautogui_mod
    _pyautogui_available = True
except Exception:  # ImportError, DISPLAY errors, platform guards
    pass

_mss_available = False
try:
    import mss as _mss_mod

    mss = _mss_mod
    _mss_available = True
except Exception:
    pass

_pyperclip_available = False
try:
    import pyperclip as _pyperclip_mod

    pyperclip = _pyperclip_mod
    _pyperclip_available = True
except Exception:
    pass

_pygetwindow_available = False
try:
    import pygetwindow as _gw_mod

    gw = _gw_mod
    _pygetwindow_available = True
except Exception:  # pygetwindow raises NotImplementedError on non-Windows
    pass

_opencv_available = False
try:
    import cv2  # noqa: F401

    _opencv_available = True
except Exception:
    cv2 = None

INSTALL_HINT = (
    "Install with: pip install pyautogui mss pyperclip pygetwindow pillow "
    "or pip install oh-my-mcp[computer]"
)


def _check_pyautogui_available() -> None:
    if not _pyautogui_available:
        raise ComputerUseError(f"pyautogui is not installed. {INSTALL_HINT}")


def _check_mss_available() -> None:
    if not _mss_available:
        raise ComputerUseError(f"mss is not installed. {INSTALL_HINT}")


def _check_pyperclip_available() -> None:
    if not _pyperclip_available:
        raise ComputerUseError(f"pyperclip is not installed. {INSTALL_HINT}")


def _check_pygetwindow_available() -> None:
    if not _pygetwindow_available:
        raise ComputerUseError(f"pygetwindow is not installed. {INSTALL_HINT}")


def _is_user_visible_window(w: Any) -> bool:
    """Filter out invisible system windows (empty title, 1x1 placeholder)."""
    title = (w.title or "").strip()
    if not title:
        return False
    try:
        box = w.box
        return bool(box.width > 1 and box.height > 1)
    except Exception:
        return False


class ComputerManager:
    """
    Shared state for computer use tools.

    Attributes:
        screenshot_dir: Default directory for saving screenshots. Empty string
            means screenshots are returned as base64 unless save_path is given.
    """

    def __init__(self) -> None:
        self.screenshot_dir: str = ""
        if _pyautogui_available:
            # Safety defaults: corner failsafe ON, small pause between actions.
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1

    # -- configuration ------------------------------------------------------

    def get_config(self) -> dict[str, Any]:
        config: dict[str, Any] = {
            "screenshot_dir": self.screenshot_dir,
            "pyautogui_available": _pyautogui_available,
            "mss_available": _mss_available,
            "pyperclip_available": _pyperclip_available,
            "pygetwindow_available": _pygetwindow_available,
        }
        if _pyautogui_available:
            config["pause"] = pyautogui.PAUSE
            config["failsafe"] = pyautogui.FAILSAFE
        return config

    def set_config(
        self,
        pause: Optional[float] = None,
        failsafe: Optional[bool] = None,
        screenshot_dir: Optional[str] = None,
    ) -> dict[str, Any]:
        if pause is not None:
            if pause < 0:
                raise ComputerUseError("pause must be >= 0")
            _check_pyautogui_available()
            pyautogui.PAUSE = pause
        if failsafe is not None:
            _check_pyautogui_available()
            pyautogui.FAILSAFE = failsafe
        if screenshot_dir is not None:
            self.screenshot_dir = screenshot_dir
        return self.get_config()

    # -- screen capture -----------------------------------------------------

    def capture_image(self, region: Optional[list[int]] = None, monitor: int = 0) -> Any:
        """
        Capture the screen as a PIL Image.

        Args:
            region: [x, y, width, height] crop within the primary display.
            monitor: 0 for the primary display (pyautogui), or a 1-based index
                into mss monitor list for a specific display.
        """
        _check_pyautogui_available()

        if monitor > 0:
            _check_mss_available()
            with mss.MSS() as sct:
                try:
                    mon = sct.monitors[monitor]
                except IndexError:
                    raise ComputerUseError(
                        f"Monitor index {monitor} out of range. "
                        f"Available monitors: {len(sct.monitors) - 1}"
                    )
                shot = sct.grab(mon)
                from PIL import Image

                return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

        kwargs: dict[str, Any] = {}
        if region:
            if len(region) != 4 or any(v < 0 for v in region):
                raise ComputerUseError(
                    "region must be [x, y, width, height] with non-negative values"
                )
            kwargs["region"] = tuple(region)
        return pyautogui.screenshot(**kwargs)

    def image_to_base64(self, image: Any) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("ascii")

    # -- windows --------------------------------------------------------------

    def find_window(self, title: str) -> Any:
        """Find a visible, titled window whose title contains `title` (case-insensitive)."""
        _check_pygetwindow_available()
        matches = [
            w
            for w in gw.getAllWindows()
            if _is_user_visible_window(w) and title.lower() in (w.title or "").lower()
        ]
        if not matches:
            raise ComputerUseError(
                f"No window found with title containing: {title}. "
                "Use computer_list_windows to see available windows."
            )
        return matches[0]

    def list_windows(self, title_filter: str = "") -> list[dict[str, Any]]:
        _check_pygetwindow_available()
        result = []
        for w in gw.getAllWindows():
            t = w.title or ""
            if not _is_user_visible_window(w):
                continue
            if title_filter and title_filter.lower() not in t.lower():
                continue
            try:
                box = w.box
                result.append(
                    {
                        "title": t,
                        "left": box.left,
                        "top": box.top,
                        "width": box.width,
                        "height": box.height,
                        "is_active": w.isActive,
                        "is_minimized": w.isMinimized,
                        "is_maximized": w.isMaximized,
                    }
                )
            except Exception as e:  # window may vanish between listing and reading
                logger.warning(f"Could not read window info for {t!r}: {e}")
                continue
        return result


# Small helper for keyboard actions that need a tiny delay between keys
def _sleep(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)


# Module-level singleton shared by all handlers
computer_manager = ComputerManager()
