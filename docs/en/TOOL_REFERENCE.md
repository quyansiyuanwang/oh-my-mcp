# MCP Server Tool Reference

This document provides a detailed reference for all tools available in the MCP server, organized by category. For usage examples and API details, see the main README or category-specific documentation.

---

## 📦 Compression Tools (5)

### `compress_zip`
Create a ZIP archive from files.

### `extract_zip`
Extract files from a ZIP archive with security checks.

### `compress_tar`
Create a TAR archive (optionally compressed with gzip or bzip2).

### `extract_tar`
Extract files from a TAR archive.

### `list_archive_contents`
List contents of a ZIP or TAR archive without extracting.

---

## 🌐 Web & Network Tools (18)

- `web_search`: DuckDuckGo search
- `fetch_webpage`: Fetch HTML content
- `fetch_webpage_text`: Extract clean text
- `parse_html`: CSS selector parsing
- `download_file`: Download files
- `get_page_title`: Extract page title
- `get_page_links`: Extract all links
- `check_url_status`: HTTP status check
- `get_headers`: HTTP headers
- `validate_url_format`: URL validation
- `parse_url_components`: URL parsing
- `web_search_news`: News search
- `http_request`: Generic HTTP client
- `get_network_info`: Network info
- `dns_lookup`: DNS lookup

---

## 📁 File System Tools (12)

- `read_file`, `write_file`, `append_file`
- `list_directory`, `file_exists`, `get_file_info`
- `search_files`, `create_directory`, `delete_file`, `copy_file`
- `diff_files`, `diff_text`

---

## 📊 Data Processing Tools (15)

- `parse_json`, `format_json`, `json_query`, `csv_to_json`, `json_to_csv`, `parse_csv`, `validate_json_schema`, `flatten_json`, `merge_json`, `xml_to_json`, `parse_yaml`, `yaml_to_json`, `json_to_yaml`, `parse_toml`, `toml_to_json`

---

## 📝 Text Processing Tools (9)

- `count_words`, `extract_emails`, `extract_urls`, `regex_match`, `regex_replace`, `text_summary`, `encode_base64`, `decode_base64`, `calculate_text_similarity`

---

## 💻 System Tools (8)

- `get_system_info`, `get_cpu_info`, `get_memory_info`, `get_disk_info`, `get_env_variable`, `list_env_variables`, `get_current_time`, `get_process_info`

---

## 🛠️ Utility Tools (10)

- `generate_uuid`, `generate_hash`, `timestamp_to_date`, `date_to_timestamp`, `calculate_date_diff`, `format_date`, `calculate_expression`, `generate_random_string`, `generate_password`, `check_password_strength`

---

## 🤖 Subagent AI Orchestration (6)

- `subagent_call`, `subagent_parallel`, `subagent_conditional`, `subagent_config_set`, `subagent_config_get`, `subagent_config_list`

---

## 🖥️ Computer Use Tools (25)

### `computer_screenshot`
Capture the screen/region/monitor, save to file or return base64 PNG.

### `computer_get_screen_size`
Get the primary display size in pixels.

### `computer_get_monitors`
List all connected displays with their geometry.

### `computer_get_pixel_color`
Get the RGB/hex color of a pixel at a coordinate.

### `computer_locate_on_screen`
Locate a reference image on screen and return its center coordinates.

### `computer_mouse_move`
Move the mouse cursor (absolute or relative).

### `computer_mouse_click`
Click left/right/middle button, single or double.

### `computer_mouse_drag`
Drag from one position to another.

### `computer_mouse_scroll`
Vertical or horizontal mouse wheel scroll.

### `computer_mouse_get_position`
Get the current cursor position.

### `computer_type_text`
Type text into the currently focused window.

### `computer_press_key`
Press a keyboard key (enter, esc, tab, ...).

### `computer_hotkey`
Press a hotkey combination (e.g. ctrl+shift+esc).

### `computer_clipboard_read`
Read the clipboard text content.

### `computer_clipboard_write`
Write text to the clipboard.

### `computer_list_windows`
List open windows with title, geometry, and state.

### `computer_focus_window`
Bring a window to the foreground by title substring.

### `computer_get_window_info`
Get detailed information about a window.

### `computer_resize_window`
Resize a window by title substring.

### `computer_move_window`
Move a window to a new position.

### `computer_minimize_window`
Minimize a window by title substring.

### `computer_maximize_window`
Maximize a window by title substring.

### `computer_wait`
Wait 0-60 seconds between UI actions.

### `computer_config_get`
Get safety configuration and dependency availability.

### `computer_config_set`
Update pause interval, failsafe flag, and screenshot directory.

---

For detailed usage, see the main README or category-specific documentation in the docs folder.
