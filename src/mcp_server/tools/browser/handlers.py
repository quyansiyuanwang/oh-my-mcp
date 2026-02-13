"""
Browser automation tool handlers.

Provides Selenium-based browser automation capabilities including:
- Session management (open, close, list)
- Page navigation (navigate, back, refresh)
- Page information (source, text, URL)
- Element interaction (click, type, select, wait)
- Screenshots
- JavaScript execution
- Console log capture
- Cookie management
- Network monitoring
- Form filling
- Multi-tab management
"""

import base64
import json
import time
from datetime import datetime

from mcp_server.tools.registry import tool_handler
from mcp_server.utils import (
    BrowserError,
    SecurityError,
    ValidationError,
    logger,
    sanitize_path,
    truncate_text,
)

from .browser_config import get_browser_config
from .session_manager import (
    _check_selenium_available,
    _resolve_selector,
    _validate_navigation_url,
    session_manager,
)

# =============================================================================
# Session Management Tools
# =============================================================================


@tool_handler
def browser_open(
    url: str,
    browser: str = "chrome",
    headless: bool = False,
    window_size: str = "1920x1080",
    user_agent: str = "",
    proxy: str = "",
) -> str:
    """
    Open a new browser session and navigate to a URL.

    Creates a new browser instance (Chrome or Edge) and navigates to the
    specified URL. Returns a unique session ID for subsequent operations.

    Args:
        url: URL to navigate to after opening the browser
        browser: Browser type to use ("chrome" or "edge")
        headless: Run in headless mode without visible window
        window_size: Initial window size in WxH format (e.g., "1920x1080")
        user_agent: Custom user agent string (optional)
        proxy: Proxy server URL (optional)

    Returns:
        JSON string with session_id and current URL
    """
    try:
        _validate_navigation_url(url)

        session_id = session_manager.create_session(
            browser=browser,
            headless=headless,
            window_size=window_size,
            user_agent=user_agent,
            proxy=proxy,
        )

        driver = session_manager.get_session(session_id)
        driver.get(url)

        result = {
            "success": True,
            "session_id": session_id,
            "browser": browser,
            "headless": headless,
            "current_url": driver.current_url,
            "title": driver.title,
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except (ValidationError, SecurityError) as e:
        logger.warning(f"browser_open validation error: {e}")
        return json.dumps({"error": str(e)})
    except BrowserError as e:
        logger.error(f"browser_open failed: {e}")
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_open unexpected error: {e}")
        return json.dumps({"error": f"Failed to open browser: {e}"})


@tool_handler
def browser_close(session_id: str) -> str:
    """
    Close a browser session.

    Closes the browser window and cleans up all associated resources.

    Args:
        session_id: The session ID returned by browser_open

    Returns:
        JSON string with success status
    """
    try:
        session_manager.close_session(session_id)
        return json.dumps({"success": True, "message": f"Session {session_id} closed"})
    except BrowserError as e:
        logger.error(f"browser_close failed: {e}")
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_close unexpected error: {e}")
        return json.dumps({"error": f"Failed to close browser: {e}"})


@tool_handler
def browser_list_sessions() -> str:
    """
    List all active browser sessions.

    Returns information about all currently active browser sessions
    including their URLs, titles, and configuration.

    Returns:
        JSON string with list of active sessions
    """
    try:
        sessions = session_manager.list_sessions()
        return json.dumps(
            {
                "success": True,
                "session_count": len(sessions),
                "sessions": sessions,
            },
            indent=2,
            ensure_ascii=False,
        )
    except Exception as e:
        logger.error(f"browser_list_sessions failed: {e}")
        return json.dumps({"error": f"Failed to list sessions: {e}"})


# =============================================================================
# Page Navigation Tools
# =============================================================================


@tool_handler
def browser_navigate(session_id: str, url: str) -> str:
    """
    Navigate to a URL in an existing browser session.

    Args:
        session_id: The session ID
        url: URL to navigate to

    Returns:
        JSON string with current URL and title after navigation
    """
    try:
        _validate_navigation_url(url)
        driver = session_manager.get_session(session_id)
        driver.get(url)

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "current_url": driver.current_url,
                "title": driver.title,
            },
            indent=2,
            ensure_ascii=False,
        )
    except (ValidationError, SecurityError) as e:
        return json.dumps({"error": str(e)})
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_navigate failed: {e}")
        return json.dumps({"error": f"Navigation failed: {e}"})


