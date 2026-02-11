"""
Utility tools for the MCP server.

Provides tools for:
- UUID generation
- Hash generation (MD5, SHA256, etc.)
- Date and time operations
- Mathematical calculations
- Random string generation
- Password generation and strength checking
"""

import hashlib
import uuid
import random
import string
import secrets
from datetime import datetime, timedelta
from typing import Optional

from dateutil import parser as date_parser

from .utils import logger, ValidationError

# Module metadata
CATEGORY_NAME = "Utilities"
CATEGORY_DESCRIPTION = "UUID, hashing, date/time operations, math, password generation"
TOOLS = [
    "generate_uuid",
    "generate_hash",
    "timestamp_to_date",
    "date_to_timestamp",
    "calculate_date_diff",
    "format_date",
    "calculate_expression",
    "generate_random_string",
    "generate_password",
    "check_password_strength",
]


def register_tools(mcp):
    """Register all utility tools with the MCP server."""

    @mcp.tool()
    def generate_uuid(version: int = 4, uppercase: bool = False) -> str:
        """
        Generate a UUID.

        Args:
            version: UUID version (1 or 4, default: 4)
            uppercase: Return uppercase UUID (default: False)

        Returns:
            UUID string
        """
        try:
            if version == 1:
                result = str(uuid.uuid1())
            elif version == 4:
                result = str(uuid.uuid4())
            else:
                return f"Error: Unsupported UUID version: {version}. Use 1 or 4."

            return result.upper() if uppercase else result

        except Exception as e:
            logger.error(f"UUID generation failed: {e}")
            return f"Error: UUID generation failed: {str(e)}"

    @mcp.tool()
    def generate_hash(
        text: str, algorithm: str = "sha256", encoding: str = "utf-8"
    ) -> str:
        """
        Generate hash of text using specified algorithm.

        Args:
            text: Text to hash
            algorithm: Hash algorithm - md5, sha1, sha256, sha512 (default: sha256)
            encoding: Text encoding (default: utf-8)

        Returns:
            Hexadecimal hash string
        """
        try:
            algorithm = algorithm.lower()

            if algorithm == "md5":
                hasher = hashlib.md5()
            elif algorithm == "sha1":
                hasher = hashlib.sha1()
            elif algorithm == "sha256":
                hasher = hashlib.sha256()
            elif algorithm == "sha512":
                hasher = hashlib.sha512()
            else:
                return f"Error: Unsupported algorithm: {algorithm}. Use md5, sha1, sha256, or sha512."

            hasher.update(text.encode(encoding))

            import json

            return json.dumps(
                {
                    "algorithm": algorithm,
                    "hash": hasher.hexdigest(),
                    "length": len(hasher.hexdigest()),
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Hash generation failed: {e}")
            return f'{{"error": "Hash generation failed: {str(e)}"}}'

    @mcp.tool()
    def timestamp_to_date(
        timestamp: float, format: str = "iso", timezone: str = "local"
    ) -> str:
        """
        Convert Unix timestamp to readable date.

        Args:
            timestamp: Unix timestamp (seconds since epoch)
            format: Output format - 'iso', 'readable', or custom strftime format (default: iso)
            timezone: 'local' or 'utc' (default: local)

        Returns:
            Formatted date string
        """
        try:
            from datetime import timezone as tz

            if timezone.lower() == "utc":
                dt = datetime.fromtimestamp(timestamp, tz.utc)
            else:
                dt = datetime.fromtimestamp(timestamp)

            if format == "iso":
                result = dt.isoformat()
            elif format == "readable":
                result = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Custom format
                result = dt.strftime(format)

            import json

            return json.dumps(
                {
                    "timestamp": timestamp,
                    "formatted": result,
                    "timezone": timezone,
                    "iso": dt.isoformat(),
                    "readable": dt.strftime("%Y-%m-%d %H:%M:%S"),
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Timestamp conversion failed: {e}")
            return f'{{"error": "Timestamp conversion failed: {str(e)}"}}'

    @mcp.tool()
    def date_to_timestamp(date_string: str, timezone: str = "local") -> str:
        """
        Convert date string to Unix timestamp.

        Args:
            date_string: Date string to convert (various formats supported)
            timezone: 'local' or 'utc' (default: local)

        Returns:
            JSON string with timestamp and parsed date info
        """
        try:
            # Parse date string (supports many formats)
            dt = date_parser.parse(date_string)

            # Convert to timestamp
            timestamp = dt.timestamp()

            import json

            return json.dumps(
                {
                    "input": date_string,
                    "timestamp": timestamp,
                    "iso": dt.isoformat(),
                    "readable": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "year": dt.year,
                    "month": dt.month,
                    "day": dt.day,
                    "hour": dt.hour,
                    "minute": dt.minute,
                    "second": dt.second,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Date parsing failed: {e}")
            return f'{{"error": "Date parsing failed: {str(e)}. Use ISO format or common date formats."}}'

    @mcp.tool()
    def calculate_date_diff(date1: str, date2: str, unit: str = "days") -> str:
        """
        Calculate difference between two dates.

        Args:
            date1: First date string
            date2: Second date string
            unit: Unit for difference - 'days', 'hours', 'minutes', 'seconds' (default: days)

        Returns:
            JSON string with difference in various units
        """
        try:
            dt1 = date_parser.parse(date1)
            dt2 = date_parser.parse(date2)

            diff = dt2 - dt1

            # Calculate in different units
            total_seconds = diff.total_seconds()

            result = {
                "date1": dt1.isoformat(),
                "date2": dt2.isoformat(),
                "difference": {
                    "days": diff.days,
                    "seconds": diff.seconds,
                    "total_seconds": total_seconds,
                    "total_minutes": total_seconds / 60,
                    "total_hours": total_seconds / 3600,
                    "total_days": diff.total_seconds() / 86400,
                },
            }

            if unit == "days":
                result["result"] = diff.total_seconds() / 86400
            elif unit == "hours":
                result["result"] = total_seconds / 3600
            elif unit == "minutes":
                result["result"] = total_seconds / 60
            elif unit == "seconds":
                result["result"] = total_seconds
            else:
                result["error"] = f"Unknown unit: {unit}"

            result["unit"] = unit

            import json

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Date difference calculation failed: {e}")
            return f'{{"error": "Date difference calculation failed: {str(e)}"}}'

    @mcp.tool()
    def format_date(date_string: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Format a date string using custom format.

        Args:
            date_string: Date string to format
            format: strftime format string (default: %Y-%m-%d %H:%M:%S)

        Returns:
            Formatted date string
        """
        try:
            dt = date_parser.parse(date_string)
            formatted = dt.strftime(format)

            import json

            return json.dumps(
                {
                    "input": date_string,
                    "format": format,
                    "output": formatted,
                    "examples": {
                        "iso": dt.isoformat(),
                        "us_date": dt.strftime("%m/%d/%Y"),
                        "eu_date": dt.strftime("%d/%m/%Y"),
                        "time_12h": dt.strftime("%I:%M:%S %p"),
                        "time_24h": dt.strftime("%H:%M:%S"),
                    },
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Date formatting failed: {e}")
            return f'{{"error": "Date formatting failed: {str(e)}"}}'

    @mcp.tool()
    def calculate_expression(expression: str) -> str:
        """
        Safely evaluate a mathematical expression.

        Args:
            expression: Mathematical expression to evaluate (supports +, -, *, /, **, (), basic math functions)

        Returns:
            JSON string with result
        """
        try:
            import math
            import re

            # Security: Only allow safe characters
            if not re.match(r"^[0-9+\-*/(). ,pietan\^]+$", expression.lower()):
                return '{"error": "Expression contains invalid characters. Only numbers, operators, and basic math functions allowed."}'

            # Replace common patterns
            safe_expr = expression.replace("^", "**")

            # Create safe namespace with math functions
            safe_dict = {
                "abs": abs,
                "round": round,
                "max": max,
                "min": min,
                "pow": pow,
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "pi": math.pi,
                "e": math.e,
            }

            result = eval(safe_expr, {"__builtins__": {}}, safe_dict)

            import json

            return json.dumps(
                {
                    "expression": expression,
                    "result": result,
                    "type": type(result).__name__,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Expression evaluation failed: {e}")
            return f'{{"error": "Evaluation failed: {str(e)}"}}'

    @mcp.tool()
    def generate_random_string(length: int = 16, charset: str = "alphanumeric") -> str:
        """
        Generate a random string.

        Args:
            length: Length of string to generate (default: 16)
            charset: Character set - 'alphanumeric', 'letters', 'digits', 'hex', 'ascii' (default: alphanumeric)

        Returns:
            Random string
        """
        try:
            if length <= 0:
                return "Error: Length must be positive"

            if length > 10000:
                return "Error: Length too large (max: 10000)"

            charset = charset.lower()

            if charset == "alphanumeric":
                chars = string.ascii_letters + string.digits
            elif charset == "letters":
                chars = string.ascii_letters
            elif charset == "digits":
                chars = string.digits
            elif charset == "hex":
                chars = string.hexdigits.lower()[:16]  # 0-9a-f
            elif charset == "ascii":
                chars = string.ascii_letters + string.digits + string.punctuation
            else:
                return f"Error: Unknown charset: {charset}. Use alphanumeric, letters, digits, hex, or ascii."

            result = "".join(random.choice(chars) for _ in range(length))

            import json

            return json.dumps(
                {"string": result, "length": len(result), "charset": charset}, indent=2
            )

        except Exception as e:
            logger.error(f"Random string generation failed: {e}")
            return f'{{"error": "Generation failed: {str(e)}"}}'

    @mcp.tool()
    def generate_password(
        length: int = 16,
        include_symbols: bool = True,
        include_numbers: bool = True,
        exclude_ambiguous: bool = True,
    ) -> str:
        """
        Generate a strong password.

        Args:
            length: Password length (8-128, default: 16)
            include_symbols: Include special characters (default: True)
            include_numbers: Include numbers (default: True)
            exclude_ambiguous: Exclude ambiguous characters like 0/O, 1/l/I (default: True)

        Returns:
            JSON string with password and strength info
        """
        import json

        try:
            # 验证长度
            if length < 8:
                return json.dumps({"error": "Password length must be at least 8"})
            if length > 128:
                return json.dumps({"error": "Password length must be at most 128"})

            # 构建字符集
            chars = ""
            char_types = []

            # 字母
            letters = string.ascii_letters
            if exclude_ambiguous:
                letters = letters.replace("l", "").replace("I", "").replace("O", "")
            chars += letters
            char_types.append("letters")

            # 数字
            if include_numbers:
                numbers = string.digits
                if exclude_ambiguous:
                    numbers = numbers.replace("0", "").replace("1", "")
                chars += numbers
                char_types.append("numbers")

            # 特殊字符
            if include_symbols:
                symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
                chars += symbols
                char_types.append("symbols")

            if not chars:
                return json.dumps({"error": "No character types selected"})

            # 生成密码（使用 secrets 模块确保加密安全）
            password = "".join(secrets.choice(chars) for _ in range(length))

            # 计算强度评分（简化版）
            strength_score = min(100, length * 5)
            if include_numbers:
                strength_score += 10
            if include_symbols:
                strength_score += 15
            strength_score = min(100, strength_score)

            logger.info(f"Generated password (length: {length}, strength: {strength_score})")

            return json.dumps(
                {
                    "success": True,
                    "password": password,
                    "length": length,
                    "strength_score": strength_score,
                    "character_types": char_types,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Password generation failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def check_password_strength(password: str) -> str:
        """
        Check password strength and provide recommendations.

        Args:
            password: Password to check

        Returns:
            JSON string with strength score (0-100), recommendations, and analysis
        """
        import json

        try:
            score = 0
            issues = []
            strengths = []

            # 长度检查
            length = len(password)
            if length < 8:
                issues.append("Password is too short (minimum 8 characters)")
            elif length >= 8:
                score += 20
                if length >= 12:
                    score += 10
                    strengths.append("Good length")
                if length >= 16:
                    score += 10
                    strengths.append("Excellent length")

            # 字符类型检查
            has_lower = any(c.islower() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_symbol = any(c in string.punctuation for c in password)

            if has_lower:
                score += 10
            else:
                issues.append("No lowercase letters")

            if has_upper:
                score += 10
            else:
                issues.append("No uppercase letters")

            if has_digit:
                score += 15
            else:
                issues.append("No numbers")

            if has_symbol:
                score += 20
                strengths.append("Contains special characters")
            else:
                issues.append("No special characters")

            # 重复字符检查
            has_repeats = any(password[i] == password[i + 1] for i in range(len(password) - 1))
            if has_repeats:
                score -= 5
                issues.append("Contains repeated characters")

            # 顺序字符检查
            sequential = ["123", "234", "345", "456", "567", "678", "789", "abc", "bcd", "cde"]
            has_sequential = any(seq in password.lower() for seq in sequential)
            if has_sequential:
                score -= 10
                issues.append("Contains sequential characters")

            # 常见密码检查（简化版）
            common_passwords = [
                "password", "123456", "12345678", "qwerty", "abc123", "monkey",
                "letmein", "trustno1", "dragon", "baseball", "iloveyou", "master",
                "sunshine", "ashley", "bailey", "shadow", "superman", "qazwsx"
            ]
            if password.lower() in common_passwords:
                score = 0
                issues.append("This is a commonly used password")

            # 确保分数在 0-100 范围内
            score = max(0, min(100, score))

            # 强度等级
            if score < 30:
                strength_level = "Weak"
            elif score < 60:
                strength_level = "Fair"
            elif score < 80:
                strength_level = "Good"
            else:
                strength_level = "Strong"

            logger.info(f"Password strength check: {strength_level} (score: {score})")

            return json.dumps(
                {
                    "success": True,
                    "strength_score": score,
                    "strength_level": strength_level,
                    "length": length,
                    "has_lowercase": has_lower,
                    "has_uppercase": has_upper,
                    "has_numbers": has_digit,
                    "has_symbols": has_symbol,
                    "issues": issues,
                    "strengths": strengths,
                },
                indent=2,
            )

        except Exception as e:
            logger.error(f"Password strength check failed: {e}")
            return json.dumps({"error": str(e)})
