#!/usr/bin/env python3
"""
MCP Server Build Script
-----------------------
Cross-platform build script for packaging the MCP server with PyInstaller.
Supports Windows and Linux.

Usage:
    python build.py              # Build for current platform
    python build.py --onefile    # Build as single executable
    python build.py --clean      # Clean build artifacts first
"""

import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
import time
from typing import Any

# Change to project root directory (two levels up from this script)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
os.chdir(PROJECT_ROOT)


def get_platform_info() -> dict[str, Any]:
    """Get current platform information."""
    system = platform.system().lower()
    is_windows = system == "windows"
    is_linux = system == "linux"
    return {
        "system": system,
        "is_windows": is_windows,
        "is_linux": is_linux,
        "arch": platform.machine(),
    }


def find_site_packages():
    """Find site-packages directory."""
    # Try virtual environment first
    venv_paths = [
        Path(".venv/Lib/site-packages"),  # Windows
        Path(".venv/lib"),  # Linux (need to find python3.x subdirectory)
    ]

    for venv_path in venv_paths:
        if venv_path.exists():
            if venv_path.name == "lib":
                # Linux: find python3.x subdirectory
                python_dirs = list(venv_path.glob("python3.*/site-packages"))
                if python_dirs:
                    return python_dirs[0]
            else:
                return venv_path

    # Fallback to system site-packages
    import site

    return Path(site.getsitepackages()[0])


def get_collect_all_packages():
    """Get list of packages to collect all submodules from."""
    return [
        "fastmcp",  # FastMCP and all its submodules
        "mcp",  # MCP protocol package
        "httpx",  # HTTP client
        "uvicorn",  # ASGI server
        "websockets",  # WebSocket support
        "pydantic",  # Data validation
        "pydantic_core",  # Pydantic core
        "rich",  # Console output
        "anyio",  # Async I/O
        "authlib",  # Authentication
        "cyclopts",  # CLI framework
        "jsonref",  # JSON references
        "jsonschema_path",  # JSON schema
        "openapi_pydantic",  # OpenAPI support
        "pydocket",  # Redis simulation
        "fakeredis",  # Fake Redis
        "lupa",  # Lua integration
        "sniffio",  # Async library detection
    ]


def get_hidden_imports():
    """Get list of hidden imports needed for local modules."""
    return [
        # Local tool modules
        "mcp_server.tools.compression",
        "mcp_server.tools.compression.handlers",
        "mcp_server.tools.web",
        "mcp_server.tools.web.handlers",
        "mcp_server.tools.file",
        "mcp_server.tools.file.handlers",
        "mcp_server.tools.data",
        "mcp_server.tools.data.handlers",
        "mcp_server.tools.text",
        "mcp_server.tools.text.handlers",
        "mcp_server.tools.system",
        "mcp_server.tools.system.handlers",
        "mcp_server.tools.utility",
        "mcp_server.tools.utility.handlers",
        "mcp_server.tools.subagent",
        "mcp_server.tools.subagent.handlers",
        "mcp_server.tools.subagent_config",
        "mcp_server.tools.search_engine",
        "mcp_server.tools.registry",
        # Local utility modules
        "mcp_server.utils",
        "mcp_server.command_executor",
        "mcp_server.cli",
        "mcp_server.cli.config",
        # Additional third-party dependencies
        "psutil",
        "yaml",
        "lxml",
        "lxml.etree",
        "lxml.html",
        "bs4",
        "requests",
        "urllib3",
        "ddgs",
        "dateutil",
    ]


def get_data_files() -> list[Any]:
    """Get list of data files to include."""
    site_packages = find_site_packages()
    data_files: list[Any] = []

    # Include FastMCP metadata
    fastmcp_dist = list(site_packages.glob("fastmcp-*.dist-info"))
    for dist_info in fastmcp_dist:
        data_files.append((str(dist_info), dist_info.name))

    # Include fakeredis commands.json
    fakeredis_json = site_packages / "fakeredis" / "commands.json"
    if fakeredis_json.exists():
        data_files.append((str(fakeredis_json), "fakeredis"))

    # Include plugin config.yaml files for tool discovery
    tools_dir = PROJECT_ROOT / "src" / "mcp_server" / "tools"
    for config_yaml in tools_dir.glob("*/config.yaml"):
        plugin_name = config_yaml.parent.name
        dest = os.path.join("mcp_server", "tools", plugin_name)
        data_files.append((str(config_yaml), dest))
        print(f"  Including plugin config: {plugin_name}/config.yaml")

    return data_files


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("🧹 Cleaning build artifacts...")

    dirs_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = ["*.spec"]

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"  Removing {dir_name}/")
            shutil.rmtree(dir_name, ignore_errors=True)

    for pattern in files_to_remove:
        for file_path in glob.glob(pattern):
            print(f"  Removing {file_path}")
            os.remove(file_path)

    print("[Clean] Clean complete\n")