@tool_handler
def browser_back(session_id: str) -> str:
    """
    Navigate back in browser history.

    Args:
        session_id: The session ID

    Returns:
        JSON string with current URL and title after going back
    """
    try:
        driver = session_manager.get_session(session_id)
        driver.back()
        time.sleep(0.5)  # Allow page to load

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "current_url": driver.current_url,
                "title": driver.title,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_back failed: {e}")
        return json.dumps({"error": f"Back navigation failed: {e}"})


@tool_handler
def browser_forward(session_id: str) -> str:
    """
    Navigate forward in browser history.

    Args:
        session_id: The session ID

    Returns:
        JSON string with current URL and title after going forward
    """
    try:
        driver = session_manager.get_session(session_id)
        driver.forward()
        time.sleep(0.5)  # Allow page to load

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "current_url": driver.current_url,
                "title": driver.title,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_forward failed: {e}")
        return json.dumps({"error": f"Forward navigation failed: {e}"})


@tool_handler
def browser_refresh(session_id: str) -> str:
    """
    Refresh the current page.

    Args:
        session_id: The session ID

    Returns:
        JSON string with current URL and title after refresh
    """
    try:
        driver = session_manager.get_session(session_id)
        driver.refresh()

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "current_url": driver.current_url,
                "title": driver.title,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_refresh failed: {e}")
        return json.dumps({"error": f"Refresh failed: {e}"})


# =============================================================================
# Page Information Tools
# =============================================================================


@tool_handler
def browser_get_page_source(session_id: str, max_length: int = 50000) -> str:
    """
    Get the HTML source code of the current page.

    Args:
        session_id: The session ID
        max_length: Maximum length of source to return (truncated if exceeded)

    Returns:
        JSON string with page source (may be truncated)
    """
    try:
        driver = session_manager.get_session(session_id)
        source = driver.page_source

        truncated = False
        if len(source) > max_length:
            source = truncate_text(source, max_length, suffix="... [TRUNCATED]")
            truncated = True

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "url": driver.current_url,
                "title": driver.title,
                "source_length": len(driver.page_source),
                "truncated": truncated,
                "source": source,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_get_page_source failed: {e}")
        return json.dumps({"error": f"Failed to get page source: {e}"})


@tool_handler
def browser_get_text(
    session_id: str, selector: str = "body", by: str = "css", max_length: int = 20000
) -> str:
    """
    Get the text content of an element.

    Args:
        session_id: The session ID
        selector: Element selector (CSS selector by default)
        by: Selector type (css, xpath, id, name, class, tag)
        max_length: Maximum text length to return

    Returns:
        JSON string with element text content
    """
    try:
        _check_selenium_available()

        driver = session_manager.get_session(session_id)
        by_type = _resolve_selector(by)
        element = driver.find_element(by_type, selector)
        text = element.text

        truncated = False
        if len(text) > max_length:
            text = truncate_text(text, max_length, suffix="... [TRUNCATED]")
            truncated = True

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "selector": selector,
                "text_length": len(element.text),
                "truncated": truncated,
                "text": text,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_get_text failed: {e}")
        return json.dumps({"error": f"Failed to get element text: {e}"})


@tool_handler
def browser_get_url(session_id: str) -> str:
    """
    Get the current page URL and title.

    Args:
        session_id: The session ID

    Returns:
        JSON string with current URL and title
    """
    try:
        driver = session_manager.get_session(session_id)

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "url": driver.current_url,
                "title": driver.title,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_get_url failed: {e}")
        return json.dumps({"error": f"Failed to get URL: {e}"})


# =============================================================================
# Element Interaction Tools
# =============================================================================


@tool_handler
def browser_click(session_id: str, selector: str, by: str = "css", timeout: int = 10) -> str:
    """
    Click an element on the page.

    Waits for the element to be clickable before clicking.

    Args:
        session_id: The session ID
        selector: Element selector
        by: Selector type (css, xpath, id, name, class, tag)
        timeout: Maximum seconds to wait for element

    Returns:
        JSON string with success status
    """
    try:
        _check_selenium_available()
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        driver = session_manager.get_session(session_id)
        by_type = _resolve_selector(by)

        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.element_to_be_clickable((by_type, selector)))
        element.click()

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "action": "click",
                "selector": selector,
                "current_url": driver.current_url,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_click failed: {e}")
        return json.dumps({"error": f"Click failed: {e}"})


