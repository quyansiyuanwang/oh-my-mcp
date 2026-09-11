#!/usr/bin/env python3
"""Tests for text processing tools."""

import base64
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.tools import text


class MockMCP:
    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


MOCK_MCP = MockMCP()
text.register_tools(MOCK_MCP)
T = MOCK_MCP.tools


class TestCountWords:
    def test_basic_counts(self) -> None:
        result = json.loads(T["count_words"]("hello world\nsecond line"))
        assert result["word_count"] == 4
        assert result["line_count"] == 2
        assert result["character_count"] == len("hello world\nsecond line")

    def test_detailed(self) -> None:
        result = json.loads(T["count_words"]("One sentence. Two sentences!", detailed=True))
        assert result["sentence_count"] == 2

    def test_detailed_false(self) -> None:
        result = json.loads(T["count_words"]("hello", detailed=False))
        assert "sentence_count" not in result


class TestExtraction:
    def test_extract_emails(self) -> None:
        result = json.loads(T["extract_emails"]("contact a@b.com or c@d.org, not foo@bar"))
        assert result["count"] == 2
        assert result["emails"] == ["a@b.com", "c@d.org"]

    def test_extract_emails_dedup(self) -> None:
        result = json.loads(T["extract_emails"]("x@y.com x@y.com"))
        assert result["count"] == 1

    def test_extract_urls(self) -> None:
        result = json.loads(T["extract_urls"]("see https://example.com/page?q=1 and http://a.io"))
        assert result["count"] == 2
        assert result["urls"][0] == "https://example.com/page?q=1"

    def test_extract_urls_empty(self) -> None:
        result = json.loads(T["extract_urls"]("no urls here"))
        assert result["count"] == 0


class TestRegex:
    def test_regex_match_basic(self) -> None:
        result = json.loads(T["regex_match"]("abc123def456", r"\d+"))
        assert result["count"] == 2
        assert result["matches"] == ["123", "456"]

    def test_regex_match_ignorecase_flag(self) -> None:
        result = json.loads(T["regex_match"]("Hello WORLD", "hello", flags="i"))
        assert result["count"] == 1

    def test_regex_match_invalid_pattern(self) -> None:
        result = json.loads(T["regex_match"]("text", "[unclosed"))
        assert "error" in result

    def test_regex_replace(self) -> None:
        assert T["regex_replace"]("a1b2", r"\d", "#") == "a#b#"

    def test_regex_replace_flags(self) -> None:
        assert T["regex_replace"]("Hello World", "world", "there", flags="i") == "Hello there"

    def test_regex_replace_invalid(self) -> None:
        assert "Error" in T["regex_replace"]("t", "(", "x")


class TestSummary:
    def test_short_text_unchanged(self) -> None:
        assert T["text_summary"]("short", max_length=100) == "short"

    def test_truncate(self) -> None:
        long_text = "x" * 300
        result = T["text_summary"](long_text, max_length=100)
        assert len(result) <= 100
        assert result.endswith("...")

    def test_sentences_method(self) -> None:
        long_text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        result = T["text_summary"](long_text, max_length=30, method="sentences")
        assert result.startswith("First")
        assert len(result) <= 32  # max_length + ellipsis


class TestBase64:
    def test_roundtrip_ascii(self) -> None:
        encoded = T["encode_base64"]("hello")
        assert encoded == base64.b64encode(b"hello").decode()
        assert T["decode_base64"](encoded) == "hello"

    def test_roundtrip_unicode(self) -> None:
        encoded = T["encode_base64"]("中文测试")
        assert T["decode_base64"](encoded) == "中文测试"

    def test_decode_invalid(self) -> None:
        assert "Error" in T["decode_base64"]("!!!not-base64!!!")


class TestSimilarity:
    def test_identical_levenshtein(self) -> None:
        result = json.loads(T["calculate_text_similarity"]("abc", "abc"))
        assert result["similarity"] == 1.0
        assert result["distance"] == 0

    def test_different_levenshtein(self) -> None:
        result = json.loads(T["calculate_text_similarity"]("kitten", "sitting"))
        assert result["distance"] == 3
        assert 0 <= result["similarity"] < 1

    def test_empty_levenshtein(self) -> None:
        result = json.loads(T["calculate_text_similarity"]("", ""))
        assert result["similarity"] == 1.0

    def test_jaccard(self) -> None:
        result = json.loads(
            T["calculate_text_similarity"]("the quick fox", "the lazy fox", method="jaccard")
        )
        assert result["method"] == "jaccard"
        assert abs(result["similarity"] - 1 / 2) < 0.01

    def test_invalid_method(self) -> None:
        result = json.loads(T["calculate_text_similarity"]("a", "b", method="bogus"))
        assert "error" in result
