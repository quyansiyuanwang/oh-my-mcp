"""
File system tool handlers.

Provides tools for:
- Reading and writing files
- Directory operations
- File searching
- File metadata retrieval
- File comparison and diff
"""

import difflib
import glob
import json
import re
import shutil
from pathlib import Path
from typing import Any

from mcp_server.tools.registry import tool_handler
from mcp_server.utils import (
    FileOperationError,
    ValidationError,
    error_json,
    format_bytes,
    format_timestamp,
    logger,
    safe_get_file_size,
    safe_read_file,
    safe_write_file,
    sanitize_path,
)


@tool_handler
def read_file(path: str, encoding: str = "utf-8") -> str:
    """
    Read the contents of a file.

    Args:
        path: Path to the file to read
        encoding: File encoding (default: utf-8)

    Returns:
        File contents as string
    """
    try:
        return safe_read_file(path, encoding=encoding)
    except FileOperationError as e:
        logger.error(f"Failed to read file: {e}")
        return f"Error: {str(e)}"


@tool_handler
def write_file(path: str, content: str, encoding: str = "utf-8", overwrite: bool = True) -> str:
    """
    Write content to a file.

    Args:
        path: Path to the file to write
        content: Content to write to the file
        encoding: File encoding (default: utf-8)
        overwrite: Whether to overwrite if file exists (default: True)

    Returns:
        Success message with file path
    """
    try:
        safe_write_file(path, content, encoding=encoding, overwrite=overwrite)
        p = sanitize_path(path)
        file_size = safe_get_file_size(p)
        return f"File written successfully to {path} ({format_bytes(file_size)})"
    except FileOperationError as e:
        logger.error(f"Failed to write file: {e}")
        return f"Error: {str(e)}"


@tool_handler
def append_file(path: str, content: str, encoding: str = "utf-8") -> str:
    """
    Append content to a file.

    Args:
        path: Path to the file
        content: Content to append
        encoding: File encoding (default: utf-8)

    Returns:
        Success message with file path
    """
    try:
        p = sanitize_path(path)

        # Create parent directories if needed
        p.parent.mkdir(parents=True, exist_ok=True)

        # newline="" appends content verbatim (no newline translation)
        with open(p, "a", encoding=encoding, newline="") as f:
            f.write(content)

        file_size = safe_get_file_size(p)
        return f"Content appended to {path} ({format_bytes(file_size)})"

    except Exception as e:
        logger.error(f"Failed to append to file: {e}")
        return f"Error: {str(e)}"


@tool_handler
def list_directory(path: str = ".", pattern: str = "*", recursive: bool = False) -> str:
    """
    List contents of a directory.

    Args:
        path: Directory path (default: current directory)
        pattern: Glob pattern to filter files (default: * for all files)
        recursive: Search recursively in subdirectories (default: False)

    Returns:
        JSON string containing list of files and directories
    """
    try:
        p = sanitize_path(path)

        if not p.exists():
            return error_json(f"Directory not found: {path}")

        if not p.is_dir():
            return error_json(f"Not a directory: {path}")

        items = []

        if recursive:
            search_pattern = str(p / "**" / pattern)
            paths = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = str(p / pattern)
            paths = glob.glob(search_pattern)

        for item_path in sorted(paths):
            item = Path(item_path)
            try:
                is_file = item.is_file()
                is_dir = item.is_dir()

                item_info: dict[str, Any] = {
                    "name": item.name,
                    "path": str(item),
                    "type": ("file" if is_file else "directory" if is_dir else "other"),
                }

                if is_file:
                    item_info["size"] = format_bytes(safe_get_file_size(item))
                    item_info["size_bytes"] = safe_get_file_size(item)
                    item_info["modified"] = format_timestamp(item.stat().st_mtime)

                items.append(item_info)
            except Exception as e:
                logger.warning(f"Could not get info for {item_path}: {e}")
                continue

        return json.dumps(
            {
                "directory": str(p),
                "pattern": pattern,
                "recursive": recursive,
                "count": len(items),
                "items": items,
            },
            indent=2,
        )

    except Exception as e:
        logger.error(f"Failed to list directory: {e}")
        return error_json(f"Failed to list directory: {str(e)}")