@tool_handler
def browser_type(
    session_id: str,
    selector: str,
    text: str,
    by: str = "css",
    clear: bool = True,
    timeout: int = 10,
) -> str:
    """
    Type text into an input element.

    Args:
        session_id: The session ID
        selector: Element selector
        text: Text to type
        by: Selector type (css, xpath, id, name, class, tag)
        clear: Whether to clear existing text first
        timeout: Maximum seconds to wait for element

    Returns:
        JSON string with success status
    """
    try:
        _check_selenium_available()
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        driver = session_manager.get_session(session_id)
        by_type = _resolve_selector(by)

        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((by_type, selector)))

        if clear:
            element.clear()

        element.send_keys(text)

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "action": "type",
                "selector": selector,
                "text_length": len(text),
                "cleared": clear,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_type failed: {e}")
        return json.dumps({"error": f"Type failed: {e}"})


@tool_handler
def browser_select(
    session_id: str,
    selector: str,
    value: str,
    by: str = "css",
    select_by: str = "value",
    timeout: int = 10,
) -> str:
    """
    Select an option from a dropdown/select element.

    Args:
        session_id: The session ID
        selector: Select element selector
        value: Value to select
        by: Selector type for finding the select element
        select_by: How to match the option ("value", "text", or "index")
        timeout: Maximum seconds to wait for element

    Returns:
        JSON string with success status
    """
    try:
        _check_selenium_available()
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import Select, WebDriverWait

        driver = session_manager.get_session(session_id)
        by_type = _resolve_selector(by)

        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((by_type, selector)))

        select = Select(element)

        if select_by == "value":
            select.select_by_value(value)
        elif select_by == "text":
            select.select_by_visible_text(value)
        elif select_by == "index":
            select.select_by_index(int(value))
        else:
            raise ValidationError(f"Invalid select_by value: {select_by}")

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "action": "select",
                "selector": selector,
                "value": value,
                "select_by": select_by,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except ValidationError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_select failed: {e}")
        return json.dumps({"error": f"Select failed: {e}"})


@tool_handler
def browser_wait_for(
    session_id: str,
    selector: str,
    by: str = "css",
    timeout: int = 10,
    condition: str = "present",
) -> str:
    """
    Wait for an element to satisfy a condition.

    Args:
        session_id: The session ID
        selector: Element selector
        by: Selector type (css, xpath, id, name, class, tag)
        timeout: Maximum seconds to wait
        condition: Condition to wait for:
            - "present": Element exists in DOM
            - "visible": Element is visible
            - "clickable": Element is clickable
            - "gone": Element no longer exists

    Returns:
        JSON string with success status
    """
    try:
        _check_selenium_available()
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        driver = session_manager.get_session(session_id)
        by_type = _resolve_selector(by)

        wait = WebDriverWait(driver, timeout)

        if condition == "present":
            wait.until(EC.presence_of_element_located((by_type, selector)))
        elif condition == "visible":
            wait.until(EC.visibility_of_element_located((by_type, selector)))
        elif condition == "clickable":
            wait.until(EC.element_to_be_clickable((by_type, selector)))
        elif condition == "gone":
            wait.until(EC.invisibility_of_element_located((by_type, selector)))
        else:
            raise ValidationError(
                f"Invalid condition: {condition}. " f"Use: present, visible, clickable, gone"
            )

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "selector": selector,
                "condition": condition,
                "timeout": timeout,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except ValidationError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        # Timeout exceptions
        logger.warning(f"browser_wait_for timed out: {e}")
        return json.dumps(
            {
                "error": f"Timeout waiting for element '{selector}' to be {condition}",
                "timeout": timeout,
            }
        )


# =============================================================================
# Screenshot Tool
# =============================================================================


