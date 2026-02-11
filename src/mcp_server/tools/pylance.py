"""
Pylance/Pyright Tools

Provides tools for Python type checking, code analysis, and diagnostics using Pyright.
"""

import json
from pathlib import Path

from ..command_executor import CommandExecutor
from ..utils import (
    CommandExecutionError,
    ValidationError,
    logger,
    sanitize_path,
)

# Module metadata
CATEGORY_NAME = "Pylance/Pyright"
CATEGORY_DESCRIPTION = "Python type checking, code analysis, and diagnostics"
TOOLS = [
    "pylance_check_file",
    "pylance_check_project",
    "pylance_get_diagnostics",
    "pylance_get_version",
]


def register_tools(mcp):
    """Register all Pylance/Pyright tools."""

    executor = CommandExecutor()

    @mcp.tool()
    def pylance_check_file(file_path: str, output_json: bool = True) -> str:
        """Check a single Python file for type errors using Pyright.

        Args:
            file_path: Path to the Python file to check
            output_json: Output results as JSON (default: True)

        Returns:
            JSON string with type checking results
        """
        try:
            # Validate file path
            path = sanitize_path(file_path)
            if not path.exists():
                return json.dumps({"error": f"File not found: {file_path}"})

            if not path.is_file():
                return json.dumps({"error": f"Not a file: {file_path}"})

            # Build command arguments
            args = [str(path)]
            if output_json:
                args.append("--outputjson")

            # Execute pyright command
            result = executor.execute("pyright", args, timeout=60)

            # Parse output
            if output_json and result["stdout"]:
                try:
                    diagnostics = json.loads(result["stdout"])
                    return json.dumps({
                        "success": result["success"],
                        "file": str(path),
                        "diagnostics": diagnostics,
                    })
                except json.JSONDecodeError:
                    pass

            return json.dumps({
                "success": result["success"],
                "file": str(path),
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"pylance_check_file failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def pylance_check_project(project_path: str = ".", config_file: str = "") -> str:
        """Check an entire Python project for type errors using Pyright.

        Args:
            project_path: Path to the project directory (default: current directory)
            config_file: Path to pyrightconfig.json (optional)

        Returns:
            JSON string with project-level type checking results
        """
        try:
            # Validate project path
            path = sanitize_path(project_path)
            if not path.exists():
                return json.dumps({"error": f"Project path not found: {project_path}"})

            if not path.is_dir():
                return json.dumps({"error": f"Not a directory: {project_path}"})

            # Build command arguments
            args = ["--outputjson"]

            if config_file:
                config_path = sanitize_path(config_file)
                if config_path.exists():
                    args.extend(["--project", str(config_path)])

            # Execute pyright command
            result = executor.execute("pyright", args, cwd=str(path), timeout=120)

            # Parse output
            if result["stdout"]:
                try:
                    diagnostics = json.loads(result["stdout"])
                    return json.dumps({
                        "success": result["success"],
                        "project_path": str(path),
                        "diagnostics": diagnostics,
                    })
                except json.JSONDecodeError:
                    pass

            return json.dumps({
                "success": result["success"],
                "project_path": str(path),
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"pylance_check_project failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def pylance_get_diagnostics(file_path: str, verbose: bool = False) -> str:
        """Get detailed diagnostics for a Python file using Pyright.

        Args:
            file_path: Path to the Python file
            verbose: Include verbose diagnostics (default: False)

        Returns:
            JSON string with detailed diagnostics and statistics
        """
        try:
            # Validate file path
            path = sanitize_path(file_path)
            if not path.exists():
                return json.dumps({"error": f"File not found: {file_path}"})

            # Build command arguments
            args = [str(path), "--outputjson"]
            if verbose:
                args.append("--verbose")

            # Execute pyright command
            result = executor.execute("pyright", args, timeout=60)

            # Parse output
            if result["stdout"]:
                try:
                    diagnostics = json.loads(result["stdout"])
                    return json.dumps({
                        "success": result["success"],
                        "file": str(path),
                        "diagnostics": diagnostics,
                        "verbose": verbose,
                    })
                except json.JSONDecodeError:
                    pass

            return json.dumps({
                "success": result["success"],
                "file": str(path),
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"pylance_get_diagnostics failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def pylance_get_version() -> str:
        """Get Pyright version information.

        Returns:
            JSON string with Pyright version
        """
        try:
            result = executor.execute("pyright", ["--version"], timeout=10)

            return json.dumps({
                "success": result["success"],
                "version": result["stdout"].strip(),
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"pylance_get_version failed: {e}")
            return json.dumps({"error": str(e)})
