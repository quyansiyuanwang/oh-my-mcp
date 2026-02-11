#!/usr/bin/env python3
"""
MCP Server Configuration Script - Interactive Environment Setup
-----------------------------------------------------------------
This script helps you configure the MCP server environment, including:
- Python environment and dependencies
- Subagent API credentials (OpenAI, Anthropic, ZhipuAI)
- Claude Desktop integration

Usage:
    Interactive mode:    uv run configure.py
    Non-interactive:     uv run configure.py --provider openai --api-key sk-xxx
    Help:                uv run configure.py --help
"""

import sys
import os
import subprocess
import argparse
import json
import getpass
from pathlib import Path
from typing import Optional, List, Dict, Tuple


# Color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def strip_all():
        """Disable colors when not in TTY"""
        if not sys.stdout.isatty():
            Colors.HEADER = ""
            Colors.OKBLUE = ""
            Colors.OKCYAN = ""
            Colors.OKGREEN = ""
            Colors.WARNING = ""
            Colors.FAIL = ""
            Colors.ENDC = ""
            Colors.BOLD = ""
            Colors.UNDERLINE = ""


# Symbols for different platforms
class Symbols:
    SUCCESS = "[OK]"
    ERROR = "[ERROR]"
    WARNING = "[WARN]"
    INFO = "[INFO]"
    CHECK = "v"

    @staticmethod
    def init():
        """Initialize symbols based on platform and encoding"""
        # On Windows, always use ASCII symbols due to GBK encoding issues
        # On other platforms, try Unicode symbols
        if os.name != "nt":
            try:
                # Test if we can encode Unicode symbols
                test = "\u2713\u2717\u26a0\u2139"
                test.encode(sys.stdout.encoding or "utf-8")
                Symbols.SUCCESS = "\u2713"  # ✓
                Symbols.ERROR = "\u2717"  # ✗
                Symbols.WARNING = "\u26a0"  # ⚠
                Symbols.INFO = "\u2139"  # ℹ
                Symbols.CHECK = "\u2713"  # ✓
            except (UnicodeEncodeError, AttributeError, LookupError):
                pass  # Keep ASCII symbols


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print a success message"""
    print(f"{Colors.OKGREEN}{Symbols.SUCCESS} {text}{Colors.ENDC}")


def print_error(text: str):
    """Print an error message"""
    print(f"{Colors.FAIL}{Symbols.ERROR} {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print a warning message"""
    print(f"{Colors.WARNING}{Symbols.WARNING} {text}{Colors.ENDC}")


def print_info(text: str):
    """Print an info message"""
    print(f"{Colors.OKCYAN}{Symbols.INFO} {text}{Colors.ENDC}")


def check_environment() -> Tuple[bool, List[str]]:
    """
    Check if the environment meets requirements.

    Returns:
        Tuple of (is_valid, warnings)
    """
    warnings = []
    is_valid = True

    # Check Python version
    if sys.version_info < (3, 12):
        print_error(
            f"Python 3.12 or higher is required. Current version: {sys.version_info.major}.{sys.version_info.minor}"
        )
        is_valid = False
    else:
        print_success(
            f"Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )

    # Check if in virtual environment
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if not in_venv:
        warnings.append("Not running in a virtual environment. Consider using venv or virtualenv.")
        print_warning("Not in a virtual environment (recommended but not required)")
    else:
        print_success("Running in virtual environment")

    # Check for pip
    pip_available = False
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"], capture_output=True, check=True, timeout=5
        )
        print_success("pip is available")
        pip_available = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print_warning("pip is not available")

    # Check for uv (optional but recommended)
    uv_available = False
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, check=True, timeout=5)
        print_success(f"uv is available (faster installation)")
        uv_available = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print_info("uv is not available (optional - pip will be used)")

    # At least one package manager must be available
    if not pip_available and not uv_available:
        print_error("Neither pip nor uv is available - cannot install dependencies")
        is_valid = False
    elif not pip_available and uv_available:
        print_info("Using uv as package manager (pip not required)")

    return is_valid, warnings


