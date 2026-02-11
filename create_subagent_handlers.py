#!/usr/bin/env python3
"""Script to create subagent handlers.py from subagent.py"""

import re
from pathlib import Path

# Get script directory
script_dir = Path(__file__).parent

# Read subagent.py
subagent_path = script_dir / "src" / "mcp_server" / "tools" / "subagent.py"
with open(subagent_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find where register_tools starts
register_start = content.find("def register_tools(mcp: Any) -> None:")
before_register = content[:register_start]

# Fix imports
before_register = before_register.replace("from ..utils import", "from mcp_server.utils import")
before_register = before_register.replace(
    "from .subagent_config import", "from mcp_server.tools.subagent_config import"
)

# Add registry import
handlers_content = before_register + "\nfrom mcp_server.tools.registry import tool_handler\n\n"

# Extract tool functions from register_tools
after_register = content[register_start:]

# Find all @mcp.tool() decorated functions
pattern = r"    @mcp\.tool\(\)\s+def ([\w_]+)\("
tool_names = re.findall(pattern, after_register)

print(f"Found {len(tool_names)} tools: {tool_names}")

# Extract each tool function
for tool_name in tool_names:
    # Find function start
    func_pattern = rf"    @mcp\.tool\(\)\s+def {tool_name}\([^)]*\)[^:]*:"
    func_match = re.search(func_pattern, after_register)

    if func_match:
        start_pos = func_match.start()

        # Find next @mcp.tool() or end marker
        next_tool = re.search(r"\n    @mcp\.tool\(\)", after_register[start_pos + 10 :])
        end_marker = re.search(r'\n    logger\.info\("Subagent tools', after_register[start_pos:])

        if next_tool:
            end_pos = start_pos + next_tool.start() + 10
        elif end_marker:
            end_pos = start_pos + end_marker.start()
        else:
            end_pos = len(after_register)

        # Extract function
        func_text = after_register[start_pos:end_pos]

        # Replace decorator and remove indentation
        func_text = func_text.replace("    @mcp.tool()", "@tool_handler")
        lines = func_text.split("\n")
        dedented_lines = []
        for line in lines:
            if line.startswith("    "):
                dedented_lines.append(line[4:])
            else:
                dedented_lines.append(line)

        func_text = "\n".join(dedented_lines)
        handlers_content += func_text + "\n\n"

# Write handlers.py
output_path = script_dir / "src" / "mcp_server" / "tools" / "subagent" / "handlers.py"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(handlers_content)

print(f"Created {output_path}")
