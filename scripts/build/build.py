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
import re
import shutil
import subprocess
import sys
import time
import tomllib  # Python 3.11+
from pathlib import Path
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


def parse_pyproject_dependencies() -> list[str]:
    """Parse dependencies from pyproject.toml and extract package names."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"

    if not pyproject_path.exists():
        print("[Warning] pyproject.toml not found, using default packages")
        return []

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    dependencies = data.get("project", {}).get("dependencies", [])

    # Extract package names from dependency specifications
    # e.g., "requests>=2.31.0" -> "requests"
    # e.g., "tomli>=2.0.0; python_version < '3.11'" -> "tomli"
    package_names = []
    for dep in dependencies:
        # Remove version specifiers and conditions
        match = re.match(r"^([a-zA-Z0-9_-]+)", dep.split(";")[0])
        if match:
            package_name = match.group(1)
            # Normalize package names (e.g., beautifulsoup4 -> bs4)
            if package_name == "beautifulsoup4":
                package_names.append("bs4")
            elif package_name == "python-dateutil":
                package_names.append("dateutil")
            else:
                package_names.append(package_name)

    return package_names


def get_collect_all_packages():
    """Get list of packages to collect all submodules from (auto-detected from pyproject.toml)."""

    # Core MCP packages that need full collection
    core_packages = [
        "fastmcp",  # FastMCP and all its submodules
        "mcp",  # MCP protocol package
        "lupa",  # Lua runtime for fakeredis (has binary components)
        "fakeredis",  # Redis simulation
    ]

    # Read dependencies from pyproject.toml
    project_dependencies = parse_pyproject_dependencies()

    print(f"[Auto-detect] Found {len(project_dependencies)} dependencies in pyproject.toml")

    # Combine core packages with project dependencies
    all_packages = list(set(core_packages + project_dependencies))

    # Add extra packages that need special handling
    # rich needs all its submodules including _unicode_data
    if "rich" not in all_packages:
        all_packages.append("rich")

    # Remove packages that should not be collected entirely
    exclude_from_collect = []  # Add packages to exclude if needed

    all_packages = [pkg for pkg in all_packages if pkg not in exclude_from_collect]

    return all_packages


def get_hidden_imports():
    """Get list of hidden imports needed for local modules (fully auto-detected)."""
    hidden_imports = []

    # Auto-detect tool plugins from tools directory
    tools_dir = PROJECT_ROOT / "src" / "mcp_server" / "tools"
    print(f"[Auto-detect] Scanning tools directory: {tools_dir}")

    if not tools_dir.exists():
        print(f"[Warning] Tools directory not found: {tools_dir}")
        return hidden_imports

    for config_yaml in tools_dir.glob("*/config.yaml"):
        plugin_name = config_yaml.parent.name
        plugin_dir = config_yaml.parent

        # Add plugin package
        hidden_imports.append(f"mcp_server.tools.{plugin_name}")

        # Add handlers module if it exists
        if (plugin_dir / "handlers.py").exists():
            hidden_imports.append(f"mcp_server.tools.{plugin_name}.handlers")

        # Auto-detect all Python modules in plugin directory
        for py_file in plugin_dir.glob("*.py"):
            if py_file.name not in ["__init__.py", "handlers.py"]:
                module_name = py_file.stem
                hidden_imports.append(f"mcp_server.tools.{plugin_name}.{module_name}")
                print(f"  Found plugin module: {plugin_name}.{module_name}")

        print(f"  Detected plugin: {plugin_name}")

    # Auto-detect other modules in tools directory (non-plugin .py files)
    for py_file in tools_dir.glob("*.py"):
        if py_file.name != "__init__.py":
            module_name = py_file.stem
            hidden_imports.append(f"mcp_server.tools.{module_name}")
            print(f"  Found tools module: {module_name}")

    # Auto-detect CLI modules
    cli_dir = PROJECT_ROOT / "src" / "mcp_server" / "cli"
    if cli_dir.exists():
        hidden_imports.append("mcp_server.cli")
        for py_file in cli_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                module_name = py_file.stem
                hidden_imports.append(f"mcp_server.cli.{module_name}")
                print(f"  Found CLI module: {module_name}")

    # Auto-detect root-level mcp_server modules
    root_modules = ["utils", "command_executor"]
    for module_name in root_modules:
        module_path = PROJECT_ROOT / "src" / "mcp_server" / f"{module_name}.py"
        if module_path.exists():
            hidden_imports.append(f"mcp_server.{module_name}")
            print(f"  Found root module: {module_name}")

    print(f"[Auto-detect] Total hidden imports: {len(hidden_imports)}")
    return hidden_imports


def get_data_files() -> list[Any]:
    """Get list of data files to include (auto-detected)."""
    site_packages = find_site_packages()
    data_files: list[Any] = []

    # Include FastMCP metadata
    fastmcp_dist = list(site_packages.glob("fastmcp-*.dist-info"))
    for dist_info in fastmcp_dist:
        data_files.append((str(dist_info), dist_info.name))
        print(f"  Including dist-info: {dist_info.name}")

    # Include fakeredis commands.json if it exists
    fakeredis_json = site_packages / "fakeredis" / "commands.json"
    if fakeredis_json.exists():
        data_files.append((str(fakeredis_json), "fakeredis"))
        print("  Including fakeredis commands.json")

    # Auto-detect and include plugin config.yaml files for tool discovery
    tools_dir = PROJECT_ROOT / "src" / "mcp_server" / "tools"
    if tools_dir.exists():
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
    print(f"[Collect] Auto-collecting {len(collect_packages)} packages with all submodules:")
    for package in collect_packages:
        print(f"  - {package}")
        cmd.extend(["--collect-all", package])
    print()

    # Add hidden imports (for local modules only)
    hidden_imports = get_hidden_imports()
    print(f"[Imports] Adding {len(hidden_imports)} local hidden imports")
    for module in hidden_imports:
        cmd.extend(["--hidden-import", module])
    print()

    # Add data files
    data_files = get_data_files()
    print(f"[Data] Adding {len(data_files)} data files")
    for src, dest in data_files:
        cmd.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
    print()

    # Add exclude modules (to reduce size). PIL/Pillow is required by
    # computer-use screenshots, so it must NOT be excluded.
    excludes = ["tkinter", "matplotlib", "numpy", "pandas", "IPython", "jupyter"]
    print(f"[Exclude] Excluding {len(excludes)} unnecessary modules")
    for module in excludes:
        cmd.extend(["--exclude-module", module])
    print()

    # Add main script
    cmd.append("src/mcp_server/main.py")

    # Run PyInstaller
    print("\n[Run] Running PyInstaller...\n")
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
        print("[Package] Single executable built:")
        print(f"   Location: {onefile_path}")
        print(f"   Size: {size_mb:.1f} MB")
        print(f"\n[Usage] Usage: {onefile_path}")
    elif exe_path.exists():
        dir_size = sum(f.stat().st_size for f in exe_path.parent.rglob("*") if f.is_file())
        size_mb = dir_size / (1024 * 1024)
        print("[Package] Directory bundle built:")
        print(f"   Location: {exe_path.parent}")
        print(f"   Executable: {exe_path}")
        print(f"   Total size: {size_mb:.1f} MB")
        print(f"\n[Usage] Usage: {exe_path}")

    print("\n[Config] To configure Claude Desktop:")
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
    print("  MCP Server Build Script (Fully Automated)")
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