@tool_handler
def browser_screenshot(
    session_id: str,
    save_path: str = "",
    selector: str = "",
    by: str = "css",
    full_page: bool = False,
    filename: str = "",
) -> str:
    """
    Take a screenshot of the page or a specific element.

    Args:
        session_id: The session ID
        save_path: File path to save screenshot (optional)
        selector: Element selector for element screenshot (optional)
        by: Selector type if selector is provided
        full_page: Capture full scrollable page (Chrome only)
        filename: Custom filename (used with configured screenshot_dir)

    Returns:
        JSON string with screenshot info

    Note:
        - If save_path is provided, saves to that exact path
        - If filename is provided and screenshot_dir is configured, saves to {screenshot_dir}/{filename}
        - If neither is provided but screenshot_dir is configured, auto-generates filename with timestamp
        - If nothing is configured, returns base64 encoded image
    """
    try:
        _check_selenium_available()

        driver = session_manager.get_session(session_id)

        if selector:
            # Element screenshot
            by_type = _resolve_selector(by)
            element = driver.find_element(by_type, selector)
            screenshot_data = element.screenshot_as_png
        elif full_page:
            # Full page screenshot using CDP (Chrome/Edge only)
            try:
                # Get full page dimensions
                total_width = driver.execute_script("return document.documentElement.scrollWidth")
                total_height = driver.execute_script("return document.documentElement.scrollHeight")

                # Set viewport to full page size
                driver.set_window_size(total_width, total_height)
                time.sleep(0.5)  # Allow reflow

                screenshot_data = driver.get_screenshot_as_png()

            except Exception as e:
                logger.warning(f"Full page screenshot fallback to regular: {e}")
                screenshot_data = driver.get_screenshot_as_png()
        else:
            # Regular viewport screenshot
            screenshot_data = driver.get_screenshot_as_png()

        # Determine save path
        final_save_path = None

        if save_path:
            # Use explicitly provided path
            final_save_path = sanitize_path(save_path)
        else:
            # Check if screenshot_dir is configured
            config = get_browser_config()
            screenshot_dir = config.get_screenshot_dir_path()

            if screenshot_dir:
                # Generate filename
                if filename:
                    # Use provided filename
                    if not filename.lower().endswith(".png"):
                        filename = f"{filename}.png"
                    final_save_path = screenshot_dir / filename
                else:
                    # Auto-generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    auto_filename = f"screenshot_{timestamp}.png"
                    final_save_path = screenshot_dir / auto_filename

        if final_save_path:
            # Save to file
            final_save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(final_save_path, "wb") as f:
                f.write(screenshot_data)

            return json.dumps(
                {
                    "success": True,
                    "session_id": session_id,
                    "saved_to": str(final_save_path),
                    "size_bytes": len(screenshot_data),
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            # Return base64 encoded
            b64_data = base64.b64encode(screenshot_data).decode("utf-8")
            return json.dumps(
                {
                    "success": True,
                    "session_id": session_id,
                    "format": "png",
                    "size_bytes": len(screenshot_data),
                    "base64": b64_data,
                },
                indent=2,
                ensure_ascii=False,
            )

    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_screenshot failed: {e}")
        return json.dumps({"error": f"Screenshot failed: {e}"})


# =============================================================================
# JavaScript Execution Tool
# =============================================================================


@tool_handler
def browser_execute_js(session_id: str, script: str, args: str = "[]") -> str:
    """
    Execute JavaScript code in the page context.

    Args:
        session_id: The session ID
        script: JavaScript code to execute
        args: JSON array of arguments to pass to the script (accessible via arguments[])

    Returns:
        JSON string with execution result
    """
    try:
        driver = session_manager.get_session(session_id)

        try:
            parsed_args = json.loads(args) if args else []
        except json.JSONDecodeError:
            parsed_args = []

        result = driver.execute_script(script, *parsed_args)

        # Serialize result (handle non-JSON-serializable types)
        try:
            serialized = json.dumps(result, ensure_ascii=False)
            result_data = json.loads(serialized)
        except (TypeError, ValueError):
            result_data = str(result)

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "result": result_data,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_execute_js failed: {e}")
        return json.dumps({"error": f"JavaScript execution failed: {e}"})


# =============================================================================
# Console Log Tool
# =============================================================================


@tool_handler
def browser_get_console_logs(session_id: str, level: str = "all") -> str:
    """
    Get browser console logs.

    Captures console.log, console.error, console.warn, etc. from the page.

    Args:
        session_id: The session ID
        level: Filter by log level (all, error, warning, info, debug)

    Returns:
        JSON string with console log entries
    """
    try:
        logs = session_manager.get_console_logs(session_id, level)

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "level_filter": level,
                "log_count": len(logs),
                "logs": logs,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_get_console_logs failed: {e}")
        return json.dumps({"error": f"Failed to get console logs: {e}"})


# =============================================================================
# Cookie Management Tools
# =============================================================================


@tool_handler
def browser_get_cookies(session_id: str, name: str = "") -> str:
    """
    Get browser cookies.

    Args:
        session_id: The session ID
        name: Filter by cookie name (optional, returns all if empty)

    Returns:
        JSON string with cookie data
    """
    try:
        driver = session_manager.get_session(session_id)
        cookies = driver.get_cookies()

        if name:
            cookies = [c for c in cookies if c.get("name") == name]

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "cookie_count": len(cookies),
                "cookies": cookies,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_get_cookies failed: {e}")
        return json.dumps({"error": f"Failed to get cookies: {e}"})


@tool_handler
def browser_set_cookie(
    session_id: str,
    name: str,
    value: str,
    domain: str = "",
    path: str = "/",
    secure: bool = False,
    http_only: bool = False,
    expiry: int = 0,
) -> str:
    """
    Set a browser cookie.

    Args:
        session_id: The session ID
        name: Cookie name
        value: Cookie value
        domain: Cookie domain (optional, uses current domain if empty)
        path: Cookie path
        secure: Secure flag
        http_only: HttpOnly flag
        expiry: Expiry timestamp (0 for session cookie)

    Returns:
        JSON string with success status
    """
    try:
        driver = session_manager.get_session(session_id)

        cookie = {
            "name": name,
            "value": value,
            "path": path,
            "secure": secure,
            "httpOnly": http_only,
        }

        if domain:
            cookie["domain"] = domain

        if expiry > 0:
            cookie["expiry"] = expiry

        driver.add_cookie(cookie)

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "cookie_name": name,
                "message": f"Cookie '{name}' set successfully",
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_set_cookie failed: {e}")
        return json.dumps({"error": f"Failed to set cookie: {e}"})


@tool_handler
def browser_delete_cookies(session_id: str, name: str = "") -> str:
    """
    Delete browser cookies.

    Args:
        session_id: The session ID
        name: Cookie name to delete (optional, deletes all if empty)

    Returns:
        JSON string with success status
    """
    try:
        driver = session_manager.get_session(session_id)

        if name:
            driver.delete_cookie(name)
            message = f"Cookie '{name}' deleted"
        else:
            driver.delete_all_cookies()
            message = "All cookies deleted"

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "message": message,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_delete_cookies failed: {e}")
        return json.dumps({"error": f"Failed to delete cookies: {e}"})


# =============================================================================
# Network Monitoring Tools
# =============================================================================


@tool_handler
def browser_enable_network_log(session_id: str) -> str:
    """
    Enable network request logging.

    After enabling, network requests will be captured and can be retrieved
    using browser_get_network_logs.

    Args:
        session_id: The session ID

    Returns:
        JSON string with success status
    """
    try:
        session_manager.enable_network_logging(session_id)

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "message": "Network logging enabled. Use browser_get_network_logs to retrieve.",
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_enable_network_log failed: {e}")
        return json.dumps({"error": f"Failed to enable network logging: {e}"})


@tool_handler
def browser_get_network_logs(
    session_id: str,
    filter_url: str = "",
    filter_method: str = "",
    limit: int = 50,
) -> str:
    """
    Get captured network request logs.

    Requires browser_enable_network_log to be called first.

    Args:
        session_id: The session ID
        filter_url: Filter by URL substring (optional)
        filter_method: Filter by HTTP method (GET, POST, etc.)
        limit: Maximum number of entries to return

    Returns:
        JSON string with network log entries
    """
    try:
        logs = session_manager.get_network_logs(
            session_id,
            filter_url=filter_url,
            filter_method=filter_method,
            limit=limit,
        )

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "filter_url": filter_url,
                "filter_method": filter_method,
                "log_count": len(logs),
                "logs": logs,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_get_network_logs failed: {e}")
        return json.dumps({"error": f"Failed to get network logs: {e}"})


# =============================================================================
# Form Filling Tool
# =============================================================================


@tool_handler
def browser_fill_form(session_id: str, form_data: str, by: str = "css") -> str:
    """
    Fill multiple form fields at once.

    Args:
        session_id: The session ID
        form_data: JSON object mapping selectors to values, e.g.:
            '{"#username": "john", "#password": "secret", "#country": "US"}'
        by: Selector type for all fields (css, xpath, id, name, class, tag)

    Returns:
        JSON string with fill results for each field
    """
    try:
        _check_selenium_available()
        from selenium.webdriver.support.ui import Select

        driver = session_manager.get_session(session_id)
        by_type = _resolve_selector(by)

        try:
            fields = json.loads(form_data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid form_data JSON: {e}")

        if not isinstance(fields, dict):
            raise ValidationError("form_data must be a JSON object")

        results = []

        for selector, value in fields.items():
            try:
                element = driver.find_element(by_type, selector)
                tag_name = element.tag_name.lower()

                if tag_name == "select":
                    # Dropdown
                    select = Select(element)
                    try:
                        select.select_by_value(str(value))
                    except Exception:
                        select.select_by_visible_text(str(value))
                    results.append({"selector": selector, "status": "selected", "value": value})

                elif tag_name == "input":
                    input_type = element.get_attribute("type") or "text"
                    if input_type in ("checkbox", "radio"):
                        # Checkbox/radio
                        should_check = str(value).lower() in ("true", "1", "yes", "on")
                        is_checked = element.is_selected()
                        if should_check != is_checked:
                            element.click()
                        results.append(
                            {"selector": selector, "status": "toggled", "checked": should_check}
                        )
                    else:
                        # Text input
                        element.clear()
                        element.send_keys(str(value))
                        results.append({"selector": selector, "status": "typed", "value": value})

                elif tag_name == "textarea":
                    element.clear()
                    element.send_keys(str(value))
                    results.append({"selector": selector, "status": "typed", "value": value})

                else:
                    # Try to type anyway
                    element.clear()
                    element.send_keys(str(value))
                    results.append({"selector": selector, "status": "typed", "value": value})

            except Exception as e:
                results.append({"selector": selector, "status": "error", "error": str(e)})

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "fields_processed": len(results),
                "results": results,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except ValidationError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_fill_form failed: {e}")
        return json.dumps({"error": f"Form fill failed: {e}"})


# =============================================================================
# Multi-Tab Management Tools
# =============================================================================


@tool_handler
def browser_new_tab(session_id: str, url: str = "") -> str:
    """
    Open a new browser tab.

    Args:
        session_id: The session ID
        url: URL to navigate to in new tab (optional)

    Returns:
        JSON string with new tab info
    """
    try:
        driver = session_manager.get_session(session_id)

        # Open new tab via JavaScript
        driver.execute_script("window.open('');")

        # Switch to new tab
        handles = driver.window_handles
        driver.switch_to.window(handles[-1])

        if url:
            _validate_navigation_url(url)
            driver.get(url)

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "tab_index": len(handles) - 1,
                "tab_count": len(handles),
                "current_url": driver.current_url,
            },
            indent=2,
            ensure_ascii=False,
        )
    except (ValidationError, SecurityError) as e:
        return json.dumps({"error": str(e)})
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_new_tab failed: {e}")
        return json.dumps({"error": f"Failed to open new tab: {e}"})


@tool_handler
def browser_switch_tab(session_id: str, tab_index: int) -> str:
    """
    Switch to a different browser tab by index.

    Args:
        session_id: The session ID
        tab_index: Tab index (0-based)

    Returns:
        JSON string with current tab info
    """
    try:
        driver = session_manager.get_session(session_id)
        handles = driver.window_handles

        if tab_index < 0 or tab_index >= len(handles):
            raise ValidationError(
                f"Invalid tab index {tab_index}. Valid range: 0-{len(handles) - 1}"
            )

        driver.switch_to.window(handles[tab_index])

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "tab_index": tab_index,
                "tab_count": len(handles),
                "current_url": driver.current_url,
                "title": driver.title,
            },
            indent=2,
            ensure_ascii=False,
        )
    except ValidationError as e:
        return json.dumps({"error": str(e)})
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_switch_tab failed: {e}")
        return json.dumps({"error": f"Failed to switch tab: {e}"})


