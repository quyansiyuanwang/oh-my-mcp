"""
Tests for browser automation tools.

Uses mocking to test browser tools without requiring actual browsers.
"""

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server.tools import browser


class MockMCP:
    """Mock MCP server for testing."""

    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


class MockWebDriver:
    """Mock Selenium WebDriver for testing."""

    def __init__(self):
        self.current_url = "https://example.com"
        self.title = "Example Domain"
        self.page_source = "<html><head><title>Example</title></head><body>Hello</body></html>"
        self.window_handles = ["handle1"]
        self._current_handle = "handle1"
        self._cookies = []
        self._logs = {"browser": [], "performance": []}

    @property
    def current_window_handle(self):
        return self._current_handle

    def get(self, url):
        self.current_url = url

    def back(self):
        pass

    def forward(self):
        pass

    def refresh(self):
        pass

    def quit(self):
        pass

    def close(self):
        pass

    def find_element(self, by, selector):
        element = MagicMock()
        element.text = "Element text"
        element.tag_name = "div"
        element.is_displayed.return_value = True
        element.is_enabled.return_value = True
        element.get_attribute.return_value = ""
        element.screenshot_as_png = b"\x89PNG\r\n\x1a\n"
        return element

    def find_elements(self, by, selector):
        element = self.find_element(by, selector)
        return [element, element]

    def execute_script(self, script, *args):
        if "scrollWidth" in script:
            return 1920
        if "scrollHeight" in script:
            return 1080
        return None

    def execute_cdp_cmd(self, cmd, params):
        return {}

    def get_screenshot_as_png(self):
        return b"\x89PNG\r\n\x1a\n"

    def get_cookies(self):
        return self._cookies

    def add_cookie(self, cookie):
        self._cookies.append(cookie)

    def delete_cookie(self, name):
        self._cookies = [c for c in self._cookies if c.get("name") != name]

    def delete_all_cookies(self):
        self._cookies = []

    def get_log(self, log_type):
        return self._logs.get(log_type, [])

    def set_page_load_timeout(self, timeout):
        pass

    def implicitly_wait(self, timeout):
        pass

    def set_script_timeout(self, timeout):
        pass

    def set_window_size(self, width, height):
        pass

    def switch_to(self):
        pass


class MockSwitchTo:
    """Mock switchTo for WebDriver."""

    def __init__(self, driver):
        self._driver = driver

    def window(self, handle):
        self._driver._current_handle = handle


# Patch the switch_to property
MockWebDriver.switch_to = property(lambda self: MockSwitchTo(self))


@pytest.fixture
def mock_mcp():
    """Create a mock MCP server with browser tools registered."""
    mcp = MockMCP()
    browser.register_tools(mcp)
    return mcp


@pytest.fixture
def mock_driver():
    """Create a mock WebDriver."""
    return MockWebDriver()


@pytest.fixture
def mock_session_manager(mock_driver):
    """Patch session_manager to use mock driver."""
    with patch("mcp_server.tools.browser.handlers.session_manager") as mock_sm:
        mock_sm.create_session.return_value = "test-session-123"
        mock_sm.get_session.return_value = mock_driver
        mock_sm.list_sessions.return_value = [
            {
                "session_id": "test-session-123",
                "browser": "chrome",
                "headless": False,
                "window_size": "1920x1080",
                "current_url": "https://example.com",
                "title": "Example Domain",
                "tab_count": 1,
            }
        ]
        mock_sm.get_console_logs.return_value = [
            {"level": "INFO", "message": "Test log", "timestamp": 1234567890}
        ]
        mock_sm.get_network_logs.return_value = [
            {"type": "request", "url": "https://example.com", "method": "GET"}
        ]
        yield mock_sm