@tool_handler
def file_exists(path: str) -> str:
    """
    Check if a file or directory exists.

    Args:
        path: Path to check

    Returns:
        JSON string with existence status and type
    """
    try:
        p = sanitize_path(path)
        exists = p.exists()

        result = {"path": path, "exists": exists}

        if exists:
            result["type"] = "file" if p.is_file() else "directory" if p.is_dir() else "other"

        return json.dumps(result, indent=2)

    except Exception as e:
        return error_json(f"Failed to check path: {str(e)}")


@tool_handler
def get_file_info(path: str) -> str:
    """
    Get detailed information about a file or directory.

    Args:
        path: Path to file or directory

    Returns:
        JSON string containing file metadata
    """
    try:
        p = sanitize_path(path)

        if not p.exists():
            return error_json(f"Path not found: {path}")

        stat = p.stat()

        info = {
            "path": str(p),
            "name": p.name,
            "absolute_path": str(p.resolve()),
            "type": ("file" if p.is_file() else "directory" if p.is_dir() else "other"),
            "size_bytes": stat.st_size,
            "size": format_bytes(stat.st_size),
            "created": format_timestamp(stat.st_ctime),
            "modified": format_timestamp(stat.st_mtime),
            "accessed": format_timestamp(stat.st_atime),
        }

        if p.is_file():
            info["extension"] = p.suffix
            info["stem"] = p.stem

        return json.dumps(info, indent=2)

    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        return error_json(f"Failed to get file info: {str(e)}")


@tool_handler
def search_files(directory: str = ".", pattern: str = "*", name_contains: str = "") -> str:
    """
    Search for files in a directory.

    Args:
        directory: Directory to search in (default: current directory)
        pattern: Glob pattern (default: *)
        name_contains: Optional string that filename must contain

    Returns:
        JSON string containing list of matching files
    """
    try:
        p = sanitize_path(directory)

        if not p.exists():
            return error_json(f"Directory not found: {directory}")

        if not p.is_dir():
            return error_json(f"Not a directory: {directory}")

        # Search recursively
        search_pattern = str(p / "**" / pattern)
        paths = glob.glob(search_pattern, recursive=True)

        matches = []
        for item_path in sorted(paths):
            item = Path(item_path)

            # Skip directories
            if not item.is_file():
                continue

            # Check name contains filter
            if name_contains and name_contains.lower() not in item.name.lower():
                continue

            try:
                matches.append(
                    {
                        "name": item.name,
                        "path": str(item),
                        "size": format_bytes(safe_get_file_size(item)),
                        "modified": format_timestamp(item.stat().st_mtime),
                    }
                )
            except Exception as e:
                logger.warning(f"Could not get info for {item_path}: {e}")
                continue

        return json.dumps(
            {
                "directory": str(p),
                "pattern": pattern,
                "name_contains": name_contains,
                "count": len(matches),
                "matches": matches,
            },
            indent=2,
        )

    except Exception as e:
        logger.error(f"Failed to search files: {e}")
        return error_json(f"Failed to search files: {str(e)}")


@tool_handler
def create_directory(path: str, parents: bool = True) -> str:
    """
    Create a directory.

    Args:
        path: Path to the directory to create
        parents: Create parent directories if needed (default: True)

    Returns:
        Success message with directory path
    """
    try:
        p = sanitize_path(path)

        if p.exists():
            if p.is_dir():
                return f"Directory already exists: {path}"
            return f"Error: Path exists but is not a directory: {path}"

        p.mkdir(parents=parents, exist_ok=True)
        return f"Directory created successfully: {path}"

    except Exception as e:
        logger.error(f"Failed to create directory: {e}")
        return f"Error: {str(e)}"


@tool_handler
def delete_file(path: str, confirm: bool = False) -> str:
    """
    Delete a file (requires confirmation).

    Args:
        path: Path to the file to delete
        confirm: Must be True to actually delete (safety feature)

    Returns:
        Success or error message
    """
    if not confirm:
        return "Error: Must set confirm=True to delete file (safety feature)"

    try:
        p = sanitize_path(path)

        if not p.exists():
            return f"Error: File not found: {path}"

        if p.is_dir():
            return f"Error: Path is a directory, not a file: {path}"

        p.unlink()
        return f"File deleted successfully: {path}"

    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        return f"Error: {str(e)}"


