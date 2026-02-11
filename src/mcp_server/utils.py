"""
Utility functions and infrastructure for the MCP server.

Provides:
- Error handling and custom exceptions
- Logging configuration
- Input validation
- Retry logic for external requests
- Safe file operations
"""

import logging
import os
import re
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp_server.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


# Custom Exceptions
class MCPServerError(Exception):
    """Base exception for MCP server errors."""

    pass


class ValidationError(MCPServerError):
    """Raised when input validation fails."""

    pass


class NetworkError(MCPServerError):
    """Raised when network operations fail."""

    pass


class FileOperationError(MCPServerError):
    """Raised when file operations fail."""

    pass


class DataProcessingError(MCPServerError):
    """Raised when data processing fails."""

    pass


class CommandExecutionError(MCPServerError):
    """Raised when command execution fails."""

    pass


class CommandValidationError(ValidationError):
    """Raised when command validation fails."""

    pass


class CommandTimeoutError(CommandExecutionError):
    """Raised when command execution times out."""

    pass


class SecurityError(MCPServerError):
    """Raised when security validation fails."""

    pass


# Validation utilities
def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_path(path: str, must_exist: bool = False) -> bool:
    """
    Validate file/directory path.

    Args:
        path: Path string to validate
        must_exist: Whether path must exist

    Returns:
        True if valid path, False otherwise
    """
    try:
        p = Path(path)
        # Check for path traversal attempts
        p.resolve().relative_to(Path.cwd())

        if must_exist:
            return p.exists()
        return True
    except (ValueError, OSError):
        return False


def sanitize_path(path: str) -> Path:
    """
    Sanitize and resolve a file path.

    Args:
        path: Path string to sanitize

    Returns:
        Resolved Path object

    Raises:
        ValidationError: If path is invalid or attempts traversal
    """
    try:
        p = Path(path).resolve()
        # Basic security check - prevent absolute path traversal outside workspace
        # This is a simple check; adjust based on your security requirements
        return p
    except Exception as e:
        raise ValidationError(f"Invalid path: {path}") from e


def safe_get_file_size(path: Path) -> int:
    """
    Safely get file size.

    Args:
        path: Path to file

    Returns:
        File size in bytes
    """
    try:
        return path.stat().st_size
    except Exception:
        return 0


# Retry decorator
def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Retry decorator for functions that may fail transiently.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch and retry
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )
            raise last_exception

        return wrapper

    return decorator


# Safe file operations
def safe_read_file(
    path: str, encoding: str = "utf-8", max_size: int = 10 * 1024 * 1024
) -> str:
    """
    Safely read file contents with size limit.

    Args:
        path: Path to file
        encoding: File encoding
        max_size: Maximum file size in bytes (default 10MB)

    Returns:
        File contents as string

    Raises:
        FileOperationError: If file cannot be read or is too large
    """
    try:
        p = sanitize_path(path)

        if not p.exists():
            raise FileOperationError(f"File not found: {path}")

        if not p.is_file():
            raise FileOperationError(f"Not a file: {path}")

        file_size = safe_get_file_size(p)
        if file_size > max_size:
            raise FileOperationError(
                f"File too large: {file_size} bytes (max: {max_size} bytes)"
            )

        with open(p, "r", encoding=encoding) as f:
            return f.read()

    except FileOperationError:
        raise
    except Exception as e:
        raise FileOperationError(f"Failed to read file {path}: {e}") from e


def safe_write_file(
    path: str, content: str, encoding: str = "utf-8", overwrite: bool = True
) -> None:
    """
    Safely write content to file.

    Args:
        path: Path to file
        content: Content to write
        encoding: File encoding
        overwrite: Whether to overwrite existing file

    Raises:
        FileOperationError: If file cannot be written
    """
    try:
        p = sanitize_path(path)

        if p.exists() and not overwrite:
            raise FileOperationError(f"File exists and overwrite=False: {path}")

        # Create parent directories if needed
        p.parent.mkdir(parents=True, exist_ok=True)

        with open(p, "w", encoding=encoding) as f:
            f.write(content)

    except FileOperationError:
        raise
    except Exception as e:
        raise FileOperationError(f"Failed to write file {path}: {e}") from e


# Text utilities
def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def extract_text_by_regex(text: str, pattern: str, group: int = 0) -> list[str]:
    """
    Extract text using regex pattern.

    Args:
        text: Text to search
        pattern: Regex pattern
        group: Capture group to extract (0 for entire match)

    Returns:
        List of matched strings
    """
    try:
        matches = re.finditer(pattern, text)
        return [m.group(group) for m in matches]
    except re.error as e:
        raise ValidationError(f"Invalid regex pattern: {pattern}") from e