def build_executable(onefile: bool = False) -> bool:
    """Build executable using PyInstaller."""
    plat = get_platform_info()

    print(f"[Build] Building MCP Server for {plat['system']} ({plat['arch']})...\n")

    # Check if PyInstaller is installed
    try:
        __import__("PyInstaller")
        print("[OK] PyInstaller is installed\n")
    except ImportError:
        print("[ERROR] PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller installed\n")

    # Prepare PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "oh-my-mcp",
        "--console",  # Console application
        "--noconfirm",  # Replace output directory without asking
    ]

    # Add onefile option if requested
    if onefile:
        cmd.append("--onefile")
        print("[Package] Building as single executable file\n")
    else:
        print("[Package] Building as directory bundle\n")

    # Add collect-all packages (auto-discover all submodules)
    collect_packages = get_collect_all_packages()
    print(f"[Collect] Auto-collecting {len(collect_packages)} packages with all submodules...")
    for package in collect_packages:
        cmd.extend(["--collect-all", package])

    # Add hidden imports (for local modules)
    hidden_imports = get_hidden_imports()
    print(f"[Imports] Adding {len(hidden_imports)} local hidden imports...")
    for module in hidden_imports:
        cmd.extend(["--hidden-import", module])

    # Add data files
    data_files = get_data_files()
    print(f"[Data] Adding {len(data_files)} data files...")
    for src, dest in data_files:
        cmd.extend(["--add-data", f"{src}{os.pathsep}{dest}"])

    # Add exclude modules (to reduce size)
    excludes = ["tkinter", "matplotlib", "numpy", "pandas", "PIL", "IPython", "jupyter"]
    print(f"[Exclude] Excluding {len(excludes)} unnecessary modules...")
    for module in excludes:
        cmd.extend(["--exclude-module", module])

    # Add main script
    cmd.append("src/mcp_server/main.py")

    # Run PyInstaller
    print(f"\n[Run] Running PyInstaller...\n")
    print(f"Command: {' '.join(cmd[:5])} ... (and {len(cmd)-5} more args)\n")

    start = time.time()
    try:
        _ = subprocess.run(cmd, check=True, capture_output=False)
        print("\n[OK] Build successful!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed with exit code {e.returncode}\n")
        return False
    finally:
        end = time.time()
        duration = end - start
        print(f"\n[Time] Build duration: {duration:.2f} seconds\n")


def show_build_info():
    """Show information about the build output."""
    plat = get_platform_info()

    if plat["is_windows"]:
        exe_path = Path("dist/oh-my-mcp/oh-my-mcp.exe")
        onefile_path = Path("dist/oh-my-mcp.exe")
    else:
        exe_path = Path("dist/oh-my-mcp/oh-my-mcp")
        onefile_path = Path("dist/oh-my-mcp")

    if onefile_path.exists():
        size_mb = onefile_path.stat().st_size / (1024 * 1024)
        print(f"[Package] Single executable built:")
        print(f"   Location: {onefile_path}")
        print(f"   Size: {size_mb:.1f} MB")
        print(f"\n[Usage] Usage: {onefile_path}")
    elif exe_path.exists():
        dir_size = sum(f.stat().st_size for f in exe_path.parent.rglob("*") if f.is_file())
        size_mb = dir_size / (1024 * 1024)
        print(f"[Package] Directory bundle built:")
        print(f"   Location: {exe_path.parent}")
        print(f"   Executable: {exe_path}")
        print(f"   Total size: {size_mb:.1f} MB")
        print(f"\n[Usage] Usage: {exe_path}")

    print(f"\n[Config] To configure Claude Desktop:")
    if plat["is_windows"]:
        config_path = os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json")
    else:
        config_path = os.path.expanduser(
            "~/Library/Application Support/Claude/claude_desktop_config.json"
        )

    print(f"   Edit: {config_path}")
    print(
        f'   Add: "command": "{os.path.abspath(exe_path if exe_path.exists() else onefile_path)}"'
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build MCP Server executable with PyInstaller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                 # Build directory bundle
  python build.py --onefile       # Build single executable
  python build.py --clean         # Clean and build
  python build.py --onefile --clean  # Clean and build single file
        """,
    )

    parser.add_argument(
        "--onefile",
        "-F",
        action="store_true",
        help="Build as single executable file (slower startup, easier distribution)",
    )

    parser.add_argument(
        "--clean", "-c", action="store_true", help="Clean build artifacts before building"
    )

    args = parser.parse_args()

    # Show header
    print("=" * 70)
    print("  MCP Server Build Script")
    print("=" * 70)
    print()

    # Clean if requested
    if args.clean:
        clean_build_artifacts()

    # Build
    success = build_executable(onefile=args.onefile)

    # Show results
    if success:
        print()
        show_build_info()
        print()
        print("=" * 70)
        print("  Build Complete!")
        print("=" * 70)
        return 0
    else:
        print()
        print("=" * 70)
        print("  Build Failed!")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
