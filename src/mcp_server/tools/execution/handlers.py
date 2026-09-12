"""
Command execution tool handlers.

Wires the hardened `command_executor` infrastructure into MCP tools with a
persistent, user-managed allowlist:

- The allowlist starts EMPTY — `run_command` refuses everything until commands
  are explicitly trusted via `add_allowed_commands`.
- Arguments are sanitized (null bytes stripped) and validated (shell
  metacharacters, dangerous patterns, path traversal, argument size/count).
- Commands run with shell=False, capped timeouts and size-limited output.
- The allowlist persists in ``~/.oh-my-mcp/execution_config.json``.
"""

import json
import sys
from pathlib import Path

from mcp_server.command_executor import CommandExecutor, CommandValidator
from mcp_server.tools.registry import tool_handler
from mcp_server.utils import (
    COMMAND_TIMEOUT_DEFAULT,
    COMMAND_TIMEOUT_MAX,
    CommandExecutionError,
    CommandTimeoutError,
    CommandValidationError,
    SecurityError,
    ValidationError,
    error_json,
    logger,
    sanitize_path,
)

_CONFIG_PATH = Path.home() / ".oh-my-mcp" / "execution_config.json"
_MAX_ALLOWLIST_SIZE = 100

# Shared executor instance; CommandValidator.ALLOWED_COMMANDS is a class-level
# set shared by every executor.
_executor = CommandExecutor()


def _load_allowlist() -> set[str]:
    try:
        if _CONFIG_PATH.exists():
            data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            commands = data.get("allowed_commands", [])
            if isinstance(commands, list):
                CommandValidator.ALLOWED_COMMANDS = {str(c) for c in commands}
    except Exception as e:
        logger.warning(f"Could not load execution config: {e}")
    return CommandValidator.ALLOWED_COMMANDS


