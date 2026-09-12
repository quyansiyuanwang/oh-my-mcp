# MCP Server Tool Reference

This document provides a detailed reference for all tools available in the MCP server, organized by category. For usage examples and API details, see the main README or category-specific documentation.

---

<!-- DOCGEN:tool-reference:start -->
## 🌐 Browser Automation Tools (33)

### `browser_open`
Open a new browser session and navigate to a URL.

```python
browser_open(url: str, browser: str = 'chrome', headless: bool = False, window_size: str = '1920x1080', user_agent: str = '', proxy: str = '')
```

### `browser_close`
Close a browser session.

```python
browser_close(session_id: str)
```

### `browser_list_sessions`
List all active browser sessions.

```python
browser_list_sessions()
```

### `browser_navigate`
Navigate to a URL in an existing browser session.

```python
browser_navigate(session_id: str, url: str)
```

### `browser_back`
Navigate back in browser history.

```python
browser_back(session_id: str)
```

### `browser_forward`
Navigate forward in browser history.

```python
browser_forward(session_id: str)
```

### `browser_refresh`
Refresh the current page.

```python
browser_refresh(session_id: str)
```

### `browser_get_page_source`
Get the HTML source code of the current page.

```python
browser_get_page_source(session_id: str, max_length: int = 50000)
```

### `browser_get_text`
Get the text content of an element.

```python
browser_get_text(session_id: str, selector: str = 'body', by: str = 'css', max_length: int = 20000)
```

### `browser_get_url`
Get the current page URL and title.

```python
browser_get_url(session_id: str)
```

### `browser_click`
Click an element on the page.

```python
browser_click(session_id: str, selector: str, by: str = 'css', timeout: int = 10)
```

### `browser_type`
Type text into an input element.

```python
browser_type(session_id: str, selector: str, text: str, by: str = 'css', clear: bool = True, timeout: int = 10)
```

### `browser_select`
Select an option from a dropdown/select element.

```python
browser_select(session_id: str, selector: str, value: str, by: str = 'css', select_by: str = 'value', timeout: int = 10)
```

### `browser_wait_for`
Wait for an element to satisfy a condition.

```python
browser_wait_for(session_id: str, selector: str, by: str = 'css', timeout: int = 10, condition: str = 'present')
```

### `browser_screenshot`
Take a screenshot of the page or a specific element.

```python
browser_screenshot(session_id: str, save_path: str = '', selector: str = '', by: str = 'css', full_page: bool = False, filename: str = '')
```

### `browser_execute_js`
Execute JavaScript code in the page context.

```python
browser_execute_js(session_id: str, script: str, args: str = '[]')
```

### `browser_get_console_logs`
Get browser console logs.

```python
browser_get_console_logs(session_id: str, level: str = 'all')
```

### `browser_get_cookies`
Get browser cookies.

```python
browser_get_cookies(session_id: str, name: str = '')
```

### `browser_set_cookie`
Set a browser cookie.

```python
browser_set_cookie(session_id: str, name: str, value: str, domain: str = '', path: str = '/', secure: bool = False, http_only: bool = False, expiry: int = 0)
```

### `browser_delete_cookies`
Delete browser cookies.

```python
browser_delete_cookies(session_id: str, name: str = '')
```

### `browser_enable_network_log`
Enable network request logging.

```python
browser_enable_network_log(session_id: str)
```

### `browser_get_network_logs`
Get captured network request logs.

```python
browser_get_network_logs(session_id: str, filter_url: str = '', filter_method: str = '', limit: int = 50)
```

### `browser_fill_form`
Fill multiple form fields at once.

```python
browser_fill_form(session_id: str, form_data: str, by: str = 'css')
```

### `browser_new_tab`
Open a new browser tab.

```python
browser_new_tab(session_id: str, url: str = '')
```

### `browser_switch_tab`
Switch to a different browser tab by index.

```python
browser_switch_tab(session_id: str, tab_index: int)
```

### `browser_close_tab`
Close a browser tab.

```python
browser_close_tab(session_id: str, tab_index: int = -1)
```

### `browser_list_tabs`
List all open tabs in the browser session.

