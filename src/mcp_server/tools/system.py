"""
System information and monitoring tools for the MCP server.

Provides tools for:
- System information (OS, platform, Python version)
- Resource monitoring (CPU, memory, disk)
- Environment variables
- Process information
- Time and timezone utilities
"""

import os
import sys
import platform
from datetime import datetime
from typing import Optional

import psutil

from .utils import logger, format_bytes

# Module metadata
CATEGORY_NAME = "System"
CATEGORY_DESCRIPTION = "System info, CPU/memory monitoring, environment variables"
TOOLS = [
    "get_system_info",
    "get_cpu_info",
    "get_memory_info",
    "get_disk_info",
    "get_env_variable",
    "list_env_variables",
    "get_current_time",
    "get_process_info",
]


def register_tools(mcp):
    """Register all system tools with the MCP server."""

    @mcp.tool()
    def get_system_info() -> str:
        """
        Get comprehensive system information.

        Returns:
            JSON string containing system details
        """
        try:
            import json

            info = {
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "architecture": platform.architecture()[0],
                    "node": platform.node(),
                },
                "python": {
                    "version": sys.version,
                    "version_info": {
                        "major": sys.version_info.major,
                        "minor": sys.version_info.minor,
                        "micro": sys.version_info.micro,
                    },
                    "executable": sys.executable,
                    "implementation": platform.python_implementation(),
                },
                "environment": {
                    "user": os.getenv("USERNAME") or os.getenv("USER", "unknown"),
                    "home": os.path.expanduser("~"),
                    "cwd": os.getcwd(),
                },
            }

            return json.dumps(info, indent=2)

        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return f'{{"error": "Failed to get system info: {str(e)}"}}'

    @mcp.tool()
    def get_cpu_info() -> str:
        """
        Get CPU information and current usage.

        Returns:
            JSON string containing CPU details and usage
        """
        try:
            import json

            cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
            cpu_percent_per_core = psutil.cpu_percent(interval=1, percpu=True)
            cpu_count = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()

            info = {
                "usage_percent": cpu_percent,
                "usage_per_core": cpu_percent_per_core,
                "cores": {"logical": cpu_count, "physical": cpu_count_physical},
            }

            if cpu_freq:
                info["frequency"] = {
                    "current_mhz": cpu_freq.current,
                    "min_mhz": cpu_freq.min,
                    "max_mhz": cpu_freq.max,
                }

            return json.dumps(info, indent=2)

        except Exception as e:
            logger.error(f"Failed to get CPU info: {e}")
            return f'{{"error": "Failed to get CPU info: {str(e)}"}}'

    @mcp.tool()
    def get_memory_info() -> str:
        """
        Get memory (RAM) usage statistics.

        Returns:
            JSON string containing memory usage details
        """
        try:
            import json

            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()

            info = {
                "virtual_memory": {
                    "total": format_bytes(virtual_mem.total),
                    "available": format_bytes(virtual_mem.available),
                    "used": format_bytes(virtual_mem.used),
                    "free": format_bytes(virtual_mem.free),
                    "percent": virtual_mem.percent,
                    "total_bytes": virtual_mem.total,
                    "available_bytes": virtual_mem.available,
                    "used_bytes": virtual_mem.used,
                },
                "swap_memory": {
                    "total": format_bytes(swap_mem.total),
                    "used": format_bytes(swap_mem.used),
                    "free": format_bytes(swap_mem.free),
                    "percent": swap_mem.percent,
                    "total_bytes": swap_mem.total,
                },
            }

            return json.dumps(info, indent=2)

        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return f'{{"error": "Failed to get memory info: {str(e)}"}}'

    @mcp.tool()
    def get_disk_info(path: str = "/") -> str:
        """
        Get disk space information for a path.

        Args:
            path: Path to check disk space (default: root/current drive)

        Returns:
            JSON string containing disk usage details
        """
        try:
            import json

            # Use current directory if path is /
            if path == "/":
                path = os.getcwd()

            disk_usage = psutil.disk_usage(path)

            info = {
                "path": path,
                "total": format_bytes(disk_usage.total),
                "used": format_bytes(disk_usage.used),
                "free": format_bytes(disk_usage.free),
                "percent": disk_usage.percent,
                "total_bytes": disk_usage.total,
                "used_bytes": disk_usage.used,
                "free_bytes": disk_usage.free,
            }

            # Add partitions info
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": format_bytes(usage.total),
                            "used_percent": usage.percent,
                        }
                    )
                except Exception:
                    continue

            info["partitions"] = partitions

            return json.dumps(info, indent=2)

        except Exception as e:
            logger.error(f"Failed to get disk info: {e}")
            return f'{{"error": "Failed to get disk info: {str(e)}"}}'

    @mcp.tool()
    def get_env_variable(name: str, default: str = "") -> str:
        """
        Get an environment variable value.

        Args:
            name: Name of the environment variable
            default: Default value if variable not found (default: empty string)

        Returns:
            Environment variable value or default
        """
        try:
            value = os.getenv(name, default)

            import json

            return json.dumps(
                {"name": name, "value": value, "exists": name in os.environ}, indent=2
            )

        except Exception as e:
            logger.error(f"Failed to get env variable: {e}")
            return f'{{"error": "Failed to get env variable: {str(e)}"}}'

    @mcp.tool()
    def list_env_variables(filter_pattern: str = "") -> str:
        """
        List all environment variables.

        Args:
            filter_pattern: Optional substring to filter variable names (case-insensitive)

        Returns:
            JSON string with environment variables
        """
        try:
            import json

            env_vars = {}
            for key, value in os.environ.items():
                if not filter_pattern or filter_pattern.lower() in key.lower():
                    # Mask sensitive-looking values
                    if any(
                        sensitive in key.upper()
                        for sensitive in [
                            "PASSWORD",
                            "SECRET",
                            "TOKEN",
                            "KEY",
                            "CREDENTIAL",
                        ]
                    ):
                        env_vars[key] = "***MASKED***"
                    else:
                        env_vars[key] = value

            return json.dumps(
                {
                    "count": len(env_vars),
                    "filter": filter_pattern,
                    "variables": env_vars,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Failed to list env variables: {e}")
            return f'{{"error": "Failed to list env variables: {str(e)}"}}'

    @mcp.tool()
    def get_current_time(timezone: str = "local", format: str = "iso") -> str:
        """
        Get current date and time.

        Args:
            timezone: Timezone (default: local) - use 'utc' for UTC
            format: Output format - 'iso', 'timestamp', or 'readable' (default: iso)

        Returns:
            Current time in requested format
        """
        try:
            import json
            from datetime import timezone as tz

            if timezone.lower() == "utc":
                now = datetime.now(tz.utc)
            else:
                now = datetime.now()

            result = {"timezone": timezone}

            if format == "iso":
                result["time"] = now.isoformat()
            elif format == "timestamp":
                result["time"] = now.timestamp()
            elif format == "readable":
                result["time"] = now.strftime("%Y-%m-%d %H:%M:%S")
            else:
                result["time"] = now.isoformat()

            result["formats"] = {
                "iso": now.isoformat(),
                "timestamp": now.timestamp(),
                "readable": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Failed to get current time: {e}")
            return f'{{"error": "Failed to get current time: {str(e)}"}}'

    @mcp.tool()
    def get_process_info() -> str:
        """
        Get information about the current process.

        Returns:
            JSON string with process details
        """
        try:
            import json

            process = psutil.Process()

            with process.oneshot():
                info = {
                    "pid": process.pid,
                    "name": process.name(),
                    "status": process.status(),
                    "created": datetime.fromtimestamp(process.create_time()).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "cpu_percent": process.cpu_percent(interval=0.1),
                    "memory": {
                        "rss": format_bytes(process.memory_info().rss),
                        "vms": format_bytes(process.memory_info().vms),
                        "percent": round(process.memory_percent(), 2),
                    },
                    "threads": process.num_threads(),
                    "cwd": process.cwd(),
                }

            return json.dumps(info, indent=2)

        except Exception as e:
            logger.error(f"Failed to get process info: {e}")
            return f'{{"error": "Failed to get process info: {str(e)}"}}'

    # Register system resources
    @mcp.resource("system://info")
    def system_info_resource() -> str:
        """System information resource."""
        return get_system_info()

    @mcp.resource("system://stats")
    def system_stats_resource() -> str:
        """Real-time system statistics resource."""
        import json

        try:
            stats = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage(os.getcwd()).percent,
                "timestamp": datetime.now().isoformat(),
            }
            return json.dumps(stats, indent=2)
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
