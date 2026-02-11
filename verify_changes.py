#!/usr/bin/env python3
"""
Quick verification script to check tool counts after removing Python/UV/Pylance tools.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def count_tools():
    """Count total tools from all modules."""
    from mcp_server import tools

    tool_counts = {}
    total = 0

    # Import each tool module and count
    for module_name in tools.__all__:
        try:
            module = getattr(tools, module_name)
            # Count functions that don't start with underscore
            tool_count = sum(
                1
                for name in dir(module)
                if callable(getattr(module, name)) and not name.startswith("_")
            )
            tool_counts[module_name] = tool_count
            total += tool_count
        except Exception as e:
            print(f"Error importing {module_name}: {e}")

    return tool_counts, total


def verify_removals():
    """Verify that Python/UV/Pylance modules are removed."""
    from mcp_server import tools

    removed_modules = ["python", "uv", "pylance"]
    still_present = [m for m in removed_modules if m in tools.__all__]

    if still_present:
        print(f"❌ ERROR: These modules should be removed: {still_present}")
        return False

    print("✅ Python/UV/Pylance modules successfully removed")
    return True


def verify_command_whitelist():
    """Verify command whitelist is empty."""
    from mcp_server.command_executor import CommandValidator

    if len(CommandValidator.ALLOWED_COMMANDS) > 0:
        print(
            f"❌ ERROR: ALLOWED_COMMANDS should be empty, but contains: {CommandValidator.ALLOWED_COMMANDS}"
        )
        return False

    print("✅ Command whitelist is empty (no external commands allowed)")
    return True


def main():
    print("=" * 70)
    print("MCP Server Verification")
    print("=" * 70)
    print()

    # Check module removals
    print("1. Checking module removals...")
    if not verify_removals():
        return 1
    print()

    # Check command whitelist
    print("2. Checking command whitelist...")
    if not verify_command_whitelist():
        return 1
    print()

    # Count tools
    print("3. Counting tools...")
    try:
        tool_counts, total = count_tools()
        print(f"✅ Successfully counted tools")
        print()
        print("Tool counts by module:")
        for module, count in sorted(tool_counts.items()):
            print(f"  - {module:15s}: {count:2d} tools")
        print()
        print(f"Total tool modules: {len(tool_counts)}")
        print(f"Expected: 7 modules (removed python, uv, pylance)")
        print()

        if len(tool_counts) == 7:
            print("✅ Correct number of tool modules")
        else:
            print(f"⚠️  Warning: Expected 7 modules, found {len(tool_counts)}")

        print()
        print("=" * 70)
        print("Verification Complete!")
        print("=" * 70)
        return 0

    except Exception as e:
        print(f"❌ ERROR: Failed to count tools: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
