"""
System information and monitoring tool handlers.

Provides tools for:
- System information (OS, platform, Python version)
- Resource monitoring (CPU, memory, disk)
- Environment variables
- Process information
- Time and timezone utilities
"""

import json
import os
import platform
import sys
from datetime import UTC, datetime
from typing import Any

import psutil

from mcp_server.tools.registry import tool_handler
from mcp_server.utils import ValidationError, error_json, format_bytes, logger


@tool_handler
def get_system_info() -> str:
    """
    Get comprehensive system information.

    Returns:
        JSON string containing system details
    """
    try:
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
                "user": os.getenv("USERNAME") or os.getenv("USER") or "unknown",
                "home": os.path.expanduser("~"),
                "cwd": os.getcwd(),
            },
        }

        return json.dumps(info, indent=2)

    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return error_json(f"Failed to get system info: {e!s}")


@tool_handler
def get_cpu_info() -> str:
    """
    Get CPU information and current usage.

    Returns:
        JSON string containing CPU details and usage
    """
    try:
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
        return error_json(f"Failed to get CPU info: {e!s}")


@tool_handler
def get_memory_info() -> str:
    """
    Get memory (RAM) usage statistics.

    Returns:
        JSON string containing memory usage details
    """
    try:
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
        return error_json(f"Failed to get memory info: {e!s}")


@tool_handler
def get_disk_info(path: str = "/") -> str:
    """
    Get disk space information for a path.

    Args:
        path: Path to check disk space (default: root/current drive)

    Returns:
        JSON string containing disk usage details
    """
    try:
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
        return error_json(f"Failed to get disk info: {e!s}")


@tool_handler
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

        return json.dumps({"name": name, "value": value, "exists": name in os.environ}, indent=2)

    except Exception as e:
        logger.error(f"Failed to get env variable: {e}")
        return error_json(f"Failed to get env variable: {e!s}")


@tool_handler
def list_env_variables(filter_pattern: str = "") -> str:
    """
    List all environment variables.

    Args:
        filter_pattern: Optional substring to filter variable names (case-insensitive)

    Returns:
        JSON string with environment variables
    """
    try:
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
        return error_json(f"Failed to list env variables: {e!s}")


@tool_handler
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

        now = datetime.now(UTC) if timezone.lower() == "utc" else datetime.now()

        result: dict[str, Any] = {"timezone": timezone}

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
        return error_json(f"Failed to get current time: {e!s}")


@tool_handler
def get_process_info() -> str:
    """
    Get information about the current process.

    Returns:
        JSON string with process details
    """
    try:
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
        return error_json(f"Failed to get process info: {e!s}")


@tool_handler
def get_network_interfaces() -> str:
    """
    List network interfaces with addresses and link status.

    Returns:
        JSON string with per-interface IPv4/IPv6/MAC addresses, MTU,
        up/down state and speed
    """
    try:
        addrs_by_if = psutil.net_if_addrs()
        stats_by_if = psutil.net_if_stats()

        interfaces = []
        for name, addr_list in addrs_by_if.items():
            entry: dict[str, Any] = {"name": name, "addresses": []}
            stats = stats_by_if.get(name)
            if stats is not None:
                entry["is_up"] = stats.isup
                entry["mtu"] = stats.mtu
                entry["speed_mbps"] = stats.speed
            for addr in addr_list:
                family = str(addr.family).rsplit(".", 1)[-1]
                info = {"family": family, "address": addr.address}
                if addr.netmask:
                    info["netmask"] = addr.netmask
                entry["addresses"].append(info)
            interfaces.append(entry)

        return json.dumps({"success": True, "interfaces": interfaces}, indent=2)
    except Exception as e:
        logger.error(f"Failed to get network interfaces: {e}")
        return error_json(f"Failed to get network interfaces: {e}")


@tool_handler
def get_battery_info() -> str:
    """
    Get battery status (percentage, charging state, time estimates).

    On systems without a battery (desktops) returns has_battery=False.

    Returns:
        JSON string with battery information
    """
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return json.dumps({"success": True, "has_battery": False}, indent=2)

        result: dict[str, Any] = {
            "success": True,
            "has_battery": True,
            "percent": round(battery.percent, 1),
            "plugged_in": battery.power_plugged is True,
        }
        if battery.secsleft not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN, -1):
            hours, remainder = divmod(battery.secsleft, 3600)
            result["time_left"] = f"{hours:02d}:{remainder // 60:02d}"
        elif battery.power_plugged:
            result["time_left"] = "charging"
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Failed to get battery info: {e}")
        return error_json(f"Failed to get battery info: {e}")


@tool_handler
def list_processes(sort_by: str = "cpu", limit: int = 20) -> str:
    """
    List running processes sorted by CPU, memory, name or PID.

    Args:
        sort_by: "cpu", "memory", "name" or "pid" (default "cpu").
            CPU percentages need a short sampling interval (~0.1s).
        limit: Maximum number of processes returned (default 20, max 200)

    Returns:
        JSON string with the process list and total process count
    """
    try:
        if limit < 1 or limit > 200:
            raise ValidationError("limit must be between 1 and 200")
        sort_key = sort_by.lower()
        if sort_key not in ("cpu", "memory", "name", "pid"):
            raise ValidationError("sort_by must be one of: cpu, memory, name, pid")

        procs = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = proc.info
                procs.append(
                    {
                        "pid": info["pid"],
                        "name": info["name"] or "",
                        "cpu_percent": info["cpu_percent"] or 0.0,
                        "memory_percent": round(info["memory_percent"] or 0.0, 2),
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        reverse = sort_key in ("cpu", "memory")
        procs.sort(
            key=lambda p: p[sort_key if sort_key != "cpu" else "cpu_percent"], reverse=reverse
        )

        return json.dumps(
            {
                "success": True,
                "sort_by": sort_key,
                "total_processes": len(procs),
                "returned": min(limit, len(procs)),
                "processes": procs[:limit],
            },
            indent=2,
        )
    except ValidationError as e:
        logger.warning(f"list_processes validation error: {e}")
        return error_json(str(e))
    except Exception as e:
        logger.error(f"Failed to list processes: {e}")
        return error_json(f"Failed to list processes: {e}")
