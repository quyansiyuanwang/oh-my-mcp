"""
文件操作示例

演示如何使用 MCP Server 的文件系统工具。
"""

import json
import tempfile
from pathlib import Path

from mcp_server.tools.file.handlers import (
    file_exists,
    get_file_info,
    list_directory,
    read_file,
    search_files,
    write_file,
)


def example_file_operations():
    """示例：基本文件操作"""
    print("=== 文件操作示例 ===\n")

    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # 1. 写入文件
        print("1. 写入文件")
        file_path = str(tmpdir_path / "example.txt")
        content = "Hello, MCP Server!\nThis is a test file."

        write_result = write_file(file_path, content)
        print(f"   {json.loads(write_result)['message']}")

        # 2. 读取文件
        print("\n2. 读取文件")
        read_result = read_file(file_path)
        read_data = json.loads(read_result)
        print(f"   内容: {read_data['content']}")

        # 3. 检查文件是否存在
        print("\n3. 检查文件存在")
        exists_result = file_exists(file_path)
        exists_data = json.loads(exists_result)
        print(f"   存在: {exists_data['exists']}")
        print(f"   类型: {exists_data['type']}")

        # 4. 获取文件信息
        print("\n4. 获取文件信息")
        info_result = get_file_info(file_path)
        info_data = json.loads(info_result)
        print(f"   大小: {info_data['size']} 字节")
        print(f"   修改时间: {info_data['modified']}")

        # 5. 创建更多文件
        print("\n5. 创建多个文件")
        for i in range(3):
            write_file(str(tmpdir_path / f"file{i}.txt"), f"Content {i}")
        print("   创建了 3 个文件")

        # 6. 列出目录内容
        print("\n6. 列出目录内容")
        list_result = list_directory(tmpdir)
        list_data = json.loads(list_result)
        print(f"   找到 {list_data['count']} 个项目:")
        for item in list_data["items"]:
            print(f"   - {item['name']} ({item['type']})")

        # 7. 搜索文件
        print("\n7. 搜索文件")
        search_result = search_files(tmpdir, "*.txt")
        search_data = json.loads(search_result)
        print(f"   找到 {len(search_data['files'])} 个 .txt 文件")


def main():
    """运行示例"""
    try:
        example_file_operations()
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