def _save_allowlist(commands: set[str]) -> None:
    try:
        _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CONFIG_PATH.write_text(
            json.dumps({"allowed_commands": sorted(commands)}, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        logger.warning(f"Could not save execution config: {e}")


def _parse_args(args_json: str) -> list[str]:
    """Parse a JSON array of argument strings."""
    if not args_json or not args_json.strip():
        return []
    try:
        parsed = json.loads(args_json)
    except json.JSONDecodeError as e:
        raise ValidationError(
            f'args must be a JSON array of strings, e.g. ["-la", "/tmp"]: {e}'
        ) from e
    if not isinstance(parsed, list) or not all(isinstance(a, str) for a in parsed):
        raise ValidationError("args must be a JSON array of strings")
    return parsed


@tool_handler
def run_command(
    command: str,
    args: str = "",
    cwd: str = "",
    timeout: int = COMMAND_TIMEOUT_DEFAULT,
    max_output_chars: int = 10000,
) -> str:
    """
    Execute an allowlisted command with sanitized arguments (no shell).

    The command must be in the persistent allowlist (see
    list_allowed_commands / add_allowed_commands). The allowlist starts
    empty, so nothing can run until explicitly trusted.

    Args:
        command: Command executable, e.g. "git", "python", "C:/tools/app.exe"
        args: JSON array of argument strings, e.g. '["status", "--short"]'
        cwd: Working directory (empty = server current directory)
        timeout: Seconds before the command is killed (default 30, max 300)
        max_output_chars: Truncate stdout/stderr to this many characters each
            (default 10000; the tail is kept so error messages survive)

    Returns:
        JSON string with returncode, stdout, stderr, execution_time and
        output_truncated flag
    """
    try:
        if timeout < 1 or timeout > COMMAND_TIMEOUT_MAX:
            raise ValidationError(f"timeout must be between 1 and {COMMAND_TIMEOUT_MAX}")
        if max_output_chars < 100:
            raise ValidationError("max_output_chars must be at least 100")

        arg_list = _parse_args(args)
        result = _executor.execute(
            command=command,
            args=arg_list,
            cwd=cwd or None,
            timeout=timeout,
        )
        truncated = False
        for field in ("stdout", "stderr"):
            value = result[field]
            if len(value) > max_output_chars:
                result[field] = "...(truncated)..." + value[-max_output_chars:]
                truncated = True
        result["output_truncated"] = truncated
        return json.dumps(result, indent=2, ensure_ascii=False)
    except (
        ValidationError,
        CommandValidationError,
        CommandTimeoutError,
        CommandExecutionError,
        SecurityError,
    ) as e:
        logger.warning(f"run_command failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"run_command unexpected error: {e}")
        return error_json(f"Command execution failed: {e}")


@tool_handler
def list_allowed_commands() -> str:
    """
    List the commands that run_command is allowed to execute.

    Returns:
        JSON string with the sorted allowlist and its config file path
    """
    try:
        commands = sorted(_load_allowlist())
        return json.dumps(
            {
                "success": True,
                "allowed_commands": commands,
                "count": len(commands),
                "config_path": str(_CONFIG_PATH),
            },
            indent=2,
        )
    except Exception as e:
        logger.error(f"list_allowed_commands unexpected error: {e}")
        return error_json(f"Failed to list allowed commands: {e}")


@tool_handler
def add_allowed_commands(commands: list[str]) -> str:
    """
    Permanently allow commands for run_command (persisted across restarts).

    Only trust commands you fully control the meaning of: any allowlisted
    command can be executed by the AI with arbitrary (sanitized) arguments.

    Args:
        commands: Command names to allow, e.g. ["git", "python", "npm"]

    Returns:
        JSON string with the updated allowlist
    """
    try:
        if not isinstance(commands, list) or not commands:
            raise ValidationError("commands must be a non-empty list of strings")
        if not all(isinstance(c, str) and c.strip() for c in commands):
            raise ValidationError("commands must be non-empty strings")

        current = _load_allowlist()
        before = len(current)
        for c in commands:
            current.add(c.strip())
        if len(current) > _MAX_ALLOWLIST_SIZE:
            raise ValidationError(f"Allowlist too large (max {_MAX_ALLOWLIST_SIZE} commands)")
        CommandValidator.ALLOWED_COMMANDS = current
        _save_allowlist(current)
        return json.dumps(
            {
                "success": True,
                "added": sorted(set(commands)),
                "allowed_commands": sorted(current),
                "count": len(current),
                "new_count": len(current) - before,
            },
            indent=2,
        )
    except ValidationError as e:
        logger.warning(f"add_allowed_commands rejected: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"add_allowed_commands unexpected error: {e}")
        return error_json(f"Failed to add allowed commands: {e}")


@tool_handler
def remove_allowed_commands(commands: list[str]) -> str:
    """
    Remove commands from the run_command allowlist (persisted).

    Args:
        commands: Command names to revoke, e.g. ["python"]

    Returns:
        JSON string with the updated allowlist
    """
    try:
        if not isinstance(commands, list) or not commands:
            raise ValidationError("commands must be a non-empty list of strings")

        current = _load_allowlist()
        removed = sorted(c for c in commands if c in current)
        current -= set(commands)
        CommandValidator.ALLOWED_COMMANDS = current
        _save_allowlist(current)
        return json.dumps(
            {
                "success": True,
                "removed": removed,
                "allowed_commands": sorted(current),
                "count": len(current),
            },
            indent=2,
        )
    except ValidationError as e:
        logger.warning(f"remove_allowed_commands rejected: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"remove_allowed_commands unexpected error: {e}")
        return error_json(f"Failed to remove allowed commands: {e}")


# Script extension -> interpreter command that must be allowlisted.
# sys.executable is used for Python so the server's own interpreter runs it.
_SCRIPT_INTERPRETERS: dict[str, tuple[str, ...]] = {
    ".py": (sys.executable,),
    ".ps1": ("powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"),
    ".sh": ("bash",),
    ".bat": ("cmd", "/c"),
    ".cmd": ("cmd", "/c"),
}


@tool_handler
def run_script(
    script_path: str,
    args: str = "",
    cwd: str = "",
    timeout: int = COMMAND_TIMEOUT_DEFAULT,
    max_output_chars: int = 10000,
) -> str:
    """
    Execute a script file (.py/.ps1/.sh/.bat/.cmd) with sanitized arguments.

    The interpreter that runs the script (python, powershell, bash, cmd) must
    be in the allowlist first — e.g. add_allowed_commands(["python"]) for
    .py scripts. Running a script is arbitrary code execution, so only point
    this at scripts you trust.

    Args:
        script_path: Path to the script file
        args: JSON array of argument strings passed to the script
        cwd: Working directory (empty = server current directory)
        timeout: Seconds before the script is killed (default 30, max 300)
        max_output_chars: Truncate stdout/stderr to this many characters each

    Returns:
        JSON string with returncode, stdout, stderr, execution_time
    """
    try:
        if timeout < 1 or timeout > COMMAND_TIMEOUT_MAX:
            raise ValidationError(f"timeout must be between 1 and {COMMAND_TIMEOUT_MAX}")

        script = sanitize_path(script_path)
        if not script.exists():
            raise ValidationError(f"Script not found: {script_path}")
        if not script.is_file():
            raise ValidationError(f"Not a file: {script_path}")

        ext = script.suffix.lower()
        interpreter = _SCRIPT_INTERPRETERS.get(ext)
        if interpreter is None:
            raise ValidationError(
                f"Unsupported script type: {ext}. "
                f"Supported: {', '.join(sorted(_SCRIPT_INTERPRETERS))}"
            )

        # the interpreter must be explicitly trusted, same as run_command
        if interpreter[0] not in _load_allowlist():
            raise ValidationError(
                f"Interpreter '{interpreter[0]}' is not allowlisted. "
                f'Run add_allowed_commands(["{interpreter[0]}"]) first.'
            )

        arg_list = _parse_args(args)
        result = _executor.execute(
            command=interpreter[0],
            args=[*interpreter[1:], str(script), *arg_list],
            cwd=cwd or None,
            timeout=timeout,
        )
        truncated = False
        for field in ("stdout", "stderr"):
            value = result[field]
            if len(value) > max_output_chars:
                result[field] = "...(truncated)..." + value[-max_output_chars:]
                truncated = True
        result["output_truncated"] = truncated
        result["script"] = str(script)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except (
        ValidationError,
        CommandValidationError,
        CommandTimeoutError,
        CommandExecutionError,
        SecurityError,
    ) as e:
        logger.warning(f"run_script failed: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"run_script unexpected error: {e}")
        return error_json(f"Script execution failed: {e}")