@tool_handler
def browser_close_tab(session_id: str, tab_index: int = -1) -> str:
    """
    Close a browser tab.

    Args:
        session_id: The session ID
        tab_index: Tab index to close (-1 for current tab)

    Returns:
        JSON string with remaining tabs info
    """
    try:
        driver = session_manager.get_session(session_id)
        handles = driver.window_handles

        if len(handles) <= 1:
            raise ValidationError(
                "Cannot close the last tab. Use browser_close to close the session."
            )

        if tab_index == -1:
            # Close current tab
            driver.close()
            # Switch to first remaining tab
            driver.switch_to.window(driver.window_handles[0])
        else:
            if tab_index < 0 or tab_index >= len(handles):
                raise ValidationError(
                    f"Invalid tab index {tab_index}. Valid range: 0-{len(handles) - 1}"
                )

            # Switch to target tab and close
            current_handle = driver.current_window_handle
            driver.switch_to.window(handles[tab_index])
            driver.close()

            # Switch back or to first tab if current was closed
            remaining = driver.window_handles
            if current_handle in remaining:
                driver.switch_to.window(current_handle)
            else:
                driver.switch_to.window(remaining[0])

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "tab_count": len(driver.window_handles),
                "current_url": driver.current_url,
            },
            indent=2,
            ensure_ascii=False,
        )
    except ValidationError as e:
        return json.dumps({"error": str(e)})
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_close_tab failed: {e}")
        return json.dumps({"error": f"Failed to close tab: {e}"})