```python
browser_list_tabs(session_id: str)
```

### `browser_find_elements`
Find multiple elements matching a selector.

```python
browser_find_elements(session_id: str, selector: str, by: str = 'css', limit: int = 20)
```

### `browser_get_element_attribute`
Get an attribute value from an element.

```python
browser_get_element_attribute(session_id: str, selector: str, attribute: str, by: str = 'css')
```

### `browser_scroll`
Scroll the page or scroll an element into view.

```python
browser_scroll(session_id: str, direction: str = 'down', amount: int = 500, selector: str = '', by: str = 'css')
```

### `browser_config_get`
获取浏览器配置设置

```python
browser_config_get(key: str = '')
```

### `browser_config_set`
设置浏览器配置（保存到配置文件）

```python
browser_config_set(key: str, value: str)
```

### `browser_config_reset`
重置浏览器配置为默认值

```python
browser_config_reset()
```

---

## 📦 Compression Tools (5)

### `compress_zip`
Create a ZIP archive from files and/or directories.

```python
compress_zip(files: List[str], output_path: str, compression_level: int = 6)
```

### `extract_zip`
Extract a ZIP archive.

```python
extract_zip(zip_path: str, extract_to: str = '.', password: Optional[str] = None)
```

### `compress_tar`
Create a TAR archive from files and/or directories.

```python
compress_tar(files: List[str], output_path: str, compression: str = 'gz')
```

### `extract_tar`
Extract a TAR archive.

```python
extract_tar(tar_path: str, extract_to: str = '.')
```

### `list_archive_contents`
List contents of an archive file without extracting.

```python
list_archive_contents(archive_path: str)
```

---

## 🖥️ Computer Use Tools (25)

### `computer_screenshot`
Capture the screen and return it as a saved PNG file or base64-encoded PNG.

```python
computer_screenshot(save_path: str = '', filename: str = '', region: str = '', monitor: int = 0)
```

### `computer_get_screen_size`
Get the size of the primary display in pixels.

```python
computer_get_screen_size()
```

### `computer_get_monitors`
List all connected displays with their geometry.

```python
computer_get_monitors()
```

### `computer_get_pixel_color`
Get the RGB color of a pixel on the primary display.

```python
computer_get_pixel_color(x: int, y: int)
```

### `computer_locate_on_screen`
Locate an image on the screen and return its center coordinates.

```python
computer_locate_on_screen(image_path: str, confidence: float = 0.9, grayscale: bool = False)
```

### `computer_mouse_move`
Move the mouse cursor.

```python
computer_mouse_move(x: int, y: int, duration: float = 0.25, relative: bool = False)
```

### `computer_mouse_click`
Click a mouse button, optionally after moving to a position.

```python
computer_mouse_click(x: int = -1, y: int = -1, button: str = 'left', clicks: int = 1, interval: float = 0.1)
```

### `computer_mouse_drag`
Drag from one position to another (or drag the current position).

```python
computer_mouse_drag(start_x: int = -1, start_y: int = -1, end_x: int = 0, end_y: int = 0, duration: float = 0.5, button: str = 'left')
```

### `computer_mouse_scroll`
Scroll the mouse wheel.

```python
computer_mouse_scroll(amount: int, x: int = -1, y: int = -1, horizontal: bool = False)
```

### `computer_mouse_get_position`
Get the current mouse cursor position.

```python
computer_mouse_get_position()
```

### `computer_type_text`
Type text into the currently focused window.

```python
computer_type_text(text: str, interval: float = 0.0)
```

### `computer_press_key`
Press a keyboard key (e.g. enter, esc, tab, f5, space, a).

```python
computer_press_key(key: str, presses: int = 1, interval: float = 0.1)
```

### `computer_hotkey`
Press a hotkey combination (e.g. "ctrl+c", "ctrl+shift+esc", "alt+f4").

```python
computer_hotkey(keys: str)
```

### `computer_clipboard_read`
Read the current clipboard text content.

```python
computer_clipboard_read()
```

### `computer_clipboard_write`
Write text to the clipboard.

```python
computer_clipboard_write(text: str)
```

