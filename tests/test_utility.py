#!/usr/bin/env python3
"""测试新增的MCP工具"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.tools import compression, data, file, web, utility, text

class MockMCP:
    """模拟MCP服务器用于测试"""
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

def test_compression_tools():
    """测试压缩工具"""
    print("=" * 60)
    print("测试压缩工具 (5个)")
    print("=" * 60)

    mcp = MockMCP()
    compression_tools.register_tools(mcp)

    # 创建测试文件
    test_file1 = Path("test1.txt")
    test_file2 = Path("test2.txt")
    test_file1.write_text("Hello World from file 1")
    test_file2.write_text("Hello World from file 2")

    # 1. 测试 compress_zip
    print("\n1. 测试 compress_zip:")
    result = mcp.tools['compress_zip']([str(test_file1), str(test_file2)], "test.zip", 6)
    print(f"   结果: {result[:100]}...")

    # 2. 测试 list_archive_contents
    print("\n2. 测试 list_archive_contents:")
    result = mcp.tools['list_archive_contents']("test.zip")
    print(f"   结果: {result[:150]}...")

    # 3. 测试 extract_zip
    print("\n3. 测试 extract_zip:")
    result = mcp.tools['extract_zip']("test.zip", "./extracted_zip")
    print(f"   结果: {result[:150]}...")

    # 4. 测试 compress_tar
    print("\n4. 测试 compress_tar:")
    result = mcp.tools['compress_tar']([str(test_file1), str(test_file2)], "test.tar.gz", "gz")
    print(f"   结果: {result[:100]}...")

    # 5. 测试 extract_tar
    print("\n5. 测试 extract_tar:")
    result = mcp.tools['extract_tar']("test.tar.gz", "./extracted_tar")
    print(f"   结果: {result[:150]}...")

    # 清理测试文件
    test_file1.unlink()
    test_file2.unlink()
    Path("test.zip").unlink(missing_ok=True)
    Path("test.tar.gz").unlink(missing_ok=True)

    print("\n✅ 压缩工具测试完成")

if __name__ == "__main__":
    test_compression_tools()
