"""
Command execution infrastructure for MCP server.

Provides secure command execution with:
- Command whitelist validation
- Argument sanitization
- Timeout protection
- Output size limits
- Working directory isolation
- Audit logging
"""

import re
import subprocess
from pathlib import Path
from typing import Any, Optional

from .utils import (
    CommandExecutionError,
    CommandTimeoutError,
    CommandValidationError,
    SecurityError,
    COMMAND_TIMEOUT_DEFAULT,
    COMMAND_TIMEOUT_MAX,
    logger,
    sanitize_command_output,
    validate_command_path,
)


class CommandValidator:
    """Validates commands and arguments for safe execution."""

    # Whitelist of allowed commands
    ALLOWED_COMMANDS = set()

    # Dangerous characters that could enable shell injection
    DANGEROUS_CHARS = {";", "|", "&", "$", "`", "\n", "\r"}

    # Dangerous command patterns
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf",
        r"eval\s*\(",
        r"exec\s*\(",
        r"__import__",
        r"subprocess",
        r"os\.system",
    ]

    # Maximum argument length
    MAX_ARG_LENGTH = 4096  # 4KB per argument
    MAX_ARGS_COUNT = 50

    @classmethod
    def validate_command(cls, command: str, args: list[str]) -> tuple[bool, str]:
        """
        Validate command and arguments.

        Args:
            command: Command to execute
            args: List of command arguments

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Extract base command name from full path if necessary
        import os

        command_name = os.path.basename(command)

        # Remove .exe extension on Windows for comparison
        if command_name.lower().endswith(".exe"):
            command_name = command_name[:-4]

        # Check if base command is in whitelist
        # Also check the original command in case it's just the command name
        if command not in cls.ALLOWED_COMMANDS and command_name not in cls.ALLOWED_COMMANDS:
            return False, f"Command not allowed: {command}"

        # Check argument count
        if len(args) > cls.MAX_ARGS_COUNT:
            return False, f"Too many arguments: {len(args)} (max: {cls.MAX_ARGS_COUNT})"

        # Validate each argument
        for i, arg in enumerate(args):
            # Check argument length
            if len(arg) > cls.MAX_ARG_LENGTH:
                return False, f"Argument {i} too long: {len(arg)} bytes (max: {cls.MAX_ARG_LENGTH})"

            # Check for dangerous characters
            for char in cls.DANGEROUS_CHARS:
                if char in arg:
                    return False, f"Dangerous character in argument {i}: {repr(char)}"

            # Check for dangerous patterns
            for pattern in cls.DANGEROUS_PATTERNS:
                if re.search(pattern, arg, re.IGNORECASE):
                    return False, f"Dangerous pattern in argument {i}: {pattern}"

            # Check for path traversal
            if ".." in arg and ("/" in arg or "\\" in arg):
                return False, f"Potential path traversal in argument {i}"

        return True, ""

    @classmethod
    def sanitize_args(cls, args: list[str]) -> list[str]:
        """
        Sanitize command arguments.

        Args:
            args: List of arguments to sanitize

        Returns:
            List of sanitized arguments
        """
        sanitized = []
        for arg in args:
            # Strip whitespace
            arg = arg.strip()
            # Remove null bytes
            arg = arg.replace("\x00", "")
            sanitized.append(arg)
        return sanitized


class CommandExecutor:
    """Executes commands securely with validation and resource limits."""

    def __init__(self) -> None:
        """Initialize the command executor."""
        self.validator = CommandValidator()

    def _check_command_exists(self, command: str) -> bool:
        """
        Check if command exists in system PATH.

        Args:
            command: Command name to check

        Returns:
            True if command exists, False otherwise
        """
        import shutil

        return shutil.which(command) is not None

    def _validate_working_directory(self, cwd: Optional[str]) -> Path:
        """
        Validate and resolve working directory.

        Args:
            cwd: Working directory path (None for current directory)

        Returns:
            Resolved Path object

        Raises:
            CommandValidationError: If directory is invalid or unsafe
        """
        if cwd is None:
            return Path.cwd()

        try:
            path = Path(cwd).resolve()

            if not path.exists():
                raise CommandValidationError(f"Working directory does not exist: {cwd}")

            if not path.is_dir():
                raise CommandValidationError(f"Not a directory: {cwd}")

            if not validate_command_path(str(path)):
                raise SecurityError(f"Unsafe working directory: {cwd}")

            return path

        except (CommandValidationError, SecurityError):
            raise
        except Exception as e:
            raise CommandValidationError(f"Invalid working directory: {cwd}") from e

    def execute(
        self,
        command: str,
        args: list[str],
        cwd: Optional[str] = None,
        timeout: int = COMMAND_TIMEOUT_DEFAULT,
    ) -> dict[str, Any]:
        """
        Execute a command securely.

        Args:
            command: Command to execute (must be in whitelist)
            args: List of command arguments
            cwd: Working directory (None for current directory)
            timeout: Timeout in seconds (max: COMMAND_TIMEOUT_MAX)

        Returns:
            Dictionary with:
                - success: bool
                - returncode: int
                - stdout: str
                - stderr: str
                - execution_time: float
                - command: str (for audit)

        Raises:
            CommandValidationError: If command or arguments are invalid
            CommandTimeoutError: If command execution times out
            CommandExecutionError: If command execution fails
        """
        import time

        start_time = time.time()

        try:
            # Validate timeout
            if timeout <= 0 or timeout > COMMAND_TIMEOUT_MAX:
                raise CommandValidationError(
                    f"Invalid timeout: {timeout} (must be 1-{COMMAND_TIMEOUT_MAX})"
                )

            # Sanitize arguments
            args = self.validator.sanitize_args(args)

            # Validate command and arguments
            is_valid, error_msg = self.validator.validate_command(command, args)
            if not is_valid:
                raise CommandValidationError(error_msg)

            # Check if command exists
            if not self._check_command_exists(command):
                raise CommandExecutionError(
                    f"Command not found: {command}. Please ensure it is installed and in PATH."
                )

            # Validate working directory
            working_dir = self._validate_working_directory(cwd)

            # Build full command
            full_command = [command] + args

            # Log command execution (audit)
            logger.info(f"Executing command: {command} with {len(args)} args in {working_dir}")
            logger.debug(f"Full command: {' '.join(full_command)}")

            # Execute command with subprocess (shell=False for security)
            result = subprocess.run(
                full_command,
                cwd=str(working_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,  # CRITICAL: Never use shell=True
                stdin=subprocess.DEVNULL,  # Close stdin to prevent hanging
            )

            execution_time = time.time() - start_time

            # Sanitize output
            stdout = sanitize_command_output(result.stdout)
            stderr = sanitize_command_output(result.stderr)

            # Log result
            if result.returncode == 0:
                logger.info(f"Command completed successfully in {execution_time:.2f}s")
            else:
                logger.warning(
                    f"Command failed with code {result.returncode} in {execution_time:.2f}s"
                )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time,
                "command": command,
            }

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            logger.error(f"Command timed out after {timeout}s")
            raise CommandTimeoutError(f"Command timed out after {timeout} seconds") from e

        except (CommandValidationError, CommandExecutionError, SecurityError):
            raise

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Command execution failed: {e}")
            raise CommandExecutionError(f"Command execution failed: {e}") from e
