"""
UV Package Manager Tools

Provides tools for fast Python package and project management using uv.
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
CATEGORY_NAME = "UV Package Manager"
CATEGORY_DESCRIPTION = "Fast Python package and project management with uv"
TOOLS = [
    "uv_install_package",
    "uv_uninstall_package",
    "uv_create_venv",
    "uv_list_packages",
    "uv_init_project",
    "uv_sync_dependencies",
    "uv_lock_dependencies",
    "uv_run_command",
    "uv_get_version",
]


def register_tools(mcp):
    """Register all UV package manager tools."""

    executor = CommandExecutor()

    @mcp.tool()
    def uv_install_package(
        package_name: str,
        version: str = "",
        dev: bool = False,
    ) -> str:
        """Install a Python package using uv.

        Args:
            package_name: Name of the package to install
            version: Specific version to install (optional)
            dev: Install as development dependency (default: False)

        Returns:
            JSON string with installation result
        """
        try:
            # Build command arguments
            args = ["pip", "install"]

            if dev:
                args.append("--dev")

            # Add package with version if specified
            if version:
                args.append(f"{package_name}=={version}")
            else:
                args.append(package_name)

            # Execute uv command
            result = executor.execute("uv", args, timeout=120)

            return json.dumps({
                "success": result["success"],
                "package": package_name,
                "version": version or "latest",
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"uv_install_package failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def uv_uninstall_package(package_name: str) -> str:
        """Uninstall a Python package using uv.

        Args:
            package_name: Name of the package to uninstall

        Returns:
            JSON string with uninstallation result
        """
        try:
            result = executor.execute(
                "uv",
                ["pip", "uninstall", package_name, "-y"],
                timeout=60,
            )

            return json.dumps({
                "success": result["success"],
                "package": package_name,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"uv_uninstall_package failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def uv_create_venv(path: str = ".venv", python_version: str = "") -> str:
        """Create a virtual environment using uv.

        Args:
            path: Path for the virtual environment (default: ".venv")
            python_version: Python version to use (e.g., "3.12", optional)

        Returns:
            JSON string with creation result
        """
        try:
            # Build command arguments
            args = ["venv", path]

            if python_version:
                args.extend(["--python", python_version])

            # Execute uv command
            result = executor.execute("uv", args, timeout=120)

            # Get absolute path
            venv_path = sanitize_path(path)

            return json.dumps({
                "success": result["success"],
                "venv_path": str(venv_path),
                "python_version": python_version or "default",
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"uv_create_venv failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def uv_list_packages(format: str = "json") -> str:
        """List installed packages using uv.

        Args:
            format: Output format - "json" or "text" (default: "json")

        Returns:
            JSON string with list of installed packages
        """
        try:
            if format not in ["json", "text"]:
                return json.dumps({
                    "error": f"Invalid format: {format}. Use 'json' or 'text'"
                })

            # Build command arguments
            args = ["pip", "list"]
            if format == "json":
                args.append("--format=json")

            # Execute uv command
            result = executor.execute("uv", args, timeout=60)

            if not result["success"]:
                return json.dumps({
                    "error": "Failed to list packages",
                    "stderr": result["stderr"],
                })

            # Parse output
            if format == "json":
                packages = json.loads(result["stdout"])
                return json.dumps({
                    "packages": packages,
                    "count": len(packages),
                })
            else:
                return json.dumps({
                    "output": result["stdout"],
                })

        except Exception as e:
            logger.error(f"uv_list_packages failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def uv_init_project(path: str = ".", name: str = "") -> str:
        """Initialize a new Python project using uv.

        Args:
            path: Path for the project (default: current directory)
            name: Project name (optional)

        Returns:
            JSON string with initialization result
        """
        try:
            # Build command arguments
            args = ["init", path]

            if name:
                args.extend(["--name", name])

            # Execute uv command
            result = executor.execute("uv", args, timeout=60)

            # Get absolute path
            project_path = sanitize_path(path)

            return json.dumps({
                "success": result["success"],
                "project_path": str(project_path),
                "name": name or Path(path).name,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"uv_init_project failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def uv_sync_dependencies(project_path: str = ".") -> str:
        """Sync project dependencies using uv.

        Args:
            project_path: Path to the project directory (default: current directory)

        Returns:
            JSON string with sync result
        """
        try:
            # Execute uv sync command
            result = executor.execute(
                "uv",
                ["sync"],
                cwd=project_path,
                timeout=180,
            )

            return json.dumps({
                "success": result["success"],
                "project_path": project_path,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"uv_sync_dependencies failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def uv_lock_dependencies(project_path: str = ".") -> str:
        """Lock project dependencies using uv.

        Args:
            project_path: Path to the project directory (default: current directory)

        Returns:
            JSON string with lock result
        """
        try:
            # Execute uv lock command
            result = executor.execute(
                "uv",
                ["lock"],
                cwd=project_path,
                timeout=180,
            )

            return json.dumps({
                "success": result["success"],
                "project_path": project_path,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"uv_lock_dependencies failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def uv_run_command(command: str, args: list[str] = None) -> str:
        """Run a command in the uv environment.

        Args:
            command: Command to run
            args: List of command arguments (optional)

        Returns:
            JSON string with command output
        """
        try:
            if args is None:
                args = []

            # Build uv run command
            uv_args = ["run", command] + args

            # Execute uv run command
            result = executor.execute("uv", uv_args, timeout=120)

            return json.dumps({
                "success": result["success"],
                "command": command,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "returncode": result["returncode"],
            })

        except Exception as e:
            logger.error(f"uv_run_command failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def uv_get_version() -> str:
        """Get uv version information.

        Returns:
            JSON string with uv version
        """
        try:
            result = executor.execute("uv", ["--version"], timeout=10)

            return json.dumps({
                "success": result["success"],
                "version": result["stdout"].strip(),
                "stderr": result["stderr"],
            })

        except Exception as e:
            logger.error(f"uv_get_version failed: {e}")
            return json.dumps({"error": str(e)})