@tool_handler
def browser_list_tabs(session_id: str) -> str:
    """
    List all open tabs in the browser session.

    Args:
        session_id: The session ID

    Returns:
        JSON string with all tabs info
    """
    try:
        driver = session_manager.get_session(session_id)
        current_handle = driver.current_window_handle
        handles = driver.window_handles

        tabs = []
        for i, handle in enumerate(handles):
            driver.switch_to.window(handle)
            tabs.append(
                {
                    "index": i,
                    "handle": handle,
                    "url": driver.current_url,
                    "title": driver.title,
                    "is_current": handle == current_handle,
                }
            )

        # Switch back to original tab
        driver.switch_to.window(current_handle)

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "tab_count": len(tabs),
                "tabs": tabs,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_list_tabs failed: {e}")
        return json.dumps({"error": f"Failed to list tabs: {e}"})


# =============================================================================
# Element Query Tools
# =============================================================================


@tool_handler
def browser_find_elements(
    session_id: str,
    selector: str,
    by: str = "css",
    limit: int = 20,
) -> str:
    """
    Find multiple elements matching a selector.

    Args:
        session_id: The session ID
        selector: Element selector
        by: Selector type (css, xpath, id, name, class, tag)
        limit: Maximum number of elements to return

    Returns:
        JSON string with element info (tag, text preview, attributes)
    """
    try:
        _check_selenium_available()

        driver = session_manager.get_session(session_id)
        by_type = _resolve_selector(by)

        elements = driver.find_elements(by_type, selector)[:limit]

        element_data = []
        for i, elem in enumerate(elements):
            try:
                text = elem.text[:100] + "..." if len(elem.text) > 100 else elem.text
                element_data.append(
                    {
                        "index": i,
                        "tag": elem.tag_name,
                        "text": text,
                        "id": elem.get_attribute("id") or "",
                        "class": elem.get_attribute("class") or "",
                        "href": elem.get_attribute("href") or "",
                        "value": elem.get_attribute("value") or "",
                        "is_displayed": elem.is_displayed(),
                        "is_enabled": elem.is_enabled(),
                    }
                )
            except Exception:
                continue

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "selector": selector,
                "element_count": len(element_data),
                "elements": element_data,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_find_elements failed: {e}")
        return json.dumps({"error": f"Failed to find elements: {e}"})


