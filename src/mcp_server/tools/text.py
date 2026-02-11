"""
Text processing tools for the MCP server.

Provides tools for:
- Word counting and text statistics
- Regular expression operations
- Text extraction (emails, URLs)
- Base64 encoding/decoding
- Text summarization and manipulation
"""

import re
import base64
from typing import Optional

from ..utils import logger, extract_text_by_regex, truncate_text, ValidationError

# Module metadata
CATEGORY_NAME = "Text Processing"
CATEGORY_DESCRIPTION = "Regex, encoding, email/URL extraction, text similarity"
TOOLS = [
    "count_words",
    "extract_emails",
    "extract_urls",
    "regex_match",
    "regex_replace",
    "text_summary",
    "encode_base64",
    "decode_base64",
    "calculate_text_similarity",
]


def register_tools(mcp):
    """Register all text processing tools with the MCP server."""

    @mcp.tool()
    def count_words(text: str, detailed: bool = True) -> str:
        """
        Count words and provide text statistics.

        Args:
            text: Text to analyze
            detailed: Include detailed statistics (default: True)

        Returns:
            JSON string with word count and statistics
        """
        try:
            import json

            # Basic counts
            words = text.split()
            word_count = len(words)
            char_count = len(text)
            char_count_no_spaces = len(text.replace(" ", ""))
            line_count = len(text.splitlines())

            result = {
                "word_count": word_count,
                "character_count": char_count,
                "character_count_no_spaces": char_count_no_spaces,
                "line_count": line_count,
            }

            if detailed:
                # Sentence count (approximate)
                sentences = re.split(r"[.!?]+", text)
                sentence_count = len([s for s in sentences if s.strip()])

                # Average word length
                avg_word_length = (
                    sum(len(word) for word in words) / word_count
                    if word_count > 0
                    else 0
                )

                # Paragraph count
                paragraphs = [p for p in text.split("\n\n") if p.strip()]
                paragraph_count = len(paragraphs)

                result.update(
                    {
                        "sentence_count": sentence_count,
                        "paragraph_count": paragraph_count,
                        "average_word_length": round(avg_word_length, 2),
                        "average_words_per_sentence": (
                            round(word_count / sentence_count, 2)
                            if sentence_count > 0
                            else 0
                        ),
                    }
                )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Word count failed: {e}")
            return f'{{"error": "Word count failed: {str(e)}"}}'

    @mcp.tool()
    def extract_emails(text: str) -> str:
        """
        Extract all email addresses from text.

        Args:
            text: Text to search for emails

        Returns:
            JSON string with list of email addresses found
        """
        try:
            import json

            # Regex pattern for email addresses
            email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            emails = extract_text_by_regex(text, email_pattern)

            # Remove duplicates while preserving order
            unique_emails = []
            seen = set()
            for email in emails:
                email_lower = email.lower()
                if email_lower not in seen:
                    seen.add(email_lower)
                    unique_emails.append(email)

            return json.dumps(
                {"count": len(unique_emails), "emails": unique_emails}, indent=2
            )

        except Exception as e:
            logger.error(f"Email extraction failed: {e}")
            return f'{{"error": "Email extraction failed: {str(e)}"}}'

    @mcp.tool()
    def extract_urls(text: str) -> str:
        """
        Extract all URLs from text.

        Args:
            text: Text to search for URLs

        Returns:
            JSON string with list of URLs found
        """
        try:
            import json

            # Regex pattern for URLs
            url_pattern = r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)"
            urls = extract_text_by_regex(text, url_pattern)

            # Remove duplicates while preserving order
            unique_urls = []
            seen = set()
            for url in urls:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)

            return json.dumps(
                {"count": len(unique_urls), "urls": unique_urls}, indent=2
            )

        except Exception as e:
            logger.error(f"URL extraction failed: {e}")
            return f'{{"error": "URL extraction failed: {str(e)}"}}'

    @mcp.tool()
    def regex_match(text: str, pattern: str, flags: str = "") -> str:
        """
        Find all matches of a regular expression in text.

        Args:
            text: Text to search
            pattern: Regular expression pattern
            flags: Regex flags (i=ignorecase, m=multiline, s=dotall)

        Returns:
            JSON string with list of matches
        """
        try:
            import json

            # Parse flags
            regex_flags = 0
            if "i" in flags.lower():
                regex_flags |= re.IGNORECASE
            if "m" in flags.lower():
                regex_flags |= re.MULTILINE
            if "s" in flags.lower():
                regex_flags |= re.DOTALL

            matches = re.findall(pattern, text, regex_flags)

            return json.dumps(
                {
                    "pattern": pattern,
                    "flags": flags,
                    "count": len(matches),
                    "matches": matches,
                },
                indent=2,
                ensure_ascii=False,
            )

        except re.error as e:
            return f'{{"error": "Invalid regex pattern: {str(e)}"}}'
        except Exception as e:
            logger.error(f"Regex match failed: {e}")
            return f'{{"error": "Regex match failed: {str(e)}"}}'

    @mcp.tool()
    def regex_replace(
        text: str, pattern: str, replacement: str, flags: str = ""
    ) -> str:
        """
        Replace text matching a regular expression.

        Args:
            text: Text to process
            pattern: Regular expression pattern to match
            replacement: Replacement string
            flags: Regex flags (i=ignorecase, m=multiline, s=dotall)

        Returns:
            Text with replacements made
        """
        try:
            # Parse flags
            regex_flags = 0
            if "i" in flags.lower():
                regex_flags |= re.IGNORECASE
            if "m" in flags.lower():
                regex_flags |= re.MULTILINE
            if "s" in flags.lower():
                regex_flags |= re.DOTALL

            result = re.sub(pattern, replacement, text, flags=regex_flags)
            return result

        except re.error as e:
            return f"Error: Invalid regex pattern: {str(e)}"
        except Exception as e:
            logger.error(f"Regex replace failed: {e}")
            return f"Error: Regex replace failed: {str(e)}"

    @mcp.tool()
    def text_summary(text: str, max_length: int = 500, method: str = "truncate") -> str:
        """
        Summarize or truncate text to a maximum length.

        Args:
            text: Text to summarize
            max_length: Maximum length (default: 500)
            method: Method to use - 'truncate' or 'sentences' (default: truncate)

        Returns:
            Summarized/truncated text
        """
        try:
            if len(text) <= max_length:
                return text

            if method == "sentences":
                # Try to cut at sentence boundary
                sentences = re.split(r"([.!?]+\s+)", text)
                result = ""
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    separator = sentences[i + 1] if i + 1 < len(sentences) else ""

                    if len(result) + len(sentence) + len(separator) <= max_length:
                        result += sentence + separator
                    else:
                        break

                if not result:
                    # Fallback to truncate if first sentence is too long
                    result = truncate_text(text, max_length)
                elif len(result) < len(text):
                    result += "..."

                return result
            else:
                # Simple truncation
                return truncate_text(text, max_length)

        except Exception as e:
            logger.error(f"Text summary failed: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    def encode_base64(text: str, encoding: str = "utf-8") -> str:
        """
        Encode text to Base64.

        Args:
            text: Text to encode
            encoding: Text encoding (default: utf-8)

        Returns:
            Base64 encoded string
        """
        try:
            encoded = base64.b64encode(text.encode(encoding)).decode("ascii")
            return encoded
        except Exception as e:
            logger.error(f"Base64 encoding failed: {e}")
            return f"Error: Encoding failed: {str(e)}"

    @mcp.tool()
    def decode_base64(encoded: str, encoding: str = "utf-8") -> str:
        """
        Decode Base64 to text.

        Args:
            encoded: Base64 encoded string
            encoding: Text encoding for decoded output (default: utf-8)

        Returns:
            Decoded text
        """
        try:
            decoded = base64.b64decode(encoded).decode(encoding)
            return decoded
        except Exception as e:
            logger.error(f"Base64 decoding failed: {e}")
            return f"Error: Decoding failed: {str(e)}"

    @mcp.tool()
    def calculate_text_similarity(
        text1: str, text2: str, method: str = "levenshtein"
    ) -> str:
        """
        Calculate similarity between two text strings.

        Args:
            text1: First text string
            text2: Second text string
            method: Algorithm - "levenshtein" or "jaccard" (default: levenshtein)

        Returns:
            JSON string with similarity score (0-1), distance, and method info
        """
        import json

        try:
            # 验证方法
            method = method.lower()
            if method not in ["levenshtein", "jaccard"]:
                raise ValidationError("Method must be 'levenshtein' or 'jaccard'")

            # 长文本截断（性能考虑）
            MAX_TEXT_LENGTH = 10000
            if len(text1) > MAX_TEXT_LENGTH:
                text1 = text1[:MAX_TEXT_LENGTH]
                logger.warning(f"Text1 truncated to {MAX_TEXT_LENGTH} characters")
            if len(text2) > MAX_TEXT_LENGTH:
                text2 = text2[:MAX_TEXT_LENGTH]
                logger.warning(f"Text2 truncated to {MAX_TEXT_LENGTH} characters")

            if method == "levenshtein":
                # Levenshtein 距离算法（编辑距离）
                def levenshtein_distance(s1, s2):
                    if len(s1) < len(s2):
                        return levenshtein_distance(s2, s1)
                    if len(s2) == 0:
                        return len(s1)

                    previous_row = range(len(s2) + 1)
                    for i, c1 in enumerate(s1):
                        current_row = [i + 1]
                        for j, c2 in enumerate(s2):
                            insertions = previous_row[j + 1] + 1
                            deletions = current_row[j] + 1
                            substitutions = previous_row[j] + (c1 != c2)
                            current_row.append(min(insertions, deletions, substitutions))
                        previous_row = current_row

                    return previous_row[-1]

                distance = levenshtein_distance(text1, text2)
                max_len = max(len(text1), len(text2))
                similarity = 1 - (distance / max_len) if max_len > 0 else 1.0

                logger.info(
                    f"Levenshtein similarity: {similarity:.3f} (distance: {distance})"
                )

                return json.dumps(
                    {
                        "success": True,
                        "method": "levenshtein",
                        "similarity": round(similarity, 4),
                        "distance": distance,
                        "text1_length": len(text1),
                        "text2_length": len(text2),
                    },
                    indent=2,
                )

            else:  # jaccard
                # Jaccard 相似度（基于集合）
                def jaccard_similarity(s1, s2):
                    # 转换为单词集合
                    set1 = set(s1.lower().split())
                    set2 = set(s2.lower().split())

                    if not set1 and not set2:
                        return 1.0
                    if not set1 or not set2:
                        return 0.0

                    intersection = len(set1.intersection(set2))
                    union = len(set1.union(set2))

                    return intersection / union if union > 0 else 0.0

                similarity = jaccard_similarity(text1, text2)

                logger.info(f"Jaccard similarity: {similarity:.3f}")

                return json.dumps(
                    {
                        "success": True,
                        "method": "jaccard",
                        "similarity": round(similarity, 4),
                        "text1_length": len(text1),
                        "text2_length": len(text2),
                    },
                    indent=2,
                )

        except ValidationError as e:
            logger.error(f"Text similarity calculation failed: {e}")
            return json.dumps({"error": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error in calculate_text_similarity: {e}")
            return json.dumps({"error": str(e)})
