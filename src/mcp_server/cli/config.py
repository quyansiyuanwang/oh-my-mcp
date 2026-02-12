"""
MCP Server Configuration Generator

Generates JSON configuration for MCP clients (e.g., Claude Desktop).
Can also run a simple HTTP server to provide configuration on demand.
"""

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Optional


def get_python_executable() -> str:
    """Get the Python executable path for the current environment."""
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        # In a virtual environment
        return sys.executable
    return sys.executable


def get_server_path() -> str:
    """Get the path to main.py."""
    return str(Path(__file__).parent / "main.py")


def generate_mcp_config(
    server_name: str = "comprehensive-mcp",
    python_path: Optional[str] = None,
    server_path: Optional[str] = None,
) -> dict[str, Any]:
    """
    Generate MCP configuration for Claude Desktop and other clients.

    Args:
        server_name: Name for the MCP server in configuration
        python_path: Path to Python executable (auto-detected if None)
        server_path: Path to main.py (auto-detected if None)

    Returns:
        Dictionary with MCP configuration
    """
    if python_path is None:
        python_path = get_python_executable()

    if server_path is None:
        server_path = get_server_path()

    config = {
        "mcpServers": {
            server_name: {
                "command": python_path,
                "args": [server_path],
                "env": {},
                "description": "Comprehensive MCP Server with 83 practical tools",
            }
        }
    }

    return config


def save_config(config: dict[str, Any], output_path: str = "mcp_config.json") -> str:
    """Save configuration to file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return output_path


def get_claude_config_path() -> Optional[Path]:
    """Get the Claude Desktop configuration path."""
    if sys.platform == "win32":
        # Windows
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":
        # macOS
        home = Path.home()
        return home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        # Linux
        home = Path.home()
        return home / ".config" / "claude" / "claude_desktop_config.json"

    return None


def merge_with_existing_config(
    new_config: dict[str, Any], existing_config_path: Path
) -> dict[str, Any]:
    """Merge new MCP server config with existing configuration."""
    try:
        if existing_config_path.exists():
            with open(existing_config_path, "r", encoding="utf-8") as f:
                existing: dict[str, Any] = json.load(f)

            # Merge mcpServers
            if "mcpServers" not in existing:
                existing["mcpServers"] = {}

            existing["mcpServers"].update(new_config["mcpServers"])
            return existing
        else:
            return new_config
    except Exception as e:
        print(f"Warning: Could not read existing config: {e}")
        return new_config


class ConfigHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for serving MCP configuration."""

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/config" or self.path == "/":
            config = generate_mcp_config()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self.wfile.write(json.dumps(config, indent=2).encode("utf-8"))

        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")

        elif self.path == "/info":
            info = {
                "server": "Comprehensive MCP Server Configuration Generator",
                "version": "0.1.0",
                "endpoints": {
                    "/": "Get MCP configuration JSON",
                    "/config": "Get MCP configuration JSON",
                    "/health": "Health check",
                    "/info": "This information",
                },
                "python_executable": get_python_executable(),
                "server_path": get_server_path(),
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(info, indent=2).encode("utf-8"))

        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format: str, *args: Any) -> None:
        """Custom log message format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_http_server(port: int = 8765) -> None:
    """Run HTTP server to provide configuration."""
    server_address = ("", port)
    httpd = HTTPServer(server_address, ConfigHTTPHandler)

    print("=" * 70)
    print(f"MCP Configuration Server running on http://localhost:{port}")
    print("=" * 70)
    print("\nAvailable endpoints:")
    print(f"  http://localhost:{port}/config  - Get MCP configuration JSON")
    print(f"  http://localhost:{port}/info    - Server information")
    print(f"  http://localhost:{port}/health  - Health check")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate MCP server configuration for Claude Desktop and other clients"
    )

    parser.add_argument(
        "--server-name",
        default="comprehensive-mcp",
        help="Name for the MCP server in configuration (default: comprehensive-mcp)",
    )

    parser.add_argument(
        "--output",
        "-o",
        default="mcp_config.json",
        help="Output file path (default: mcp_config.json)",
    )

    parser.add_argument(
        "--claude",
        action="store_true",
        help="Install configuration to Claude Desktop config file",
    )

    parser.add_argument(
        "--http-server",
        action="store_true",
        help="Run HTTP server to provide configuration on port 8765",
    )

    parser.add_argument(
        "--port", type=int, default=8765, help="Port for HTTP server (default: 8765)"
    )

    parser.add_argument("--show-config", action="store_true", help="Print configuration to console")

    args = parser.parse_args()

    # Generate configuration
    config = generate_mcp_config(server_name=args.server_name)

    if args.http_server:
        # Run HTTP server
        run_http_server(args.port)

    elif args.claude:
        # Install to Claude Desktop
        claude_config_path = get_claude_config_path()

        if claude_config_path:
            print("Installing to Claude Desktop configuration...")
            print(f"Config path: {claude_config_path}")

            # Create directory if it doesn't exist
            claude_config_path.parent.mkdir(parents=True, exist_ok=True)

            # Merge with existing config
            merged_config = merge_with_existing_config(config, claude_config_path)

            # Save
            with open(claude_config_path, "w", encoding="utf-8") as f:
                json.dump(merged_config, f, indent=2, ensure_ascii=False)

            print("✓ Configuration installed successfully!")
            print(f"\nServer '{args.server_name}' added to Claude Desktop configuration.")
            print("Restart Claude Desktop to use the new MCP server.")
        else:
            print("Error: Could not determine Claude Desktop configuration path")
            sys.exit(1)

    else:
        # Save to file
        output_path = save_config(config, args.output)
        print(f"✓ Configuration saved to: {output_path}")

        if args.show_config:
            print("\nConfiguration:")
            print(json.dumps(config, indent=2, ensure_ascii=False))

        print("\nTo use this configuration:")
        print("1. Copy the content to your MCP client configuration")
        print("2. Or run with --claude to automatically install to Claude Desktop")
        print("3. Or run with --http-server to serve configuration via HTTP")


if __name__ == "__main__":
    main()