def install_dependencies(use_uv: Optional[bool] = None) -> bool:
    """
    Install project dependencies.

    Args:
        use_uv: Force use of uv (True) or pip (False). None = auto-detect.

    Returns:
        True if successful, False otherwise
    """
    print_info("Installing project dependencies...")

    # Auto-detect if not specified
    if use_uv is None:
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True, timeout=5)
            use_uv = True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            use_uv = False

    # Prepare command
    if use_uv:
        cmd = ["uv", "pip", "install", "-e", "."]
        print_info("Using uv for faster installation...")
    else:
        cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
        print_info("Using pip for installation...")

    try:
        # Run installation
        result = subprocess.run(cmd, check=True, timeout=300)
        print_success("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        print_info("Try manually running: pip install -e .")
        return False
    except subprocess.TimeoutExpired:
        print_error("Installation timed out (>5 minutes)")
        return False


def get_subagent_config():
    """Import and return SubagentConfig instance"""
    try:
        from src.mcp_server.tools.subagent_config import get_config

        return get_config()
    except ImportError as e:
        print_error(f"Failed to import SubagentConfig: {e}")
        print_info("Make sure dependencies are installed: pip install -e .")
        return None


def configure_subagent(provider: str, api_key: str, api_base: Optional[str] = None) -> bool:
    """
    Configure Subagent API credentials.

    Args:
        provider: Provider name (openai, anthropic, zhipuai)
        api_key: API key
        api_base: Optional custom API base URL

    Returns:
        True if successful
    """
    config = get_subagent_config()
    if not config:
        return False

    try:
        # Set API key
        config.set_api_key(provider, api_key)
        print_success(f"API key for {provider} configured")

        # Set custom API base if provided
        if api_base:
            config.set_api_base(provider, api_base)
            print_success(f"Custom API base for {provider} configured: {api_base}")

        # Verify configuration was saved
        saved_key = config.get_api_key(provider)
        if saved_key:
            print_success(f"Configuration saved to {config.config_path}")
            return True
        else:
            print_error("Failed to verify configuration")
            return False

    except Exception as e:
        print_error(f"Failed to configure {provider}: {e}")
        return False


def get_provider_info() -> Dict[str, Dict]:
    """Get information about available AI providers"""
    return {
        "openai": {
            "name": "OpenAI",
            "default_base": "https://api.openai.com/v1",
            "key_format": "sk-...",
            "docs": "https://platform.openai.com/docs/api-reference",
        },
        "anthropic": {
            "name": "Anthropic",
            "default_base": "https://api.anthropic.com/v1",
            "key_format": "sk-ant-...",
            "docs": "https://docs.anthropic.com/en/api/getting-started",
        },
        "zhipuai": {
            "name": "ZhipuAI (智谱AI)",
            "default_base": "https://open.bigmodel.cn/api/paas/v4",
            "key_format": "xxxxxxxx.xxxxxxxxxx",
            "docs": "See docs/ZHIPUAI_GUIDE.md",
        },
    }


def select_providers_interactive() -> List[str]:
    """
    Interactively select which providers to configure.

    Returns:
        List of selected provider names
    """
    print_header("Select AI Providers to Configure")

    providers_info = get_provider_info()
    selected = []

    for provider_id, info in providers_info.items():
        print(f"\n{Colors.BOLD}{info['name']}{Colors.ENDC}")
        print(f"  Default API Base: {info['default_base']}")
        print(f"  Key Format: {info['key_format']}")
        print(f"  Documentation: {info['docs']}")

        response = input(f"\nConfigure {info['name']}? (y/n): ").strip().lower()
        if response in ["y", "yes"]:
            selected.append(provider_id)
            print_success(f"{info['name']} selected")
        else:
            print_info(f"{info['name']} skipped")

    return selected


def configure_provider_interactive(provider: str) -> bool:
    """
    Interactively configure a single provider.

    Args:
        provider: Provider name

    Returns:
        True if successful
    """
    providers_info = get_provider_info()
    info = providers_info[provider]

    print(f"\n{Colors.BOLD}Configuring {info['name']}{Colors.ENDC}")
    print(f"Expected key format: {info['key_format']}")

    # Get API key (hidden input)
    api_key = getpass.getpass(f"Enter {info['name']} API Key: ").strip()
    if not api_key:
        print_warning(f"No API key provided for {info['name']}, skipping")
        return False

    # Ask about custom API base
    use_custom = (
        input(f"Use custom API base? (default: {info['default_base']}) (y/n): ").strip().lower()
    )
    api_base = None
    if use_custom in ["y", "yes"]:
        api_base = input("Enter custom API base URL: ").strip()
        if not api_base:
            print_info("Using default API base")
            api_base = None

    # Configure
    return configure_subagent(provider, api_key, api_base)


def configure_claude_desktop() -> bool:
    """
    Configure Claude Desktop integration.

    Returns:
        True if successful
    """
    try:
        from src.mcp_server.cli.config import (
            generate_mcp_config,
            get_claude_config_path,
            save_config,
        )
    except ImportError as e:
        print_error(f"Failed to import CLI config tools: {e}")
        return False

    print_header("Claude Desktop Integration")

    # Detect Claude Desktop config path
    try:
        claude_path = get_claude_config_path()
        if claude_path:
            print_success(f"Found Claude Desktop config: {claude_path}")
        else:
            print_warning("Claude Desktop config not found")
            create_anyway = input("Create configuration file anyway? (y/n): ").strip().lower()
            if create_anyway not in ["y", "yes"]:
                return False
            # Use default path
            if os.name == "nt":
                claude_path = (
                    Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
                )
            else:
                claude_path = (
                    Path.home()
                    / "Library"
                    / "Application Support"
                    / "Claude"
                    / "claude_desktop_config.json"
                )
    except Exception as e:
        print_error(f"Error detecting Claude Desktop: {e}")
        return False

    # Generate MCP config
    try:
        mcp_config = generate_mcp_config()
        print_success("Generated MCP server configuration")
    except Exception as e:
        print_error(f"Failed to generate config: {e}")
        return False

    # Show preview
    print(f"\n{Colors.BOLD}Configuration preview:{Colors.ENDC}")
    print(json.dumps(mcp_config, indent=2))

    # Confirm
    confirm = input(f"\nSave this configuration to {claude_path}? (y/n): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print_info("Claude Desktop configuration cancelled")
        return False

    # Save configuration
    try:
        save_config(mcp_config, str(claude_path))
        print_success(f"Configuration saved to {claude_path}")
        print_warning("Please restart Claude Desktop for changes to take effect")
        return True
    except Exception as e:
        print_error(f"Failed to save configuration: {e}")
        return False


def show_config_summary():
    """Display current configuration summary"""
    config = get_subagent_config()
    if not config:
        return

    print_header("Configuration Summary")

    print(f"{Colors.BOLD}Subagent Configuration:{Colors.ENDC}")
    print(f"  Config file: {config.config_path}")

    providers_info = get_provider_info()
    configured_any = False

    for provider_id, info in providers_info.items():
        api_key = config.get_api_key(provider_id)
        if api_key:
            configured_any = True
            # Mask API key for display
            if len(api_key) > 8:
                masked_key = api_key[:4] + "..." + api_key[-4:]
            else:
                masked_key = "***"

            api_base = config.get_api_base(provider_id)
            print(f"\n  {Colors.OKGREEN}{Symbols.CHECK}{Colors.ENDC} {info['name']}:")
            print(f"      API Key: {masked_key}")
            print(f"      API Base: {api_base}")

    if not configured_any:
        print_info("  No providers configured yet")


def show_next_steps():
    """Display next steps after setup"""
    sep = os.sep

    step_2_details = (
        f"""
    • Configure(the command section should be your own python environment): {Colors.OKCYAN}
"""
        + json.dumps(
            {
                "args": [f"{os.getcwd()}{sep}src{sep}mcp_server{sep}main.py"],
                "command": f"{os.getcwd()}{sep}.venv{sep}Scripts{sep}python.exe",
                "type": "stdio",
            },
            indent=2,
        )
        + f"{Colors.ENDC}\n"
    )

    print_header("Setup Complete!")

    print(f"{Colors.BOLD}Next Steps:{Colors.ENDC}\n")

    print("1. Test your configuration\n")
    print("2. Configure the MCP server to your needs:")
    print(step_2_details)
    print("3. Learn more:")
    print(f"   • Subagent Guide: {Colors.OKCYAN}docs/SUBAGENT_GUIDE.md{Colors.ENDC}")
    print(f"   • Configuration Guide: {Colors.OKCYAN}docs/CONFIGURATION_GUIDE_CN.md{Colors.ENDC}")
    print(f"   • Examples: {Colors.OKCYAN}examples/{Colors.ENDC}\n")

    print("4. If you configured Claude Desktop:")
    print(f"   {Colors.WARNING}Restart Claude Desktop to load the MCP server{Colors.ENDC}\n")


def interactive_setup():
    """Run interactive setup wizard"""
    print_header("MCP Server Setup Wizard")
    print("This wizard will help you configure your MCP server environment.\n")

    # Stage 1: Environment Check
    print_header("Stage 1: Environment Check")
    is_valid, warnings = check_environment()

    if not is_valid:
        print_error("\nEnvironment check failed. Please fix the issues above and try again.")
        return False

    if warnings:
        print_warning("\nWarnings:")
        for warning in warnings:
            print(f"  • {warning}")

    # Stage 2: Dependencies
    print_header("Stage 2: Install Dependencies")
    install_deps = input("Install project dependencies now? (y/n): ").strip().lower()

    if install_deps in ["y", "yes"]:
        if not install_dependencies():
            print_error("\nDependency installation failed.")
            retry = input("Continue anyway? (y/n): ").strip().lower()
            if retry not in ["y", "yes"]:
                return False
    else:
        print_info("Skipping dependency installation")
        print_warning("Make sure to install dependencies later: pip install -e .")

    # Stage 3: Subagent Configuration
    print_header("Stage 3: Configure Subagent API")
    print("Subagent allows Claude to delegate complex tasks to other AI models.")

    configure_subagent_now = (
        input("\nConfigure Subagent API credentials now? (y/n): ").strip().lower()
    )

    if configure_subagent_now in ["y", "yes"]:
        selected_providers = select_providers_interactive()

        if selected_providers:
            success_count = 0
            for provider in selected_providers:
                if configure_provider_interactive(provider):
                    success_count += 1

            print(
                f"\n{Colors.OKGREEN}Configured {success_count}/{len(selected_providers)} providers{Colors.ENDC}"
            )
        else:
            print_info("No providers selected")
    else:
        print_info("Skipping Subagent configuration")
        print_info("You can configure it later by running this script again")

    # Show current configuration
    show_config_summary()

    # Stage 4: Claude Desktop Integration
    print_header("Stage 4: Claude Desktop Integration")
    print("Configure Claude Desktop to use this MCP server.")

    configure_claude = input("\nConfigure Claude Desktop now? (y/n): ").strip().lower()

    if configure_claude in ["y", "yes"]:
        configure_claude_desktop()
    else:
        print_info("Skipping Claude Desktop configuration")
        print_info("You can configure it later with: python -m mcp_server.cli.config --claude")

    # Show next steps
    show_next_steps()

    return True


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="MCP Server Setup - Configure environment and API credentials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    uv run configure.py
  
  Configure OpenAI only:
    uv run configure.py --provider openai --api-key sk-xxx
  
  Configure multiple providers:
    uv run configure.py --provider openai --api-key sk-xxx \
                        --provider anthropic --api-key sk-ant-xxx
  
  Skip dependency installation:
    uv run configure.py --skip-deps
  
  Full non-interactive setup:
    uv run configure.py --provider openai --api-key sk-xxx --skip-claude
        """,
    )

    # Global options
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument(
        "--skip-claude", action="store_true", help="Skip Claude Desktop configuration"
    )
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")

    # Provider configuration (can be repeated)
    parser.add_argument(
        "--provider",
        action="append",
        dest="providers",
        choices=["openai", "anthropic", "zhipuai"],
        help="AI provider to configure (can be repeated)",
    )
    parser.add_argument(
        "--api-key",
        action="append",
        dest="api_keys",
        help="API key for the provider (must match order of --provider)",
    )
    parser.add_argument(
        "--api-base",
        action="append",
        dest="api_bases",
        help="Custom API base URL (optional, must match order of --provider)",
    )

    args = parser.parse_args()

    # Validate provider/key pairing
    if args.providers and args.api_keys:
        if len(args.providers) != len(args.api_keys):
            parser.error("Number of --provider and --api-key arguments must match")
    elif args.providers and not args.api_keys:
        parser.error("--api-key required when --provider is specified")
    elif args.api_keys and not args.providers:
        parser.error("--provider required when --api-key is specified")

    # Validate api_bases length if provided
    if args.api_bases and args.providers:
        if len(args.api_bases) != len(args.providers):
            parser.error("Number of --api-base arguments must match --provider arguments")

    return args


def noninteractive_setup(args):
    """
    Run non-interactive setup based on command line arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        True if successful
    """
    print_header("MCP Server Setup (Non-Interactive Mode)")

    # Environment check (always run)
    print_info("Checking environment...")
    is_valid, warnings = check_environment()

    if not is_valid:
        print_error("Environment check failed")
        return False

    # Dependencies
    if not args.skip_deps:
        print_info("Installing dependencies...")
        if not install_dependencies():
            print_error("Dependency installation failed")
            return False
    else:
        print_info("Skipping dependency installation (--skip-deps)")

    # Subagent configuration
    if args.providers:
        print_info(f"Configuring {len(args.providers)} provider(s)...")
        success_count = 0

        for i, provider in enumerate(args.providers):
            api_key = args.api_keys[i]
            api_base = args.api_bases[i] if args.api_bases else None

            if configure_subagent(provider, api_key, api_base):
                success_count += 1

        print_success(f"Configured {success_count}/{len(args.providers)} providers")

        if success_count < len(args.providers):
            print_warning("Some providers failed to configure")

    # Show configuration
    show_config_summary()

    # Claude Desktop
    if not args.skip_claude:
        print_info("Configuring Claude Desktop...")
        configure_claude_desktop()
    else:
        print_info("Skipping Claude Desktop configuration (--skip-claude)")

    print_success("\nSetup completed!")
    return True


def main():
    """Main entry point"""
    try:
        # Initialize symbols for platform
        Symbols.init()

        # Parse arguments first to check for --no-color
        args = parse_arguments()

        # Disable colors if requested
        if args.no_color:
            Colors.strip_all()

        # Determine mode
        has_provider_args = args.providers is not None

        if has_provider_args or args.skip_deps or args.skip_claude:
            # Non-interactive mode
            success = noninteractive_setup(args)
        else:
            # Interactive mode
            success = interactive_setup()

        return 0 if success else 1

    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup cancelled by user{Colors.ENDC}")
        return 130
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