@tool_handler
def copy_file(source: str, destination: str, overwrite: bool = False) -> str:
    """
    Copy a file from source to destination.

    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite if destination exists (default: False)

    Returns:
        Success message with destination path
    """
    try:
        src = sanitize_path(source)
        dst = sanitize_path(destination)

        if not src.exists():
            return f"Error: Source file not found: {source}"

        if not src.is_file():
            return f"Error: Source is not a file: {source}"

        if dst.exists() and dst.is_dir():
            return f"Error: Destination is an existing directory: {destination}"

        if dst.exists() and not overwrite:
            return f"Error: Destination exists and overwrite=False: {destination}"

        # Create parent directories if needed
        dst.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src, dst)

        file_size = safe_get_file_size(dst)
        return f"File copied successfully to {destination} ({format_bytes(file_size)})"

    except Exception as e:
        logger.error(f"Failed to copy file: {e}")
        return f"Error: {str(e)}"


@tool_handler
def diff_files(
    file1: str,
    file2: str,
    context_lines: int = 3,
    format: str = "unified",
) -> str:
    """
    Compare two files and show differences.

    Args:
        file1: Path to first file
        file2: Path to second file
        context_lines: Number of context lines (default: 3)
        format: Output format - "unified", "context", or "ndiff" (default: "unified")

    Returns:
        JSON string with diff results and statistics
    """
    try:
        # 验证输入
        if format not in ["unified", "context", "ndiff"]:
            raise ValidationError("Format must be 'unified', 'context', or 'ndiff'")

        # 读取文件（带大小限制）
        MAX_DIFF_SIZE = 10 * 1024 * 1024  # 10MB
        content1 = safe_read_file(file1, max_size=MAX_DIFF_SIZE)
        content2 = safe_read_file(file2, max_size=MAX_DIFF_SIZE)

        # 分割为行
        lines1 = content1.splitlines(keepends=True)
        lines2 = content2.splitlines(keepends=True)

        # 生成差异
        if format == "unified":
            diff = list(
                difflib.unified_diff(
                    lines1,
                    lines2,
                    fromfile=file1,
                    tofile=file2,
                    n=context_lines,
                )
            )
        elif format == "context":
            diff = list(
                difflib.context_diff(
                    lines1,
                    lines2,
                    fromfile=file1,
                    tofile=file2,
                    n=context_lines,
                )
            )
        else:  # ndiff
            diff = list(difflib.ndiff(lines1, lines2))

        # 统计差异
        added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

        diff_output = "".join(diff)

        logger.info(f"Compared files: {file1} vs {file2} (+{added}, -{removed})")

        return json.dumps(
            {
                "success": True,
                "file1": file1,
                "file2": file2,
                "format": format,
                "lines_added": added,
                "lines_removed": removed,
                "total_changes": added + removed,
                "diff": diff_output,
            },
            ensure_ascii=False,
        )

    except (ValidationError, FileOperationError) as e:
        logger.error(f"File diff failed: {e}")
        return json.dumps({"error": str(e), "type": "validation"})
    except Exception as e:
        logger.error(f"Unexpected error in diff_files: {e}")
        return json.dumps({"error": str(e), "type": "unknown"})


@tool_handler
def diff_text(text1: str, text2: str, format: str = "unified") -> str:
    """
    Compare two text strings and show differences.

    Args:
        text1: First text string
        text2: Second text string
        format: Output format - "unified", "context", or "ndiff" (default: "unified")

    Returns:
        JSON string with diff results and statistics
    """
    try:
        # 验证输入
        if format not in ["unified", "context", "ndiff"]:
            raise ValidationError("Format must be 'unified', 'context', or 'ndiff'")

        # 分割为行
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)

        # 生成差异
        if format == "unified":
            diff = list(difflib.unified_diff(lines1, lines2, fromfile="text1", tofile="text2", n=3))
        elif format == "context":
            diff = list(difflib.context_diff(lines1, lines2, fromfile="text1", tofile="text2", n=3))
        else:  # ndiff
            diff = list(difflib.ndiff(lines1, lines2))

        # 统计差异
        added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
        removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

        diff_output = "".join(diff)

        logger.info(f"Compared text strings (+{added}, -{removed})")

        return json.dumps(
            {
                "success": True,
                "format": format,
                "lines_added": added,
                "lines_removed": removed,
                "total_changes": added + removed,
                "diff": diff_output,
            },
            ensure_ascii=False,
        )

    except ValidationError as e:
        logger.error(f"Text diff failed: {e}")
        return json.dumps({"error": str(e), "type": "validation"})
    except Exception as e:
        logger.error(f"Unexpected error in diff_text: {e}")
        return json.dumps({"error": str(e), "type": "unknown"})


