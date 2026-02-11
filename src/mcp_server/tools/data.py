"""
Data processing tools for the MCP server.

Provides tools for:
- JSON parsing, formatting, and manipulation
- CSV parsing and conversion
- XML to JSON conversion
- YAML parsing and conversion
- TOML parsing and conversion
- Data validation and querying
"""

import json
import csv
import io
import sys
from typing import Any, Optional
import xml.etree.ElementTree as ET

from .utils import logger, DataProcessingError, ValidationError

# Import YAML support
try:
    import yaml
except ImportError:
    yaml = None

# Import TOML support (Python 3.11+ has built-in tomllib)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# Module metadata
CATEGORY_NAME = "Data Processing"
CATEGORY_DESCRIPTION = "JSON, CSV, XML, YAML, TOML parsing and manipulation"
TOOLS = [
    "parse_json",
    "format_json",
    "json_query",
    "csv_to_json",
    "json_to_csv",
    "parse_csv",
    "validate_json_schema",
    "flatten_json",
    "merge_json",
    "xml_to_json",
    "parse_yaml",
    "yaml_to_json",
    "json_to_yaml",
    "parse_toml",
    "toml_to_json",
]


def register_tools(mcp):
    """Register all data processing tools with the MCP server."""

    @mcp.tool()
    def parse_json(json_string: str) -> str:
        """
        Parse and validate a JSON string.

        Args:
            json_string: JSON string to parse

        Returns:
            Formatted JSON string if valid, or error message
        """
        try:
            data = json.loads(json_string)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            return f'{{"error": "Invalid JSON: {str(e)}"}}'

    @mcp.tool()
    def format_json(json_string: str, indent: int = 2, sort_keys: bool = False) -> str:
        """
        Format JSON with pretty printing.

        Args:
            json_string: JSON string to format
            indent: Number of spaces for indentation (default: 2)
            sort_keys: Whether to sort object keys (default: False)

        Returns:
            Formatted JSON string
        """
        try:
            data = json.loads(json_string)
            return json.dumps(
                data, indent=indent, sort_keys=sort_keys, ensure_ascii=False
            )
        except json.JSONDecodeError as e:
            return f'{{"error": "Invalid JSON: {str(e)}"}}'

    @mcp.tool()
    def json_query(json_string: str, path: str) -> str:
        """
        Extract value from JSON using dot notation path.

        Args:
            json_string: JSON string to query
            path: Dot-separated path (e.g., "user.name" or "items.0.title")

        Returns:
            JSON string containing extracted value
        """
        try:
            data = json.loads(json_string)

            # Navigate the path
            parts = path.split(".")
            current = data

            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                elif isinstance(current, list):
                    try:
                        index = int(part)
                        current = current[index]
                    except (ValueError, IndexError):
                        return f'{{"error": "Invalid array index: {part}"}}'
                else:
                    return f'{{"error": "Cannot navigate path at: {part}"}}'

                if current is None:
                    return f'{{"error": "Path not found: {path}"}}'

            return json.dumps(
                {"path": path, "value": current}, indent=2, ensure_ascii=False
            )

        except json.JSONDecodeError as e:
            return f'{{"error": "Invalid JSON: {str(e)}"}}'
        except Exception as e:
            return f'{{"error": "Query failed: {str(e)}"}}'

    @mcp.tool()
    def csv_to_json(
        csv_string: str, delimiter: str = ",", has_header: bool = True
    ) -> str:
        """
        Convert CSV data to JSON.

        Args:
            csv_string: CSV string to convert
            delimiter: CSV delimiter (default: ,)
            has_header: Whether first row is header (default: True)

        Returns:
            JSON string with array of objects
        """
        try:
            reader = csv.reader(io.StringIO(csv_string), delimiter=delimiter)
            rows = list(reader)

            if not rows:
                return '{"data": [], "count": 0}'

            if has_header:
                headers = rows[0]
                data = []
                for row in rows[1:]:
                    obj = {}
                    for i, header in enumerate(headers):
                        obj[header] = row[i] if i < len(row) else ""
                    data.append(obj)
            else:
                data = [
                    {"col_" + str(i): val for i, val in enumerate(row)} for row in rows
                ]

            return json.dumps(
                {"data": data, "count": len(data)}, indent=2, ensure_ascii=False
            )

        except Exception as e:
            logger.error(f"CSV to JSON conversion failed: {e}")
            return f'{{"error": "Conversion failed: {str(e)}"}}'

    @mcp.tool()
    def json_to_csv(json_string: str) -> str:
        """
        Convert JSON array to CSV format.

        Args:
            json_string: JSON string (must be array of objects)

        Returns:
            CSV string with headers
        """
        try:
            data = json.loads(json_string)

            if not isinstance(data, list):
                return "Error: JSON must be an array of objects"

            if not data:
                return ""

            # Get all unique keys from all objects
            keys = set()
            for item in data:
                if isinstance(item, dict):
                    keys.update(item.keys())

            keys = sorted(keys)

            # Create CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=keys)
            writer.writeheader()

            for item in data:
                if isinstance(item, dict):
                    writer.writerow(item)

            return output.getvalue()

        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON: {str(e)}"
        except Exception as e:
            logger.error(f"JSON to CSV conversion failed: {e}")
            return f"Error: Conversion failed: {str(e)}"

    @mcp.tool()
    def parse_csv(csv_string: str, delimiter: str = ",") -> str:
        """
        Parse CSV data and return as JSON.

        Args:
            csv_string: CSV string to parse
            delimiter: CSV delimiter (default: ,)

        Returns:
            JSON string containing parsed data
        """
        try:
            reader = csv.DictReader(io.StringIO(csv_string), delimiter=delimiter)
            data = list(reader)

            return json.dumps(
                {
                    "data": data,
                    "count": len(data),
                    "columns": reader.fieldnames if reader.fieldnames else [],
                },
                indent=2,
                ensure_ascii=False,
            )

        except Exception as e:
            logger.error(f"CSV parsing failed: {e}")
            return f'{{"error": "CSV parsing failed: {str(e)}"}}'

    @mcp.tool()
    def validate_json_schema(json_string: str) -> str:
        """
        Validate JSON syntax and structure.

        Args:
            json_string: JSON string to validate

        Returns:
            Validation result with details
        """
        try:
            data = json.loads(json_string)

            def analyze_structure(obj, depth=0):
                if isinstance(obj, dict):
                    return {"type": "object", "keys": len(obj), "depth": depth}
                elif isinstance(obj, list):
                    return {"type": "array", "length": len(obj), "depth": depth}
                elif isinstance(obj, str):
                    return {"type": "string", "length": len(obj)}
                elif isinstance(obj, (int, float)):
                    return {"type": "number", "value_type": type(obj).__name__}
                elif isinstance(obj, bool):
                    return {"type": "boolean"}
                elif obj is None:
                    return {"type": "null"}
                else:
                    return {"type": "unknown"}

            structure = analyze_structure(data)

            return json.dumps(
                {"valid": True, "structure": structure, "size_bytes": len(json_string)},
                indent=2,
            )

        except json.JSONDecodeError as e:
            return json.dumps(
                {
                    "valid": False,
                    "error": str(e),
                    "position": e.pos if hasattr(e, "pos") else None,
                },
                indent=2,
            )

    @mcp.tool()
    def flatten_json(json_string: str, separator: str = ".") -> str:
        """
        Flatten nested JSON object into single-level object.

        Args:
            json_string: JSON string to flatten
            separator: Separator for nested keys (default: .)

        Returns:
            Flattened JSON string
        """
        try:
            data = json.loads(json_string)

            def flatten(obj, parent_key=""):
                items = []
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        new_key = f"{parent_key}{separator}{k}" if parent_key else k
                        if isinstance(v, (dict, list)):
                            items.extend(flatten(v, new_key).items())
                        else:
                            items.append((new_key, v))
                elif isinstance(obj, list):
                    for i, v in enumerate(obj):
                        new_key = (
                            f"{parent_key}{separator}{i}" if parent_key else str(i)
                        )
                        if isinstance(v, (dict, list)):
                            items.extend(flatten(v, new_key).items())
                        else:
                            items.append((new_key, v))
                else:
                    items.append((parent_key, obj))
                return dict(items)

            flattened = flatten(data)
            return json.dumps(flattened, indent=2, ensure_ascii=False)

        except json.JSONDecodeError as e:
            return f'{{"error": "Invalid JSON: {str(e)}"}}'
        except Exception as e:
            return f'{{"error": "Flattening failed: {str(e)}"}}'

    @mcp.tool()
    def merge_json(json_string1: str, json_string2: str, deep: bool = True) -> str:
        """
        Merge two JSON objects.

        Args:
            json_string1: First JSON string
            json_string2: Second JSON string (takes precedence)
            deep: Deep merge nested objects (default: True)

        Returns:
            Merged JSON string
        """
        try:
            data1 = json.loads(json_string1)
            data2 = json.loads(json_string2)

            if not isinstance(data1, dict) or not isinstance(data2, dict):
                return '{"error": "Both JSON inputs must be objects"}'

            def deep_merge(dict1, dict2):
                result = dict1.copy()
                for key, value in dict2.items():
                    if (
                        key in result
                        and isinstance(result[key], dict)
                        and isinstance(value, dict)
                    ):
                        result[key] = deep_merge(result[key], value)
                    else:
                        result[key] = value
                return result

            if deep:
                merged = deep_merge(data1, data2)
            else:
                merged = {**data1, **data2}

            return json.dumps(merged, indent=2, ensure_ascii=False)

        except json.JSONDecodeError as e:
            return f'{{"error": "Invalid JSON: {str(e)}"}}'
        except Exception as e:
            return f'{{"error": "Merge failed: {str(e)}"}}'

    @mcp.tool()
    def xml_to_json(xml_string: str) -> str:
        """
        Convert XML to JSON format.

        Args:
            xml_string: XML string to convert

        Returns:
            JSON string representation of XML
        """
        try:
            root = ET.fromstring(xml_string)

            def element_to_dict(element):
                result = {}

                # Add attributes
                if element.attrib:
                    result["@attributes"] = element.attrib

                # Add text content
                if element.text and element.text.strip():
                    result["text"] = element.text.strip()

                # Add children
                children = {}
                for child in element:
                    child_data = element_to_dict(child)
                    if child.tag in children:
                        # Multiple children with same tag - make it a list
                        if not isinstance(children[child.tag], list):
                            children[child.tag] = [children[child.tag]]
                        children[child.tag].append(child_data)
                    else:
                        children[child.tag] = child_data

                if children:
                    result.update(children)

                # If only text content, return just the text
                if len(result) == 1 and "text" in result:
                    return result["text"]

                return result if result else element.text

            converted = {root.tag: element_to_dict(root)}
            return json.dumps(converted, indent=2, ensure_ascii=False)

        except ET.ParseError as e:
            return f'{{"error": "Invalid XML: {str(e)}"}}'
        except Exception as e:
            logger.error(f"XML to JSON conversion failed: {e}")
            return f'{{"error": "Conversion failed: {str(e)}"}}'

    @mcp.tool()
    def parse_yaml(yaml_string: str) -> str:
        """
        Parse YAML string to JSON.

        Args:
            yaml_string: YAML string to parse

        Returns:
            JSON string representation of YAML data
        """
        if yaml is None:
            return json.dumps({"error": "YAML support not available. Install pyyaml."})

        try:
            data = yaml.safe_load(yaml_string)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing failed: {e}")
            return json.dumps({"error": f"Invalid YAML: {str(e)}"})
        except Exception as e:
            logger.error(f"YAML parsing error: {e}")
            return json.dumps({"error": f"Parsing failed: {str(e)}"})

    @mcp.tool()
    def yaml_to_json(yaml_string: str, indent: int = 2) -> str:
        """
        Convert YAML to formatted JSON.

        Args:
            yaml_string: YAML string to convert
            indent: JSON indentation level (default: 2)

        Returns:
            Formatted JSON string
        """
        if yaml is None:
            return json.dumps({"error": "YAML support not available. Install pyyaml."})

        try:
            data = yaml.safe_load(yaml_string)
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except yaml.YAMLError as e:
            logger.error(f"YAML to JSON conversion failed: {e}")
            return json.dumps({"error": f"Invalid YAML: {str(e)}"})
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return json.dumps({"error": f"Conversion failed: {str(e)}"})

    @mcp.tool()
    def json_to_yaml(json_string: str) -> str:
        """
        Convert JSON to YAML format.

        Args:
            json_string: JSON string to convert

        Returns:
            YAML string
        """
        if yaml is None:
            return "Error: YAML support not available. Install pyyaml."

        try:
            data = json.loads(json_string)
            return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            return f"Error: Invalid JSON: {str(e)}"
        except Exception as e:
            logger.error(f"JSON to YAML conversion failed: {e}")
            return f"Error: Conversion failed: {str(e)}"

    @mcp.tool()
    def parse_toml(toml_string: str) -> str:
        """
        Parse TOML configuration file to JSON.

        Args:
            toml_string: TOML string to parse

        Returns:
            JSON string representation of TOML data
        """
        if tomllib is None:
            return json.dumps({"error": "TOML support not available. Install tomli or use Python 3.11+."})

        try:
            data = tomllib.loads(toml_string)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"TOML parsing failed: {e}")
            return json.dumps({"error": f"Invalid TOML: {str(e)}"})

    @mcp.tool()
    def toml_to_json(toml_string: str, indent: int = 2) -> str:
        """
        Convert TOML to formatted JSON.

        Args:
            toml_string: TOML string to convert
            indent: JSON indentation level (default: 2)

        Returns:
            Formatted JSON string
        """
        if tomllib is None:
            return json.dumps({"error": "TOML support not available. Install tomli or use Python 3.11+."})

        try:
            data = tomllib.loads(toml_string)
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except Exception as e:
            logger.error(f"TOML to JSON conversion failed: {e}")
            return json.dumps({"error": f"Invalid TOML: {str(e)}"})