@tool_handler
def browser_get_element_attribute(
    session_id: str,
    selector: str,
    attribute: str,
    by: str = "css",
) -> str:
    """
    Get an attribute value from an element.

    Args:
        session_id: The session ID
        selector: Element selector
        attribute: Attribute name to get
        by: Selector type (css, xpath, id, name, class, tag)

    Returns:
        JSON string with attribute value
    """
    try:
        _check_selenium_available()

        driver = session_manager.get_session(session_id)
        by_type = _resolve_selector(by)

        element = driver.find_element(by_type, selector)
        value = element.get_attribute(attribute)

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "selector": selector,
                "attribute": attribute,
                "value": value,
            },
            indent=2,
            ensure_ascii=False,
        )
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_get_element_attribute failed: {e}")
        return json.dumps({"error": f"Failed to get attribute: {e}"})


@tool_handler
def browser_scroll(
    session_id: str,
    direction: str = "down",
    amount: int = 500,
    selector: str = "",
    by: str = "css",
) -> str:
    """
    Scroll the page or scroll an element into view.

    Args:
        session_id: The session ID
        direction: Scroll direction (up, down, left, right, top, bottom)
        amount: Pixels to scroll (for up/down/left/right)
        selector: Element to scroll into view (optional, overrides direction)
        by: Selector type if selector is provided

    Returns:
        JSON string with scroll result
    """
    try:
        _check_selenium_available()

        driver = session_manager.get_session(session_id)

        if selector:
            # Scroll element into view
            by_type = _resolve_selector(by)
            element = driver.find_element(by_type, selector)
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element
            )
            action = f"scrolled to element '{selector}'"
        else:
            # Scroll page
            if direction == "down":
                driver.execute_script(f"window.scrollBy(0, {amount});")
                action = f"scrolled down {amount}px"
            elif direction == "up":
                driver.execute_script(f"window.scrollBy(0, -{amount});")
                action = f"scrolled up {amount}px"
            elif direction == "left":
                driver.execute_script(f"window.scrollBy(-{amount}, 0);")
                action = f"scrolled left {amount}px"
            elif direction == "right":
                driver.execute_script(f"window.scrollBy({amount}, 0);")
                action = f"scrolled right {amount}px"
            elif direction == "top":
                driver.execute_script("window.scrollTo(0, 0);")
                action = "scrolled to top"
            elif direction == "bottom":
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                action = "scrolled to bottom"
            else:
                raise ValidationError(
                    f"Invalid direction: {direction}. Use: up, down, left, right, top, bottom"
                )

        return json.dumps(
            {
                "success": True,
                "session_id": session_id,
                "action": action,
            },
            indent=2,
            ensure_ascii=False,
        )
    except ValidationError as e:
        return json.dumps({"error": str(e)})
    except BrowserError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"browser_scroll failed: {e}")
        return json.dumps({"error": f"Scroll failed: {e}"})