### `computer_list_windows`
List open windows with title, geometry, and state.

```python
computer_list_windows(title_filter: str = '')
```

### `computer_focus_window`
Bring a window to the foreground by title substring.

```python
computer_focus_window(title: str)
```

### `computer_get_window_info`
Get detailed information about a window by title substring.

```python
computer_get_window_info(title: str)
```

### `computer_resize_window`
Resize a window by title substring.

```python
computer_resize_window(title: str, width: int, height: int)
```

### `computer_move_window`
Move a window by title substring to a new position.

```python
computer_move_window(title: str, x: int, y: int)
```

### `computer_minimize_window`
Minimize a window by title substring.

```python
computer_minimize_window(title: str)
```

### `computer_maximize_window`
Maximize a window by title substring.

```python
computer_maximize_window(title: str)
```

### `computer_wait`
Wait for a given number of seconds (useful between UI actions while

```python
computer_wait(duration: float)
```

### `computer_config_get`
Get the computer use module configuration.

```python
computer_config_get()
```

### `computer_config_set`
Update the computer use module configuration.

```python
computer_config_set(pause: float | None = None, failsafe: bool | None = None, screenshot_dir: str | None = None)
```

---

## 📊 Data Processing Tools (15)

### `parse_json`
Parse and validate a JSON string.

```python
parse_json(json_string: str)
```

### `format_json`
Format JSON with pretty printing.

```python
format_json(json_string: str, indent: int = 2, sort_keys: bool = False)
```

### `json_query`
Extract value from JSON using dot notation path.

```python
json_query(json_string: str, path: str)
```

### `csv_to_json`
Convert CSV data to JSON.

```python
csv_to_json(csv_string: str, delimiter: str = ',', has_header: bool = True)
```

### `json_to_csv`
Convert JSON array to CSV format.

```python
json_to_csv(json_string: str)
```

### `parse_csv`
Parse CSV data and return as JSON.

```python
parse_csv(csv_string: str, delimiter: str = ',')
```

### `validate_json_schema`
Validate JSON syntax and structure.

```python
validate_json_schema(json_string: str)
```

### `flatten_json`
Flatten nested JSON object into single-level object.

```python
flatten_json(json_string: str, separator: str = '.')
```

### `merge_json`
Merge two JSON objects.

```python
merge_json(json_string1: str, json_string2: str, deep: bool = True)
```

### `xml_to_json`
Convert XML to JSON format.

```python
xml_to_json(xml_string: str)
```

### `parse_yaml`
Parse YAML string to JSON.

```python
parse_yaml(yaml_string: str)
```

### `yaml_to_json`
Convert YAML to formatted JSON.

```python
yaml_to_json(yaml_string: str, indent: int = 2)
```

### `json_to_yaml`
Convert JSON to YAML format.

```python
json_to_yaml(json_string: str)
```

### `parse_toml`
Parse TOML configuration file to JSON.

```python
parse_toml(toml_string: str)
```

### `toml_to_json`
Convert TOML to formatted JSON.

```python
toml_to_json(toml_string: str, indent: int = 2)
```

---

## ⚡ Command Execution Tools (4)

### `run_command`
Execute an allowlisted command with sanitized arguments (no shell).

```python
run_command(command: str, args: str = '', cwd: str = '', timeout: int = COMMAND_TIMEOUT_DEFAULT)
```

### `list_allowed_commands`
List the commands that run_command is allowed to execute.

```python
list_allowed_commands()
```

### `add_allowed_commands`
Permanently allow commands for run_command (persisted across restarts).

```python
add_allowed_commands(commands: list[str])
```

### `remove_allowed_commands`
Remove commands from the run_command allowlist (persisted).

```python
remove_allowed_commands(commands: list[str])
```

---

## 📁 File System Tools (13)

### `read_file`
Read the contents of a file.

```python
read_file(path: str, encoding: str = 'utf-8')
```

### `write_file`
Write content to a file.

```python
write_file(path: str, content: str, encoding: str = 'utf-8', overwrite: bool = True)
```

### `append_file`
Append content to a file.

```python
append_file(path: str, content: str, encoding: str = 'utf-8')
```

### `list_directory`
List contents of a directory.

```python
list_directory(path: str = '.', pattern: str = '*', recursive: bool = False)
```

### `file_exists`
Check if a file or directory exists.

```python
file_exists(path: str)
```

### `get_file_info`
Get detailed information about a file or directory.

```python
get_file_info(path: str)
```

### `search_files`
Search for files in a directory.

```python
search_files(directory: str = '.', pattern: str = '*', name_contains: str = '')
```

### `create_directory`
Create a directory.

```python
create_directory(path: str, parents: bool = True)
```

### `delete_file`
Delete a file (requires confirmation).

```python
delete_file(path: str, confirm: bool = False)
```

### `copy_file`
Copy a file from source to destination.

```python
copy_file(source: str, destination: str, overwrite: bool = False)
```

### `diff_files`
Compare two files and show differences.

```python
diff_files(file1: str, file2: str, context_lines: int = 3, format: str = 'unified')
```

### `diff_text`
Compare two text strings and show differences.

```python
diff_text(text1: str, text2: str, format: str = 'unified')
```

### `grep_files`
Search file contents in a directory tree for a text string or regex.

```python
grep_files(directory: str = '.', pattern: str = '*', text: str = '', regex: str = '', ignore_case: bool = True, max_results: int = 100)
```

---

## 🤖 Subagent AI Orchestration Tools (6)

### `subagent_call`
Call an external AI model to handle a subtask.

```python
subagent_call(provider: str, model: str, messages: str, max_tokens: Optional[int] = None, temperature: float = 0.7)
```

### `subagent_parallel`
Execute multiple AI subtasks in parallel with result aggregation.

```python
subagent_parallel(tasks: str, max_workers: int = 3)
```

### `subagent_conditional`
Execute conditional branching based on AI decision.

```python
subagent_conditional(condition_task: str, true_task: str, false_task: str)
```

### `subagent_config_set`
设置 Subagent 提供商的 API 配置（持久化保存）

```python
subagent_config_set(provider: str, api_key: str, api_base: Optional[str] = None)
```

### `subagent_config_get`
获取指定提供商的 API 配置信息

```python
subagent_config_get(provider: str)
```

### `subagent_config_list`
列出所有已配置的 AI 提供商

```python
subagent_config_list()
```

---

## 💻 System Tools (8)

### `get_system_info`
Get comprehensive system information.

```python
get_system_info()
```

### `get_cpu_info`
Get CPU information and current usage.

```python
get_cpu_info()
```

### `get_memory_info`
Get memory (RAM) usage statistics.

```python
get_memory_info()
```

### `get_disk_info`
Get disk space information for a path.

```python
get_disk_info(path: str = '/')
```

### `get_env_variable`
Get an environment variable value.

```python
get_env_variable(name: str, default: str = '')
```

### `list_env_variables`
List all environment variables.

```python
list_env_variables(filter_pattern: str = '')
```

### `get_current_time`
Get current date and time.

```python
get_current_time(timezone: str = 'local', format: str = 'iso')
```

### `get_process_info`
Get information about the current process.

```python
get_process_info()
```

---

## 📝 Text Processing Tools (9)

### `count_words`
Count words and provide text statistics.

```python
count_words(text: str, detailed: bool = True)
```

### `extract_emails`
Extract all email addresses from text.

```python
extract_emails(text: str)
```

### `extract_urls`
Extract all URLs from text.

```python
extract_urls(text: str)
```

### `regex_match`
Find all matches of a regular expression in text.

```python
regex_match(text: str, pattern: str, flags: str = '')
```

### `regex_replace`
Replace text matching a regular expression.

```python
regex_replace(text: str, pattern: str, replacement: str, flags: str = '')
```

### `text_summary`
Summarize or truncate text to a maximum length.

```python
text_summary(text: str, max_length: int = 500, method: str = 'truncate')
```

### `encode_base64`
Encode text to Base64.

```python
encode_base64(text: str, encoding: str = 'utf-8')
```

### `decode_base64`
Decode Base64 to text.

```python
decode_base64(encoded: str, encoding: str = 'utf-8')
```

### `calculate_text_similarity`
Calculate similarity between two text strings.

```python
calculate_text_similarity(text1: str, text2: str, method: str = 'levenshtein')
```

---

## 🛠️ Utilities Tools (10)

### `generate_uuid`
Generate a UUID.

```python
generate_uuid(version: int = 4, uppercase: bool = False)
```

### `generate_hash`
Generate hash of text using specified algorithm.

```python
generate_hash(text: str, algorithm: str = 'sha256', encoding: str = 'utf-8')
```

### `timestamp_to_date`
Convert Unix timestamp to readable date.

```python
timestamp_to_date(timestamp: float, format: str = 'iso', timezone: str = 'local')
```

### `date_to_timestamp`
Convert date string to Unix timestamp.

```python
date_to_timestamp(date_string: str, timezone: str = 'local')
```

### `calculate_date_diff`
Calculate difference between two dates.

```python
calculate_date_diff(date1: str, date2: str, unit: str = 'days')
```

### `format_date`
Format a date string using custom format.

```python
format_date(date_string: str, format: str = '%Y-%m-%d %H:%M:%S')
```

### `calculate_expression`
Safely evaluate a mathematical expression.

```python
calculate_expression(expression: str)
```

### `generate_random_string`
Generate a random string.

```python
generate_random_string(length: int = 16, charset: str = 'alphanumeric')
```

### `generate_password`
Generate a strong password.

```python
generate_password(length: int = 16, include_symbols: bool = True, include_numbers: bool = True, exclude_ambiguous: bool = True)
```

### `check_password_strength`
Check password strength and provide recommendations.

```python
check_password_strength(password: str)
```

---

## 🌐 Web & Network Tools (18)

### `web_search`
Search the web using multiple search engines with智能 fallback.

```python
web_search(query: str, max_results: int = 10)
```

### `web_search_advanced`
Advanced web search with multi-engine support and parallel searching.

```python
web_search_advanced(query: str, max_results: int = 10, engines: str = 'duckduckgo,bing', parallel: bool = False, use_cache: bool = True)
```

### `web_search_news`
Search for news articles using multiple search engines with fallback.

```python
web_search_news(query: str, max_results: int = 10)
```

### `clear_search_cache`
Clear the search cache.

```python
clear_search_cache()
```

### `get_search_stats`
Get search cache and rate limiter statistics.

```python
get_search_stats()
```

### `fetch_webpage`
Fetch the HTML content of a webpage.

```python
fetch_webpage(url: str, timeout: int = 10)
```

### `fetch_webpage_text`
Fetch and extract clean text content from a webpage.

```python
fetch_webpage_text(url: str, timeout: int = 10)
```

### `parse_html`
Parse HTML and extract elements using CSS selector.

```python
parse_html(html: str, selector: str)
```

### `download_file`
Download a file from URL and save to disk.

```python
download_file(url: str, save_path: str, timeout: int = 30)
```

### `get_page_title`
Extract the title from a webpage.

```python
get_page_title(url: str, timeout: int = 10)
```

### `get_page_links`
Extract all links from a webpage.

```python
get_page_links(url: str, timeout: int = 10, absolute: bool = True)
```

### `check_url_status`
Check the HTTP status of a URL.

```python
check_url_status(url: str, timeout: int = 10)
```

### `get_headers`
Get HTTP headers from a URL.

```python
get_headers(url: str, timeout: int = 10)
```

### `validate_url_format`
Validate if a string is a properly formatted URL.

```python
validate_url_format(url: str)
```

### `parse_url_components`
Parse a URL and extract its components.

```python
parse_url_components(url: str)
```

### `http_request`
Make HTTP request with custom headers and body.

```python
http_request(url: str, method: str = 'GET', headers: str = '{}', body: Optional[str] = None, timeout: int = 10)
```

### `get_network_info`
Get network interface information.

```python
get_network_info()
```

### `dns_lookup`
Perform DNS lookup.

```python
dns_lookup(hostname: str, record_type: str = 'A')
```


<!-- DOCGEN:tool-reference:end -->
---

For detailed usage, see the main README or category-specific documentation in the docs folder.
