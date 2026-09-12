"""
Pytest configuration and shared fixtures for MCP server tests.
"""

import random
import string
import tempfile
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text_file(temp_dir: Path) -> Path:
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("Hello, World!\nThis is a test file.")
    return file_path


@pytest.fixture
def sample_json_file(temp_dir: Path) -> Path:
    """Create a sample JSON file for testing."""
    import json

    file_path = temp_dir / "sample.json"
    data = {"name": "test", "value": 123, "items": [1, 2, 3]}
    file_path.write_text(json.dumps(data, indent=2))
    return file_path


class TestConfig:
    """Test configuration - centralized settings"""

    def __init__(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="mcp_test_")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_temp_file(self, suffix: str = "") -> Path:
        """Generate temporary file path"""
        return Path(self.temp_dir) / f"test_{self.timestamp}_{random.randint(1000, 9999)}{suffix}"

    def generate_random_text(self, length: int = 100) -> str:
        """Generate random text content"""
        words = [
            "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
            for _ in range(length // 5)
        ]
        return " ".join(words)

    def cleanup(self) -> None:
        """Clean up temporary files"""
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)


@pytest.fixture
def config() -> Generator[TestConfig, None, None]:
    """Provide test configuration with automatic cleanup."""
    test_config = TestConfig()
    yield test_config
    test_config.cleanup()
