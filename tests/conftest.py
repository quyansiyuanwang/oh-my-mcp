"""
Pytest configuration and shared fixtures for MCP server tests.
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("Hello, World!\nThis is a test file.")
    return file_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing."""
    import json
    file_path = temp_dir / "sample.json"
    data = {"name": "test", "value": 123, "items": [1, 2, 3]}
    file_path.write_text(json.dumps(data, indent=2))
    return file_path
