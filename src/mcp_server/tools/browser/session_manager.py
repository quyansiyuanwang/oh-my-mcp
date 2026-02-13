"""
Browser session manager for Selenium-based browser automation.

Manages multiple browser sessions with lifecycle control, CDP integration
for network monitoring and console log capture.
"""

import atexit
import json
import os
import uuid
from typing import Any, Dict, List

from mcp_server.utils import (
    BrowserError,
    SecurityError,
    ValidationError,
    logger,
    validate_url,
)

# Browser configuration
try:
    from .browser_config import get_browser_config

    _config_available = True
except ImportError:
    _config_available = False

# Lazy imports for selenium to allow graceful error when not installed
_selenium_available = False
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.edge.service import Service as EdgeService
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager

    _selenium_available = True
except ImportError:
    pass

# Dangerous URL schemes that should be blocked
BLOCKED_SCHEMES = {"file", "chrome", "chrome-extension", "javascript", "data", "about", "blob"}

# Maximum concurrent browser sessions
MAX_SESSIONS = 5

# Default timeouts (seconds)
DEFAULT_PAGE_LOAD_TIMEOUT = 30
DEFAULT_IMPLICIT_WAIT = 5
DEFAULT_SCRIPT_TIMEOUT = 30

# Selector type mapping
SELECTOR_MAP = {
    "css": "css selector",
    "xpath": "xpath",
    "id": "id",
    "name": "name",
    "class": "class name",
    "tag": "tag name",
    "link_text": "link text",
    "partial_link_text": "partial link text",
}


def _check_selenium_available() -> None:
    """Check if Selenium is available, raise error if not."""
    if not _selenium_available:
        raise BrowserError(
            "Selenium is not installed. "
            "Install it with: pip install selenium webdriver-manager "
            "or pip install oh-my-mcp[browser]"
        )


def _validate_navigation_url(url: str) -> None:
    """
    Validate a URL for browser navigation, blocking dangerous schemes.

    Args:
        url: URL to validate

    Raises:
        SecurityError: If URL uses a blocked scheme
        ValidationError: If URL format is invalid
    """
    if not url:
        raise ValidationError("URL cannot be empty")

    # Parse scheme
    from urllib.parse import urlparse

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()

    if scheme in BLOCKED_SCHEMES:
        raise SecurityError(
            f"Blocked URL scheme '{scheme}://'. "
            f"For security reasons, the following schemes are not allowed: "
            f"{', '.join(sorted(BLOCKED_SCHEMES))}"
        )

    if not validate_url(url):
        raise ValidationError(f"Invalid URL format: {url}")


def _resolve_selector(by: str) -> str:
    """
    Resolve selector type string to Selenium By constant value.

    Args:
        by: Selector type (css, xpath, id, name, class, tag)

    Returns:
        Selenium By constant string value

    Raises:
        ValidationError: If selector type is not recognized
    """
    by_lower = by.lower().strip()
    if by_lower not in SELECTOR_MAP:
        raise ValidationError(
            f"Unknown selector type '{by}'. " f"Supported types: {', '.join(SELECTOR_MAP.keys())}"
        )
    return SELECTOR_MAP[by_lower]


