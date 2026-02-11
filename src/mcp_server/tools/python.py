"""
Python Development Tools

Provides tools for Python code execution, syntax validation, AST analysis,
and module introspection.
"""

import ast
import json
import sys
from pathlib import Path

from .command_executor import CommandExecutor
from .utils import (
    CommandExecutionError,
    PYTHON_MAX_CODE_LENGTH,
    ValidationError,
    logger,
)

# Module metadata
CATEGORY_NAME = "Python Development"
CATEGORY_DESCRIPTION = "Code execution, syntax validation, AST analysis, module introspection"
TOOLS = [
    "python_execute_code",
    "python_validate_syntax",
    "python_parse_ast",
    "python_get_module_info",
    "python_list_packages",
    "python_format_code",
    "python_analyze_imports",
    "python_get_version",
]


def register_tools(mcp):
    """Register all Python development tools."""

    executor = CommandExecutor()

    @mcp.tool()
    def python_execute_code(
        code: str,
        timeout: int = 30,
        safe_mode: bool = True,
    ) -> str:
        """Execute Python code in isolated subprocess.

        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds (default: 30, max: 300)
            safe_mode: If True, block dangerous imports (os, subprocess, sys, etc.)

        Returns:
            JSON string with execution results (stdout, stderr, returncode, execution_time)
        """
        import tempfile
        import os

        temp_file = None
        try:
            # Validate code length
            if len(code) > PYTHON_MAX_CODE_LENGTH:
                return json.dumps({
                    "error": f"Code too long: {len(code)} bytes (max: {PYTHON_MAX_CODE_LENGTH})"
                })

            # Safe mode: check for dangerous imports
            if safe_mode:
                dangerous_modules = ["os", "subprocess", "sys", "shutil", "__import__"]
                for module in dangerous_modules:
                    if f"import {module}" in code or f"from {module}" in code:
                        return json.dumps({
                            "error": f"Dangerous import blocked in safe mode: {module}"
                        })

            # Create temporary file for code execution
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name

            # Execute code using temporary file
            result = executor.execute(
                "python",
                [temp_file],
                timeout=timeout,
            )

            return json.dumps({
                "success": result["success"],
                "returncode": result["returncode"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "execution_time": result["execution_time"],
            })

        except Exception as e:
            logger.error(f"python_execute_code failed: {e}")
            return json.dumps({"error": str(e)})
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {temp_file}: {e}")

    @mcp.tool()
    def python_validate_syntax(code: str, filename: str = "<string>") -> str:
        """Validate Python code syntax without executing.

        Args:
            code: Python code to validate
            filename: Filename for error messages (default: "<string>")

        Returns:
            JSON string with validation result (valid, error_message, line_number)
        """
        try:
            # Try to parse the code
            ast.parse(code, filename=filename)

            return json.dumps({
                "valid": True,
                "message": "Syntax is valid",
            })

        except SyntaxError as e:
            return json.dumps({
                "valid": False,
                "error_message": str(e.msg),
                "line_number": e.lineno,
                "offset": e.offset,
                "text": e.text,
            })

        except Exception as e:
            logger.error(f"python_validate_syntax failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def python_parse_ast(code: str, include_details: bool = True) -> str:
        """Parse Python code and return Abstract Syntax Tree structure.

        Args:
            code: Python code to parse
            include_details: Include detailed AST structure (default: True)

        Returns:
            JSON string with AST structure, functions, classes, and imports
        """
        try:
            # Parse the code
            tree = ast.parse(code)

            # Extract functions
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                    })

            # Extract classes
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [
                        n.name for n in node.body
                        if isinstance(n, ast.FunctionDef)
                    ]
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": methods,
                    })

            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                        })
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append({
                            "type": "from",
                            "module": node.module,
                            "name": alias.name,
                            "alias": alias.asname,
                        })

            result = {
                "functions": functions,
                "classes": classes,
                "imports": imports,
            }

            if include_details:
                result["ast_dump"] = ast.dump(tree, indent=2)

            return json.dumps(result)

        except SyntaxError as e:
            return json.dumps({
                "error": "Syntax error",
                "message": str(e.msg),
                "line": e.lineno,
            })

        except Exception as e:
            logger.error(f"python_parse_ast failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def python_get_module_info(module_name: str) -> str:
        """Get information about a Python module.

        Args:
            module_name: Name of the module to inspect

        Returns:
            JSON string with module version, path, and exported items
        """
        try:
            import importlib
            import inspect

            # Import the module
            module = importlib.import_module(module_name)

            # Get module info
            info = {
                "name": module_name,
                "file": getattr(module, "__file__", None),
                "version": getattr(module, "__version__", None),
                "doc": getattr(module, "__doc__", None),
            }

            # Get exported functions and classes
            functions = []
            classes = []

            for name, obj in inspect.getmembers(module):
                if not name.startswith("_"):
                    if inspect.isfunction(obj):
                        functions.append(name)
                    elif inspect.isclass(obj):
                        classes.append(name)

            info["functions"] = functions[:20]  # Limit to first 20
            info["classes"] = classes[:20]  # Limit to first 20

            return json.dumps(info)

        except ImportError as e:
            return json.dumps({
                "error": f"Module not found: {module_name}",
                "message": str(e),
            })

        except Exception as e:
            logger.error(f"python_get_module_info failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def python_list_packages(filter_pattern: str = "") -> str:
        """List installed Python packages.

        Args:
            filter_pattern: Optional substring to filter package names (case-insensitive)

        Returns:
            JSON string with list of packages (name, version)
        """
        try:
            # Execute uv pip list --format=json (faster and more reliable than python -m pip)
            result = executor.execute(
                "uv",
                ["pip", "list", "--format=json"],
                timeout=60,
            )

            if not result["success"]:
                return json.dumps({
                    "error": "Failed to list packages",
                    "stderr": result["stderr"],
                })

            # Parse JSON output
            packages = json.loads(result["stdout"])

            # Filter if pattern provided
            if filter_pattern:
                pattern_lower = filter_pattern.lower()
                packages = [
                    pkg for pkg in packages
                    if pattern_lower in pkg["name"].lower()
                ]

            return json.dumps({
                "packages": packages,
                "count": len(packages),
            })

        except Exception as e:
            logger.error(f"python_list_packages failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def python_analyze_imports(code: str) -> str:
        """Analyze import statements in Python code.

        Args:
            code: Python code to analyze

        Returns:
            JSON string with categorized imports (stdlib, third_party, local)
        """
        try:
            # Parse the code
            tree = ast.parse(code)

            # Standard library modules (common ones)
            stdlib_modules = {
                "os", "sys", "re", "json", "time", "datetime", "pathlib",
                "collections", "itertools", "functools", "typing", "subprocess",
                "logging", "argparse", "unittest", "math", "random", "string",
                "io", "shutil", "tempfile", "glob", "pickle", "csv", "xml",
                "http", "urllib", "socket", "threading", "multiprocessing",
            }

            stdlib_imports = []
            third_party_imports = []
            local_imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split(".")[0]
                        import_info = {
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        }

                        if module_name in stdlib_modules:
                            stdlib_imports.append(import_info)
                        elif module_name.startswith("."):
                            local_imports.append(import_info)
                        else:
                            third_party_imports.append(import_info)

                elif isinstance(node, ast.ImportFrom):
                    module_name = (node.module or "").split(".")[0]
                    for alias in node.names:
                        import_info = {
                            "module": node.module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        }

                        if node.level > 0:  # Relative import
                            local_imports.append(import_info)
                        elif module_name in stdlib_modules:
                            stdlib_imports.append(import_info)
                        else:
                            third_party_imports.append(import_info)

            return json.dumps({
                "stdlib": stdlib_imports,
                "third_party": third_party_imports,
                "local": local_imports,
                "total": len(stdlib_imports) + len(third_party_imports) + len(local_imports),
            })

        except SyntaxError as e:
            return json.dumps({
                "error": "Syntax error",
                "message": str(e.msg),
                "line": e.lineno,
            })

        except Exception as e:
            logger.error(f"python_analyze_imports failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def python_format_code(code: str, style: str = "black") -> str:
        """Format Python code using black or autopep8.

        Args:
            code: Python code to format
            style: Formatter to use - "black" or "autopep8" (default: "black")

        Returns:
            JSON string with formatted code or error
        """
        try:
            if style not in ["black", "autopep8"]:
                return json.dumps({
                    "error": f"Invalid style: {style}. Use 'black' or 'autopep8'"
                })

            # Try to format using the specified tool
            if style == "black":
                result = executor.execute(
                    "python",
                    ["-m", "black", "-", "--quiet"],
                    timeout=30,
                )
            else:  # autopep8
                result = executor.execute(
                    "python",
                    ["-m", "autopep8", "-"],
                    timeout=30,
                )

            if result["success"]:
                return json.dumps({
                    "formatted_code": result["stdout"],
                    "style": style,
                })
            else:
                # Formatter not installed, return original code with warning
                return json.dumps({
                    "formatted_code": code,
                    "warning": f"{style} not installed. Install with: pip install {style}",
                    "stderr": result["stderr"],
                })

        except Exception as e:
            logger.error(f"python_format_code failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def python_get_version() -> str:
        """Get Python version and implementation information.

        Returns:
            JSON string with Python version, implementation, and path
        """
        try:
            # Execute python --version
            result = executor.execute(
                "python",
                ["--version"],
                timeout=10,
            )

            # Get version from stdout or stderr (Python 2 uses stderr)
            version_output = result["stdout"] or result["stderr"]

            # Get additional info from sys module
            python_info = {
                "version": version_output.strip(),
                "version_info": {
                    "major": sys.version_info.major,
                    "minor": sys.version_info.minor,
                    "micro": sys.version_info.micro,
                },
                "implementation": sys.implementation.name,
                "executable": sys.executable,
                "platform": sys.platform,
            }

            return json.dumps(python_info)

        except Exception as e:
            logger.error(f"python_get_version failed: {e}")
            return json.dumps({"error": str(e)})