# =============================================================================
# Browser Configuration Management Tools
# =============================================================================


@tool_handler
def browser_config_get(key: str = "") -> str:
    """
    获取浏览器配置设置

    Args:
        key: 配置键名。留空获取所有配置。
             可选值: chrome_driver_path, edge_driver_path, default_browser,
                    default_headless, proxy, auto_fallback, screenshot_dir, all

    Returns:
        JSON格式的配置信息
    """
    try:
        from .browser_config import get_browser_config

        config = get_browser_config()

        if not key or key == "all":
            result = config.get_all_settings()
        elif key == "chrome_driver_path":
            result = {"chrome_driver_path": config.get_chrome_driver_path()}
        elif key == "edge_driver_path":
            result = {"edge_driver_path": config.get_edge_driver_path()}
        elif key == "default_browser":
            result = {"default_browser": config.get_default_browser()}
        elif key == "default_headless":
            result = {"default_headless": config.get_default_headless()}
        elif key == "proxy":
            result = {"proxy": config.get_proxy()}
        elif key == "auto_fallback":
            result = {"auto_fallback": config.get_auto_fallback_enabled()}
        elif key == "screenshot_dir":
            result = {"screenshot_dir": config.get_screenshot_dir()}
        else:
            return json.dumps({"error": f"Unknown config key: {key}"})

        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"browser_config_get failed: {e}")
        return json.dumps({"error": f"Failed to get config: {e}"})


@tool_handler
def browser_config_set(key: str, value: str) -> str:
    """
    设置浏览器配置（保存到配置文件）

    Args:
        key: 配置键名 (chrome_driver_path, edge_driver_path, default_browser,
             default_headless, proxy, auto_fallback, screenshot_dir)
        value: 配置值

    Returns:
        JSON格式的操作结果
    """
    try:
        from .browser_config import get_browser_config

        config = get_browser_config()

        if key == "chrome_driver_path":
            config.set_chrome_driver_path(value)
        elif key == "edge_driver_path":
            config.set_edge_driver_path(value)
        elif key == "default_browser":
            config.set_default_browser(value)
        elif key == "default_headless":
            headless = value.lower() in ("true", "1", "yes", "on")
            config.set_default_headless(headless)
        elif key == "proxy":
            config.set_proxy(value)
        elif key == "auto_fallback":
            enabled = value.lower() in ("true", "1", "yes", "on")
            config.set_auto_fallback(enabled)
        elif key == "screenshot_dir":
            config.set_screenshot_dir(value)
        else:
            return json.dumps({"error": f"Unknown config key: {key}"})

        result = {
            "success": True,
            "message": f"Configuration saved: {key} = {value}",
            "config_file": str(config.config_path),
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"browser_config_set failed: {e}")
        return json.dumps({"error": f"Failed to set config: {e}"})


@tool_handler
def browser_config_reset() -> str:
    """
    重置浏览器配置为默认值

    Returns:
        JSON格式的操作结果
    """
    try:
        from .browser_config import get_browser_config

        config = get_browser_config()
        config.reset_config()

        return json.dumps(
            {
                "success": True,
                "message": "Browser configuration has been reset to defaults",
                "config_file": str(config.config_path),
            },
            indent=2,
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"browser_config_reset failed: {e}")
        return json.dumps({"error": f"Failed to reset config: {e}"})