# Binary extensions skipped by grep_files
_BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".webp",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".class",
    ".jar",
    ".pyc",
    ".woff",
    ".woff2",
    ".ttf",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".sqlite",
    ".db",
}

_MAX_GREP_FILE_SIZE = 2 * 1024 * 1024  # 2MB per file


@tool_handler
def grep_files(
    directory: str = ".",
    pattern: str = "*",
    text: str = "",
    regex: str = "",
    ignore_case: bool = True,
    max_results: int = 100,
) -> str:
    """
    Search file contents in a directory tree for a text string or regex.

    Skips binary files (by extension and NUL-byte sniffing) and files larger
    than 2MB. Provide either `text` (plain substring search) or `regex`
    (Python regular expression); if both are given, `regex` wins.

    Args:
        directory: Directory to search in (searched recursively)
        pattern: Glob pattern to filter files (default: all files)
        text: Plain text to search for
        regex: Regular expression to search for
        ignore_case: Case-insensitive matching (default True)
        max_results: Maximum number of matching lines returned (default 100)

    Returns:
        JSON string with matched lines (file, line number, content) and totals
    """
    try:
        if not text and not regex:
            raise ValidationError("Provide either 'text' or 'regex' to search for")

        base = sanitize_path(directory)
        if not base.exists():
            return json.dumps({"error": f"Directory not found: {directory}"})
        if not base.is_dir():
            return json.dumps({"error": f"Not a directory: {directory}"})

        if max_results < 1 or max_results > 1000:
            raise ValidationError("max_results must be between 1 and 1000")

        flags = re.IGNORECASE if ignore_case else 0
        if regex:
            try:
                matcher = re.compile(regex, flags)
            except re.error as e:
                raise ValidationError(f"Invalid regex: {e}") from e
        else:
            matcher = re.compile(re.escape(text), flags)

        matches: list[dict[str, Any]] = []
        total_matches = 0
        files_searched = 0
        truncated = False

        for item_path in sorted(glob.glob(str(base / "**" / pattern), recursive=True)):
            item = Path(item_path)
            if not item.is_file() or item.suffix.lower() in _BINARY_EXTENSIONS:
                continue
            try:
                if item.stat().st_size > _MAX_GREP_FILE_SIZE:
                    continue
                content = item.read_text(encoding="utf-8", errors="strict")
            except UnicodeDecodeError:
                continue  # binary content
            except OSError as e:
                logger.warning(f"Could not read {item_path}: {e}")
                continue

            if "\x00" in content:
                continue  # NUL byte sniffing: binary content despite extension

            files_searched += 1
            for line_number, line in enumerate(content.splitlines(), start=1):
                if matcher.search(line):
                    total_matches += 1
                    if total_matches <= max_results:
                        matches.append(
                            {
                                "file": str(item),
                                "line_number": line_number,
                                "line": line[:500],
                            }
                        )

        truncated = total_matches > max_results

        return json.dumps(
            {
                "success": True,
                "directory": str(base),
                "pattern": pattern,
                "files_searched": files_searched,
                "total_matches": total_matches,
                "truncated": truncated,
                "matches": matches,
            },
            indent=2,
            ensure_ascii=False,
        )

    except ValidationError as e:
        logger.warning(f"grep_files validation error: {e}")
        return json.dumps({"error": str(e), "type": "validation"})
    except Exception as e:
        logger.error(f"Unexpected error in grep_files: {e}")
        return json.dumps({"error": str(e), "type": "unknown"})