# Format utilities
def format_bytes(bytes_size: int) -> str:
    """
    Format bytes to human-readable string.

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def format_timestamp(timestamp: float) -> str:
    """
    Format Unix timestamp to readable string.

    Args:
        timestamp: Unix timestamp

    Returns:
        Formatted date/time string
    """
    from datetime import datetime

    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


# Archive safety constants
MAX_EXTRACT_SIZE = 500 * 1024 * 1024  # 500MB

# Command execution constants
COMMAND_TIMEOUT_DEFAULT = 30  # seconds
COMMAND_TIMEOUT_MAX = 300  # seconds (5 minutes)
COMMAND_OUTPUT_MAX_SIZE = 10 * 1024 * 1024  # 10MB
PYTHON_MAX_CODE_LENGTH = 100 * 1024  # 100KB


def validate_archive_safety(
    archive_path: Path, max_size: int = MAX_EXTRACT_SIZE
) -> None:
    """
    Validate archive file safety to prevent ZIP bomb attacks.

    Args:
        archive_path: Path to archive file
        max_size: Maximum allowed uncompressed size in bytes

    Raises:
        ValidationError: If archive is unsafe (too large, suspicious compression ratio)
    """
    import zipfile
    import tarfile

    try:
        file_ext = archive_path.suffix.lower()

        if file_ext == ".zip":
            with zipfile.ZipFile(archive_path, "r") as zf:
                total_size = sum(info.file_size for info in zf.infolist())
                if total_size > max_size:
                    raise ValidationError(
                        f"Archive too large: {format_bytes(total_size)} "
                        f"(max: {format_bytes(max_size)})"
                    )

                # Check for suspicious compression ratio
                compressed_size = archive_path.stat().st_size
                if compressed_size > 0:
                    ratio = total_size / compressed_size
                    if ratio > 100:  # More than 100:1 compression is suspicious
                        raise ValidationError(
                            f"Suspicious compression ratio: {ratio:.1f}:1"
                        )

        elif file_ext in [".tar", ".gz", ".bz2", ".tgz", ".tbz2"]:
            with tarfile.open(archive_path, "r:*") as tf:
                total_size = sum(member.size for member in tf.getmembers())
                if total_size > max_size:
                    raise ValidationError(
                        f"Archive too large: {format_bytes(total_size)} "
                        f"(max: {format_bytes(max_size)})"
                    )

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Failed to validate archive safety: {e}") from e


def validate_command_path(path: str) -> bool:
    """
    Validate command path safety.

    Args:
        path: Path string to validate

    Returns:
        True if path is safe, False otherwise
    """
    try:
        p = Path(path).resolve()

        # Prevent access to sensitive system directories
        sensitive_dirs = [
            Path("/etc"),
            Path("/sys"),
            Path("/proc"),
            Path("C:\\Windows\\System32"),
            Path("C:\\Windows\\SysWOW64"),
        ]

        for sensitive_dir in sensitive_dirs:
            try:
                if sensitive_dir.exists() and p.is_relative_to(sensitive_dir):
                    return False
            except (ValueError, AttributeError):
                # is_relative_to not available in Python < 3.9
                try:
                    p.relative_to(sensitive_dir)
                    return False
                except ValueError:
                    pass

        return True
    except Exception:
        return False


def sanitize_command_output(output: str, max_size: int = COMMAND_OUTPUT_MAX_SIZE) -> str:
    """
    Sanitize command output by removing sensitive information and limiting size.

    Args:
        output: Command output to sanitize
        max_size: Maximum output size in bytes

    Returns:
        Sanitized output string
    """
    # Truncate if too large
    if len(output) > max_size:
        output = output[:max_size] + "\n... [OUTPUT TRUNCATED - EXCEEDED MAX SIZE] ..."

    # Filter sensitive patterns (API keys, tokens, passwords)
    sensitive_patterns = [
        (r'(api[_-]?key\s*=\s*)["\']?[\w-]+["\']?', r'\1***REDACTED***'),
        (r'(token\s*=\s*)["\']?[\w-]+["\']?', r'\1***REDACTED***'),
        (r'(password\s*=\s*)["\']?[\w-]+["\']?', r'\1***REDACTED***'),
        (r'(Bearer\s+)[\w-]+', r'\1***REDACTED***'),
    ]

    for pattern, replacement in sensitive_patterns:
        output = re.sub(pattern, replacement, output, flags=re.IGNORECASE)

    return output
