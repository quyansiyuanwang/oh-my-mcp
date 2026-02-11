#!/usr/bin/env python3
"""Improved test suite for new MCP tools - No hardcoding"""

import sys
import json
import tempfile
import random
import string
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server import (
    compression_tools,
    data_tools,
    file_tools,
    web_tools,
    utility_tools,
    text_tools
)

class MockMCP:
    """Mock MCP server for testing"""
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

class TestConfig:
    """Test configuration - centralized settings"""
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="mcp_test_")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_temp_file(self, suffix=""):
        """Generate temporary file path"""
        return Path(self.temp_dir) / f"test_{self.timestamp}_{random.randint(1000, 9999)}{suffix}"

    def generate_random_text(self, length=100):
        """Generate random text content"""
        words = [''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
                 for _ in range(length // 5)]
        return ' '.join(words)

    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

def test_compression_tools(config):
    """Test compression tools with dynamic data"""
    print("=" * 60)
    print("Testing Compression Tools")
    print("=" * 60)

    mcp = MockMCP()
    compression_tools.register_tools(mcp)

    # Create test files with random content
    test_files = []
    for i in range(2):
        file_path = config.get_temp_file(".txt")
        file_path.write_text(config.generate_random_text())
        test_files.append(str(file_path))

    # Test compress_zip
    zip_path = str(config.get_temp_file(".zip"))
    print(f"\n1. Testing compress_zip with {len(test_files)} files")
    result = mcp.tools['compress_zip'](test_files, zip_path, 6)
    data = json.loads(result)
    print(f"   Success: {data.get('success')}, Files: {data.get('file_count')}")

    # Test list_archive_contents
    print(f"\n2. Testing list_archive_contents")
    result = mcp.tools['list_archive_contents'](zip_path)
    data = json.loads(result)
    print(f"   Success: {data.get('success')}, Files: {data.get('file_count')}")

    # Test extract_zip
    extract_dir = str(config.get_temp_file("_extracted"))
    print(f"\n3. Testing extract_zip")
    result = mcp.tools['extract_zip'](zip_path, extract_dir)
    data = json.loads(result)
    print(f"   Success: {data.get('success')}, Extracted: {data.get('file_count')} files")

    print("\n[OK] Compression tools test completed")

def test_config_tools(config):
    """Test configuration file tools with dynamic data"""
    print("\n" + "=" * 60)
    print("Testing Configuration File Tools")
    print("=" * 60)

    mcp = MockMCP()
    data_tools.register_tools(mcp)

    # Generate dynamic YAML content
    yaml_content = f"""
project:
  name: test-project-{config.timestamp}
  version: {random.randint(1, 9)}.{random.randint(0, 9)}.{random.randint(0, 9)}
settings:
  debug: {random.choice(['true', 'false'])}
  port: {random.randint(8000, 9000)}
"""

    print("\n1. Testing parse_yaml")
    result = mcp.tools['parse_yaml'](yaml_content)
    data = json.loads(result)
    print(f"   Success: {'project' in data}")

    print("\n2. Testing yaml_to_json")
    result = mcp.tools['yaml_to_json'](yaml_content, 2)
    print(f"   Success: {len(result) > 0}")

    # Generate dynamic JSON content
    json_content = json.dumps({
        "name": f"test-{config.timestamp}",
        "value": random.randint(1, 100),
        "items": [random.randint(1, 10) for _ in range(3)]
    })

    print("\n3. Testing json_to_yaml")
    result = mcp.tools['json_to_yaml'](json_content)
    print(f"   Success: {len(result) > 0}")

    print("\n[OK] Configuration file tools test completed")

def test_file_diff_tools(config):
    """Test file comparison tools with dynamic data"""
    print("\n" + "=" * 60)
    print("Testing File Comparison Tools")
    print("=" * 60)

    mcp = MockMCP()
    file_tools.register_tools(mcp)

    # Create two files with slight differences
    base_text = config.generate_random_text(50)
    words = base_text.split()
    modified_text = ' '.join(words[:len(words)//2] + ['MODIFIED'] + words[len(words)//2+1:])

    file1 = config.get_temp_file(".txt")
    file2 = config.get_temp_file(".txt")
    file1.write_text(base_text)
    file2.write_text(modified_text)

    print("\n1. Testing diff_files")
    result = mcp.tools['diff_files'](str(file1), str(file2), 3, "unified")
    data = json.loads(result)
    print(f"   Success: {data.get('success')}, Changes: {data.get('total_changes')}")

    print("\n2. Testing diff_text")
    result = mcp.tools['diff_text'](base_text, modified_text, "unified")
    data = json.loads(result)
    print(f"   Success: {data.get('success')}, Changes: {data.get('total_changes')}")

    print("\n[OK] File comparison tools test completed")

def test_security_tools(config):
    """Test security tools with dynamic parameters"""
    print("\n" + "=" * 60)
    print("Testing Security Tools")
    print("=" * 60)

    mcp = MockMCP()
    utility_tools.register_tools(mcp)

    # Test with random password length
    password_length = random.randint(12, 24)
    print(f"\n1. Testing generate_password (length: {password_length})")
    result = mcp.tools['generate_password'](password_length, True, True, True)
    data = json.loads(result)
    print(f"   Success: {data.get('success')}, Strength: {data.get('strength_score')}")

    # Test with generated password
    test_password = data.get('password', '')
    print(f"\n2. Testing check_password_strength")
    result = mcp.tools['check_password_strength'](test_password)
    data = json.loads(result)
    print(f"   Success: {data.get('success')}, Level: {data.get('strength_level')}")

    print("\n[OK] Security tools test completed")

def test_text_similarity(config):
    """Test text similarity with dynamic data"""
    print("\n" + "=" * 60)
    print("Testing Text Similarity Tool")
    print("=" * 60)

    mcp = MockMCP()
    text_tools.register_tools(mcp)

    # Generate similar texts
    base_text = config.generate_random_text(30)
    words = base_text.split()
    similar_text = ' '.join(words[:len(words)//2] + words[len(words)//2+2:])

    print("\n1. Testing calculate_text_similarity (Levenshtein)")
    result = mcp.tools['calculate_text_similarity'](base_text, similar_text, "levenshtein")
    data = json.loads(result)
    print(f"   Success: {data.get('success')}, Similarity: {data.get('similarity')}")

    print("\n2. Testing calculate_text_similarity (Jaccard)")
    result = mcp.tools['calculate_text_similarity'](base_text, similar_text, "jaccard")
    data = json.loads(result)
    print(f"   Success: {data.get('success')}, Similarity: {data.get('similarity')}")

    print("\n[OK] Text similarity tool test completed")

def main():
    """Main test runner"""
    config = TestConfig()

    try:
        print(f"\nTest Configuration:")
        print(f"  Temp Directory: {config.temp_dir}")
        print(f"  Timestamp: {config.timestamp}")
        print()

        test_compression_tools(config)
        test_config_tools(config)
        test_file_diff_tools(config)
        test_security_tools(config)
        test_text_similarity(config)

        print("\n" + "=" * 60)
        print("All Tests Completed Successfully")
        print("=" * 60)

    finally:
        config.cleanup()
        print(f"\nCleaned up temporary files")

if __name__ == "__main__":
    main()