class BrowserSessionManager:
    """
    Manages multiple Selenium browser sessions.

    Each session is identified by a unique UUID and can run independently.
    Supports Chrome and Edge browsers with configurable options.
    Provides CDP integration for network monitoring and console log capture.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, Any] = {}  # session_id -> WebDriver
        self._session_configs: Dict[str, Dict[str, Any]] = {}  # session_id -> config
        self._console_logs: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> logs
        self._network_logs: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> logs
        self._network_enabled: Dict[str, bool] = {}  # session_id -> enabled

        # Register cleanup on exit
        atexit.register(self.close_all_sessions)

    @property
    def session_count(self) -> int:
        """Return the number of active sessions."""
        return len(self._sessions)

    def create_session(
        self,
        browser: str = "chrome",
        headless: bool = False,
        window_size: str = "1920x1080",
        user_agent: str = "",
        proxy: str = "",
        extra_args: str = "",
    ) -> str:
        """
        Create a new browser session.

        Args:
            browser: Browser type ("chrome" or "edge")
            headless: Whether to run in headless mode
            window_size: Window size in WxH format (e.g., "1920x1080")
            user_agent: Custom user agent string
            proxy: Proxy server URL
            extra_args: Additional browser arguments (comma-separated)

        Returns:
            Unique session ID

        Raises:
            BrowserError: If session creation fails
            ValidationError: If parameters are invalid
        """
        _check_selenium_available()

        if self.session_count >= MAX_SESSIONS:
            raise BrowserError(
                f"Maximum number of sessions ({MAX_SESSIONS}) reached. "
                f"Close an existing session first."
            )

        browser = browser.lower().strip()
        if browser not in ("chrome", "edge"):
            raise ValidationError(f"Unsupported browser '{browser}'. Supported: chrome, edge")

        # Parse window size
        try:
            width_str, height_str = window_size.split("x")
            width, height = int(width_str), int(height_str)
        except (ValueError, AttributeError):
            raise ValidationError(
                f"Invalid window_size format '{window_size}'. Expected 'WxH' (e.g., '1920x1080')"
            )

        session_id = str(uuid.uuid4())

        try:
            if browser == "chrome":
                try:
                    driver = self._create_chrome_driver(
                        headless=headless,
                        window_size=(width, height),
                        user_agent=user_agent,
                        proxy=proxy,
                        extra_args=extra_args,
                    )
                except BrowserError:
                    # Auto-fallback to Edge when Chrome driver fails
                    logger.warning(
                        "Chrome driver creation failed, auto-falling back to Edge browser"
                    )
                    browser = "edge"
                    driver = self._create_edge_driver(
                        headless=headless,
                        window_size=(width, height),
                        user_agent=user_agent,
                        proxy=proxy,
                        extra_args=extra_args,
                    )
            else:
                driver = self._create_edge_driver(
                    headless=headless,
                    window_size=(width, height),
                    user_agent=user_agent,
                    proxy=proxy,
                    extra_args=extra_args,
                )

            # Set timeouts
            driver.set_page_load_timeout(DEFAULT_PAGE_LOAD_TIMEOUT)
            driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT)
            driver.set_script_timeout(DEFAULT_SCRIPT_TIMEOUT)

            # Store session
            self._sessions[session_id] = driver
            self._session_configs[session_id] = {
                "browser": browser,
                "headless": headless,
                "window_size": window_size,
                "user_agent": user_agent,
                "created_at": __import__("time").time(),
            }
            self._console_logs[session_id] = []
            self._network_logs[session_id] = []
            self._network_enabled[session_id] = False

            logger.info(
                f"Created browser session {session_id} " f"(browser={browser}, headless={headless})"
            )
            return session_id

        except Exception as e:
            logger.error(f"Failed to create browser session: {e}")
            raise BrowserError(f"Failed to create browser session: {e}") from e

    def _create_chrome_driver(
        self,
        headless: bool,
        window_size: tuple[int, int],
        user_agent: str,
        proxy: str,
        extra_args: str,
    ) -> Any:
        """Create a Chrome WebDriver instance."""
        options = ChromeOptions()

        # Common options
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-default-apps")
        options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")

        # Enable logging for console log capture
        options.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})

        if headless:
            options.add_argument("--headless=new")

        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")

        if proxy:
            options.add_argument(f"--proxy-server={proxy}")

        if extra_args:
            for arg in extra_args.split(","):
                arg = arg.strip()
                if arg:
                    options.add_argument(arg)

        # Strategy 1: Use custom driver path from config/environment
        driver_path = None
        if _config_available:
            browser_conf = get_browser_config()
            driver_path = browser_conf.get_chrome_driver_path()
        else:
            driver_path = os.environ.get("CHROME_DRIVER_PATH", "").strip()

        if driver_path:
            logger.info(f"Using configured ChromeDriver path: {driver_path}")
            service = ChromeService(executable_path=driver_path)
            return webdriver.Chrome(service=service, options=options)

        # Strategy 2: Selenium Manager (Selenium 4.6+, auto-downloads matching driver)
        try:
            return webdriver.Chrome(options=options)
        except Exception as e:
            logger.warning(f"Selenium Manager failed for Chrome: {e}")

        # Strategy 3: webdriver-manager fallback
        try:
            service = ChromeService(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except Exception as e:
            logger.warning(f"webdriver-manager also failed for Chrome: {e}")

        raise BrowserError(
            "Failed to create Chrome driver. This is often caused by network issues "
            "preventing ChromeDriver download (firewall/proxy). Solutions:\n"
            "1. Set CHROME_DRIVER_PATH env var to a manually downloaded chromedriver\n"
            "2. Set HTTPS_PROXY/HTTP_PROXY env vars for network proxy\n"
            "3. Use browser='edge' instead (Edge often works when Chrome fails)\n"
            "4. Download matching ChromeDriver from: "
            "https://googlechromelabs.github.io/chrome-for-testing/"
        )

    def _create_edge_driver(
        self,
        headless: bool,
        window_size: tuple[int, int],
        user_agent: str,
        proxy: str,
        extra_args: str,
    ) -> Any:
        """Create an Edge WebDriver instance."""
        options = EdgeOptions()

        # Common options
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-default-apps")
        options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")

        # Enable logging for console log capture
        options.set_capability("ms:loggingPrefs", {"browser": "ALL", "performance": "ALL"})

        if headless:
            options.add_argument("--headless=new")

        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")

        if proxy:
            options.add_argument(f"--proxy-server={proxy}")

        if extra_args:
            for arg in extra_args.split(","):
                arg = arg.strip()
                if arg:
                    options.add_argument(arg)

        # Strategy 1: Use custom driver path from config/environment
        driver_path = None
        if _config_available:
            browser_conf = get_browser_config()
            driver_path = browser_conf.get_edge_driver_path()
        else:
            driver_path = os.environ.get("EDGE_DRIVER_PATH", "").strip()

        if driver_path:
            logger.info(f"Using configured EdgeDriver path: {driver_path}")
            service = EdgeService(executable_path=driver_path)
            return webdriver.Edge(service=service, options=options)

        # Strategy 2: Selenium Manager (Selenium 4.6+, auto-downloads matching driver)
        try:
            return webdriver.Edge(options=options)
        except Exception as e:
            logger.warning(f"Selenium Manager failed for Edge: {e}")

        # Strategy 3: webdriver-manager fallback
        try:
            service = EdgeService(EdgeChromiumDriverManager().install())
            return webdriver.Edge(service=service, options=options)
        except Exception as e:
            logger.warning(f"webdriver-manager also failed for Edge: {e}")

        raise BrowserError(
            "Failed to create Edge driver. This is often caused by network issues "
            "preventing EdgeDriver download (firewall/proxy). Solutions:\n"
            "1. Set EDGE_DRIVER_PATH env var to a manually downloaded msedgedriver\n"
            "2. Set HTTPS_PROXY/HTTP_PROXY env vars for network proxy\n"
            "3. Download matching EdgeDriver from: "
            "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/"
        )

    def get_session(self, session_id: str) -> Any:
        """
        Get an existing browser session.

        Args:
            session_id: The session identifier

        Returns:
            WebDriver instance

        Raises:
            BrowserError: If session does not exist
        """
        if session_id not in self._sessions:
            raise BrowserError(
                f"Browser session '{session_id}' not found. "
                f"Active sessions: {list(self._sessions.keys())}"
            )
        return self._sessions[session_id]

    def close_session(self, session_id: str) -> None:
        """
        Close and clean up a browser session.

        Args:
            session_id: The session identifier

        Raises:
            BrowserError: If session does not exist
        """
        if session_id not in self._sessions:
            raise BrowserError(f"Browser session '{session_id}' not found.")

        try:
            driver = self._sessions[session_id]
            driver.quit()
        except Exception as e:
            logger.warning(f"Error closing browser session {session_id}: {e}")
        finally:
            self._sessions.pop(session_id, None)
            self._session_configs.pop(session_id, None)
            self._console_logs.pop(session_id, None)
            self._network_logs.pop(session_id, None)
            self._network_enabled.pop(session_id, None)
            logger.info(f"Closed browser session {session_id}")

    def close_all_sessions(self) -> None:
        """Close all active browser sessions."""
        session_ids = list(self._sessions.keys())
        for session_id in session_ids:
            try:
                driver = self._sessions[session_id]
                driver.quit()
            except Exception as e:
                logger.warning(f"Error closing session {session_id}: {e}")
            finally:
                self._sessions.pop(session_id, None)
                self._session_configs.pop(session_id, None)
                self._console_logs.pop(session_id, None)
                self._network_logs.pop(session_id, None)
                self._network_enabled.pop(session_id, None)

        if session_ids:
            logger.info(f"Closed {len(session_ids)} browser session(s)")

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active browser sessions with their info.

        Returns:
            List of session info dictionaries
        """
        sessions = []
        for session_id, driver in self._sessions.items():
            config = self._session_configs.get(session_id, {})
            try:
                current_url = driver.current_url
                title = driver.title
            except Exception:
                current_url = "unknown"
                title = "unknown"

            sessions.append(
                {
                    "session_id": session_id,
                    "browser": config.get("browser", "unknown"),
                    "headless": config.get("headless", False),
                    "window_size": config.get("window_size", "unknown"),
                    "current_url": current_url,
                    "title": title,
                    "tab_count": (
                        len(driver.window_handles) if hasattr(driver, "window_handles") else 1
                    ),
                }
            )

        return sessions

    def get_console_logs(self, session_id: str, level: str = "all") -> List[Dict[str, Any]]:
        """
        Get browser console logs for a session.

        Uses Selenium's get_log('browser') API to capture console output.

        Args:
            session_id: The session identifier
            level: Filter by level (all, error, warning, info, debug)

        Returns:
            List of log entries
        """
        driver = self.get_session(session_id)

        # Collect logs from Selenium's logging API
        try:
            browser_logs = driver.get_log("browser")
            for entry in browser_logs:
                log_entry = {
                    "level": entry.get("level", "UNKNOWN"),
                    "message": entry.get("message", ""),
                    "timestamp": entry.get("timestamp", 0),
                    "source": entry.get("source", ""),
                }
                self._console_logs[session_id].append(log_entry)
        except Exception as e:
            logger.debug(f"Could not get browser logs via Selenium API: {e}")

        # Filter by level
        logs = self._console_logs.get(session_id, [])
        if level.lower() != "all":
            level_map = {
                "error": ["SEVERE", "ERROR"],
                "warning": ["WARNING", "WARN"],
                "info": ["INFO"],
                "debug": ["DEBUG", "FINE", "FINER", "FINEST"],
            }
            allowed_levels = level_map.get(level.lower(), [level.upper()])
            logs = [log for log in logs if log.get("level", "").upper() in allowed_levels]

        return logs

    def enable_network_logging(self, session_id: str) -> None:
        """
        Enable network request logging via CDP.

        Args:
            session_id: The session identifier
        """
        driver = self.get_session(session_id)

        try:
            # Enable Network domain via CDP
            driver.execute_cdp_cmd("Network.enable", {})
            self._network_enabled[session_id] = True
            logger.info(f"Network logging enabled for session {session_id}")
        except Exception as e:
            logger.warning(f"Could not enable CDP network logging: {e}")
            # Fallback: mark as enabled and use performance logs
            self._network_enabled[session_id] = True

    def get_network_logs(
        self,
        session_id: str,
        filter_url: str = "",
        filter_method: str = "",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get captured network request logs.

        Uses Selenium performance logs to extract network events.

        Args:
            session_id: The session identifier
            filter_url: Filter logs by URL substring
            filter_method: Filter by HTTP method
            limit: Maximum number of entries to return

        Returns:
            List of network log entries
        """
        driver = self.get_session(session_id)

        # Try to get network events from performance logs
        try:
            perf_logs = driver.get_log("performance")
            for entry in perf_logs:
                try:
                    log_message = json.loads(entry.get("message", "{}"))
                    message = log_message.get("message", {})
                    method = message.get("method", "")
                    params = message.get("params", {})

                    if method == "Network.requestWillBeSent":
                        request = params.get("request", {})
                        net_entry = {
                            "type": "request",
                            "url": request.get("url", ""),
                            "method": request.get("method", ""),
                            "headers": request.get("headers", {}),
                            "request_id": params.get("requestId", ""),
                            "timestamp": params.get("timestamp", 0),
                        }
                        self._network_logs[session_id].append(net_entry)

                    elif method == "Network.responseReceived":
                        response = params.get("response", {})
                        net_entry = {
                            "type": "response",
                            "url": response.get("url", ""),
                            "status": response.get("status", 0),
                            "status_text": response.get("statusText", ""),
                            "mime_type": response.get("mimeType", ""),
                            "headers": response.get("headers", {}),
                            "request_id": params.get("requestId", ""),
                            "timestamp": params.get("timestamp", 0),
                        }
                        self._network_logs[session_id].append(net_entry)

                except (json.JSONDecodeError, KeyError):
                    continue
        except Exception as e:
            logger.debug(f"Could not get performance logs: {e}")

        # Apply filters
        logs = self._network_logs.get(session_id, [])

        if filter_url:
            logs = [log for log in logs if filter_url.lower() in log.get("url", "").lower()]

        if filter_method:
            logs = [log for log in logs if log.get("method", "").upper() == filter_method.upper()]

        # Return most recent entries up to limit
        return logs[-limit:]


# Module-level singleton instance
session_manager = BrowserSessionManager()