class TestSessionManagement:
    """Tests for session management tools."""

    def test_browser_open(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_open creates a session."""
        result = mock_mcp.tools["browser_open"]("https://example.com")
        data = json.loads(result)

        assert data["success"] is True
        assert "session_id" in data
        mock_session_manager.create_session.assert_called_once()

    def test_browser_open_invalid_url(self, mock_mcp, mock_session_manager):
        """Test browser_open rejects invalid URLs."""
        result = mock_mcp.tools["browser_open"]("not-a-url")
        data = json.loads(result)

        assert "error" in data
        assert "Invalid URL" in data["error"]

    def test_browser_open_blocked_scheme(self, mock_mcp, mock_session_manager):
        """Test browser_open rejects dangerous URL schemes."""
        result = mock_mcp.tools["browser_open"]("file:///etc/passwd")
        data = json.loads(result)

        assert "error" in data
        assert "Blocked URL scheme" in data["error"]

    def test_browser_close(self, mock_mcp, mock_session_manager):
        """Test browser_close closes a session."""
        result = mock_mcp.tools["browser_close"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True
        mock_session_manager.close_session.assert_called_once_with("test-session-123")

    def test_browser_list_sessions(self, mock_mcp, mock_session_manager):
        """Test browser_list_sessions returns session info."""
        result = mock_mcp.tools["browser_list_sessions"]()
        data = json.loads(result)

        assert data["success"] is True
        assert data["session_count"] == 1
        assert len(data["sessions"]) == 1


class TestNavigation:
    """Tests for navigation tools."""

    def test_browser_navigate(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_navigate goes to URL."""
        result = mock_mcp.tools["browser_navigate"]("test-session-123", "https://google.com")
        data = json.loads(result)

        assert data["success"] is True
        # Navigation verified by checking current_url in result
        assert "current_url" in data

    def test_browser_back(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_back navigates back."""
        result = mock_mcp.tools["browser_back"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True

    def test_browser_forward(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_forward navigates forward."""
        result = mock_mcp.tools["browser_forward"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True

    def test_browser_refresh(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_refresh refreshes page."""
        result = mock_mcp.tools["browser_refresh"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True


class TestPageInformation:
    """Tests for page information tools."""

    def test_browser_get_page_source(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_get_page_source returns HTML."""
        result = mock_mcp.tools["browser_get_page_source"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True
        assert "source" in data
        assert "<html>" in data["source"]

    def test_browser_get_text(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_get_text returns element text."""
        result = mock_mcp.tools["browser_get_text"]("test-session-123", "body")
        data = json.loads(result)

        assert data["success"] is True
        assert "text" in data

    def test_browser_get_url(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_get_url returns current URL."""
        result = mock_mcp.tools["browser_get_url"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True
        assert "url" in data
        assert "title" in data


class TestElementInteraction:
    """Tests for element interaction tools."""

    def test_browser_click(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_click clicks an element."""
        with patch("selenium.webdriver.support.ui.WebDriverWait") as mock_wait:
            mock_element = MagicMock()
            mock_wait.return_value.until.return_value = mock_element

            result = mock_mcp.tools["browser_click"]("test-session-123", "#button")
            data = json.loads(result)

            assert data["success"] is True
            mock_element.click.assert_called_once()

    def test_browser_type(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_type types text into element."""
        with patch("selenium.webdriver.support.ui.WebDriverWait") as mock_wait:
            mock_element = MagicMock()
            mock_wait.return_value.until.return_value = mock_element

            result = mock_mcp.tools["browser_type"]("test-session-123", "#input", "Hello World")
            data = json.loads(result)

            assert data["success"] is True
            mock_element.send_keys.assert_called_with("Hello World")

    def test_browser_select(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_select selects dropdown option."""
        with patch("selenium.webdriver.support.ui.WebDriverWait") as mock_wait:
            with patch("selenium.webdriver.support.ui.Select") as mock_select_class:
                mock_element = MagicMock()
                mock_wait.return_value.until.return_value = mock_element
                mock_select = MagicMock()
                mock_select_class.return_value = mock_select

                result = mock_mcp.tools["browser_select"](
                    "test-session-123", "#dropdown", "option1"
                )
                data = json.loads(result)

                assert data["success"] is True
                mock_select.select_by_value.assert_called_with("option1")

    def test_browser_wait_for(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_wait_for waits for element."""
        with patch("selenium.webdriver.support.ui.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = True

            result = mock_mcp.tools["browser_wait_for"]("test-session-123", "#element")
            data = json.loads(result)

            assert data["success"] is True


class TestScreenshot:
    """Tests for screenshot tool."""

    def test_browser_screenshot_base64(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_screenshot returns base64."""
        from mcp_server.tools.browser.browser_config import BrowserConfig

        # Mock config with no screenshot_dir to ensure base64 response
        test_config = BrowserConfig()
        test_config._config = {"screenshot_dir": None}

        with patch(
            "mcp_server.tools.browser.handlers.get_browser_config",
            return_value=test_config,
        ):
            result = mock_mcp.tools["browser_screenshot"]("test-session-123")
            data = json.loads(result)

            assert data["success"] is True
            assert "base64" in data
            assert data["format"] == "png"

    def test_browser_screenshot_save(self, mock_mcp, mock_session_manager, mock_driver, tmp_path):
        """Test browser_screenshot saves to file."""
        save_path = str(tmp_path / "screenshot.png")
        result = mock_mcp.tools["browser_screenshot"]("test-session-123", save_path)
        data = json.loads(result)

        assert data["success"] is True
        assert "saved_to" in data


class TestJavaScript:
    """Tests for JavaScript execution tool."""

    def test_browser_execute_js(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_execute_js executes script."""
        mock_driver.execute_script = MagicMock(return_value={"result": 42})

        result = mock_mcp.tools["browser_execute_js"]("test-session-123", "return document.title;")
        data = json.loads(result)

        assert data["success"] is True
        assert "result" in data


class TestConsoleLogs:
    """Tests for console log tool."""

    def test_browser_get_console_logs(self, mock_mcp, mock_session_manager):
        """Test browser_get_console_logs returns logs."""
        result = mock_mcp.tools["browser_get_console_logs"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True
        assert "logs" in data
        assert data["log_count"] >= 0


class TestCookies:
    """Tests for cookie management tools."""

    def test_browser_get_cookies(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_get_cookies returns cookies."""
        mock_driver._cookies = [{"name": "test", "value": "123"}]

        result = mock_mcp.tools["browser_get_cookies"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True
        assert "cookies" in data

    def test_browser_set_cookie(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_set_cookie sets a cookie."""
        result = mock_mcp.tools["browser_set_cookie"]("test-session-123", "mycookie", "myvalue")
        data = json.loads(result)

        assert data["success"] is True

    def test_browser_delete_cookies(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_delete_cookies deletes cookies."""
        result = mock_mcp.tools["browser_delete_cookies"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True


class TestNetworkLogs:
    """Tests for network logging tools."""

    def test_browser_enable_network_log(self, mock_mcp, mock_session_manager):
        """Test browser_enable_network_log enables logging."""
        result = mock_mcp.tools["browser_enable_network_log"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True

    def test_browser_get_network_logs(self, mock_mcp, mock_session_manager):
        """Test browser_get_network_logs returns logs."""
        result = mock_mcp.tools["browser_get_network_logs"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True
        assert "logs" in data


class TestFormFilling:
    """Tests for form filling tool."""

    def test_browser_fill_form(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_fill_form fills multiple fields."""
        form_data = json.dumps({"#username": "john", "#email": "john@example.com"})

        result = mock_mcp.tools["browser_fill_form"]("test-session-123", form_data)
        data = json.loads(result)

        assert data["success"] is True
        assert data["fields_processed"] == 2

    def test_browser_fill_form_invalid_json(self, mock_mcp, mock_session_manager):
        """Test browser_fill_form rejects invalid JSON."""
        result = mock_mcp.tools["browser_fill_form"]("test-session-123", "not-json")
        data = json.loads(result)

        assert "error" in data


class TestTabManagement:
    """Tests for tab management tools."""

    def test_browser_new_tab(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_new_tab opens new tab."""
        mock_driver.window_handles = ["handle1", "handle2"]

        result = mock_mcp.tools["browser_new_tab"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True
        assert data["tab_count"] == 2

    def test_browser_switch_tab(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_switch_tab switches tabs."""
        mock_driver.window_handles = ["handle1", "handle2"]

        result = mock_mcp.tools["browser_switch_tab"]("test-session-123", 1)
        data = json.loads(result)

        assert data["success"] is True

    def test_browser_list_tabs(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_list_tabs lists tabs."""
        mock_driver.window_handles = ["handle1"]

        result = mock_mcp.tools["browser_list_tabs"]("test-session-123")
        data = json.loads(result)

        assert data["success"] is True
        assert "tabs" in data


class TestElementQuery:
    """Tests for element query tools."""

    def test_browser_find_elements(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_find_elements finds elements."""
        result = mock_mcp.tools["browser_find_elements"]("test-session-123", "div")
        data = json.loads(result)

        assert data["success"] is True
        assert "elements" in data

    def test_browser_get_element_attribute(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_get_element_attribute gets attribute."""
        result = mock_mcp.tools["browser_get_element_attribute"](
            "test-session-123", "#elem", "class"
        )
        data = json.loads(result)

        assert data["success"] is True
        assert "value" in data


class TestScroll:
    """Tests for scroll tool."""

    def test_browser_scroll_down(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_scroll scrolls down."""
        result = mock_mcp.tools["browser_scroll"]("test-session-123", "down", 500)
        data = json.loads(result)

        assert data["success"] is True

    def test_browser_scroll_to_element(self, mock_mcp, mock_session_manager, mock_driver):
        """Test browser_scroll scrolls to element."""
        result = mock_mcp.tools["browser_scroll"]("test-session-123", "down", 0, "#target")
        data = json.loads(result)

        assert data["success"] is True


class TestURLValidation:
    """Tests for URL validation security."""

    @pytest.mark.parametrize(
        "blocked_url",
        [
            "file:///etc/passwd",
            "file:///C:/Windows/System32/config",
            "chrome://settings",
            "chrome-extension://abc123",
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "about:blank",
        ],
    )
    def test_blocked_urls(self, mock_mcp, mock_session_manager, blocked_url):
        """Test that dangerous URL schemes are blocked."""
        result = mock_mcp.tools["browser_open"](blocked_url)
        data = json.loads(result)

        assert "error" in data
        assert "Blocked" in data["error"] or "Invalid" in data["error"]


class TestDriverCreation:
    """Tests for driver creation strategies: Selenium Manager, webdriver-manager, env vars."""

    def test_chrome_driver_with_env_path(self):
        """Test Chrome driver creation using CHROME_DRIVER_PATH env var."""
        from mcp_server.tools.browser.session_manager import BrowserSessionManager

        manager = BrowserSessionManager()

        with patch.dict("os.environ", {"CHROME_DRIVER_PATH": "/usr/bin/chromedriver"}):
            with patch("mcp_server.tools.browser.session_manager.webdriver") as mock_wd:
                mock_wd.Chrome.return_value = MagicMock()
                manager._create_chrome_driver(
                    headless=True,
                    window_size=(1920, 1080),
                    user_agent="",
                    proxy="",
                    extra_args="",
                )
                # Should use custom path, not Selenium Manager
                mock_wd.Chrome.assert_called_once()
                call_kwargs = mock_wd.Chrome.call_args
                assert call_kwargs.kwargs.get("service") is not None

    def test_edge_driver_with_env_path(self):
        """Test Edge driver creation using EDGE_DRIVER_PATH env var."""
        from mcp_server.tools.browser.session_manager import BrowserSessionManager

        manager = BrowserSessionManager()

        with patch.dict("os.environ", {"EDGE_DRIVER_PATH": "/usr/bin/msedgedriver"}):
            with patch("mcp_server.tools.browser.session_manager.webdriver") as mock_wd:
                mock_wd.Edge.return_value = MagicMock()
                manager._create_edge_driver(
                    headless=True,
                    window_size=(1920, 1080),
                    user_agent="",
                    proxy="",
                    extra_args="",
                )
                mock_wd.Edge.assert_called_once()
                call_kwargs = mock_wd.Edge.call_args
                assert call_kwargs.kwargs.get("service") is not None

    def test_chrome_fallback_to_webdriver_manager(self):
        """Test Chrome falls back to webdriver-manager when Selenium Manager fails."""
        from mcp_server.tools.browser.session_manager import BrowserSessionManager

        manager = BrowserSessionManager()

        with patch.dict("os.environ", {}, clear=False):
            # Ensure no custom driver path
            import os

            os.environ.pop("CHROME_DRIVER_PATH", None)

            with patch("mcp_server.tools.browser.session_manager._config_available", False):
                with patch("mcp_server.tools.browser.session_manager.webdriver") as mock_wd:
                    with patch(
                        "mcp_server.tools.browser.session_manager.ChromeDriverManager"
                    ) as mock_cdm:
                        # First call (Selenium Manager) fails, second call (webdriver-manager) succeeds
                        mock_wd.Chrome.side_effect = [
                            Exception("Selenium Manager failed"),
                            MagicMock(),
                        ]
                        mock_cdm.return_value.install.return_value = "/path/to/chromedriver"

                        manager._create_chrome_driver(
                            headless=True,
                            window_size=(1920, 1080),
                            user_agent="",
                            proxy="",
                            extra_args="",
                        )
                        assert mock_wd.Chrome.call_count == 2
                        mock_cdm.return_value.install.assert_called_once()

    def test_chrome_raises_browser_error_on_total_failure(self):
        """Test Chrome raises BrowserError with helpful message when all strategies fail."""
        from mcp_server.tools.browser.session_manager import BrowserSessionManager
        from mcp_server.utils import BrowserError

        manager = BrowserSessionManager()

        with patch.dict("os.environ", {}, clear=False):
            import os

            os.environ.pop("CHROME_DRIVER_PATH", None)

            with patch("mcp_server.tools.browser.session_manager._config_available", False):
                with patch("mcp_server.tools.browser.session_manager.webdriver") as mock_wd:
                    with patch(
                        "mcp_server.tools.browser.session_manager.ChromeDriverManager"
                    ) as mock_cdm:
                        mock_wd.Chrome.side_effect = Exception("Selenium Manager failed")
                        mock_cdm.return_value.install.side_effect = Exception(
                            "webdriver-manager failed"
                        )

                        with pytest.raises(BrowserError, match="network issues"):
                            manager._create_chrome_driver(
                                headless=True,
                                window_size=(1920, 1080),
                                user_agent="",
                                proxy="",
                                extra_args="",
                            )


class TestChromeToEdgeFallback:
    """Tests for automatic Chrome to Edge fallback."""

    def test_auto_fallback_from_chrome_to_edge(self):
        """Test that create_session falls back to Edge when Chrome driver fails."""
        from mcp_server.tools.browser.session_manager import BrowserSessionManager
        from mcp_server.utils import BrowserError

        manager = BrowserSessionManager()

        mock_driver = MockWebDriver()
        with patch.object(
            manager, "_create_chrome_driver", side_effect=BrowserError("Chrome failed")
        ):
            with patch.object(manager, "_create_edge_driver", return_value=mock_driver):
                session_id = manager.create_session(browser="chrome")

                # Should succeed via Edge fallback
                assert session_id is not None
                session_config = manager._session_configs[session_id]
                assert session_config["browser"] == "edge"

                # Cleanup
                manager.close_session(session_id)

    def test_edge_direct_no_fallback(self):
        """Test that Edge request goes directly to Edge without fallback logic."""
        from mcp_server.tools.browser.session_manager import BrowserSessionManager

        manager = BrowserSessionManager()

        mock_driver = MockWebDriver()
        with patch.object(manager, "_create_edge_driver", return_value=mock_driver) as edge_mock:
            with patch.object(manager, "_create_chrome_driver") as chrome_mock:
                session_id = manager.create_session(browser="edge")

                edge_mock.assert_called_once()
                chrome_mock.assert_not_called()

                # Cleanup
                manager.close_session(session_id)


class TestBrowserConfig:
    """Tests for browser configuration management."""

    def test_browser_config_get_all(self, mock_mcp):
        """Test getting all browser configuration."""
        result = mock_mcp.tools["browser_config_get"]("")
        data = json.loads(result)

        assert "config_file" in data
        assert "driver_paths" in data
        assert "default_browser" in data

    def test_browser_config_get_specific_key(self, mock_mcp):
        """Test getting specific configuration key."""
        result = mock_mcp.tools["browser_config_get"]("default_browser")
        data = json.loads(result)

        assert "default_browser" in data

    def test_browser_config_set(self, mock_mcp):
        """Test setting browser configuration."""
        import tempfile
        from pathlib import Path

        # Use temp config file for testing
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            from mcp_server.tools.browser.browser_config import BrowserConfig

            test_config = BrowserConfig(config_path=tmp_path)

            with patch(
                "mcp_server.tools.browser.browser_config.get_browser_config",
                return_value=test_config,
            ):
                result = mock_mcp.tools["browser_config_set"]("default_browser", "edge")
                data = json.loads(result)

                assert data.get("success") is True
                assert test_config.get_default_browser() == "edge"
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_browser_config_reset(self, mock_mcp):
        """Test resetting browser configuration."""
        import tempfile
        from pathlib import Path

        # Use temp config file for testing
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            from mcp_server.tools.browser.browser_config import BrowserConfig

            test_config = BrowserConfig(config_path=tmp_path)
            test_config.set_default_browser("edge")

            with patch(
                "mcp_server.tools.browser.browser_config.get_browser_config",
                return_value=test_config,
            ):
                result = mock_mcp.tools["browser_config_reset"]()
                data = json.loads(result)

                assert data.get("success") is True
                # After reset, should return default
                assert test_config.get_default_browser() == "chrome"
        finally:
            Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
