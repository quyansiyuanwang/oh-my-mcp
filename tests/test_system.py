"""
测试动态元数据功能
验证 main.py 是否正确从各个模块读取元数据
"""

import json
from main import get_all_tools_info, get_version_info, TOOL_MODULES

def test_tool_modules_metadata():
    """测试所有模块是否都有正确的元数据"""
    print("=" * 60)
    print("测试模块元数据")
    print("=" * 60)

    for module_info in TOOL_MODULES:
        module = module_info["module"]
        category_key = module_info["category_key"]

        # 检查元数据是否存在
        category_name = getattr(module, "CATEGORY_NAME", None)
        category_desc = getattr(module, "CATEGORY_DESCRIPTION", None)
        tools_list = getattr(module, "TOOLS", None)

        print(f"\n模块: {module.__name__}")
        print(f"  类别键: {category_key}")
        print(f"  类别名: {category_name}")
        print(f"  描述: {category_desc}")
        print(f"  工具数量: {len(tools_list) if tools_list else 0}")

        # 验证元数据完整性
        assert category_name is not None, f"{module.__name__} 缺少 CATEGORY_NAME"
        assert category_desc is not None, f"{module.__name__} 缺少 CATEGORY_DESCRIPTION"
        assert tools_list is not None, f"{module.__name__} 缺少 TOOLS"
        assert len(tools_list) > 0, f"{module.__name__} 的 TOOLS 列表为空"

    print("\n所有模块元数据验证通过!")

def test_list_all_tools():
    """测试 get_all_tools_info() 函数"""
    print("\n" + "=" * 60)
    print("测试 get_all_tools_info() 函数")
    print("=" * 60)

    data = get_all_tools_info()

    print(f"\n服务器名称: {data['server']['name']}")
    print(f"服务器版本: {data['server']['version']}")
    print(f"总工具数: {data['total_tools']}")
    print(f"\n类别数量: {len(data['categories'])}")

    for category_key, category_info in data['categories'].items():
        print(f"\n  {category_key}:")
        print(f"    名称: {category_info['name']}")
        print(f"    描述: {category_info['description']}")
        print(f"    工具数: {category_info['count']}")
        print(f"    工具列表: {', '.join(category_info['tools'][:3])}...")

    # 验证总数
    calculated_total = sum(cat['count'] for cat in data['categories'].values())
    assert data['total_tools'] == calculated_total, "工具总数不匹配"

    print("\nlist_all_tools() 验证通过!")

def test_get_server_version():
    """测试 get_version_info() 函数"""
    print("\n" + "=" * 60)
    print("测试 get_version_info() 函数")
    print("=" * 60)

    data = get_version_info()

    print(f"\n服务器名称: {data['name']}")
    print(f"版本: {data['version']}")
    print(f"描述: {data['description']}")
    print(f"总工具数: {data['total_tools']}")
    print(f"总类别数: {data['total_categories']}")
    print(f"总资源数: {data['total_resources']}")

    print("\n功能特性:")
    for i, feature in enumerate(data['features'], 1):
        print(f"  {i}. {feature}")

    # 验证数据
    assert data['total_tools'] == 74, f"工具总数应为 74,实际为 {data['total_tools']}"
    assert data['total_categories'] == 7, f"类别总数应为 7,实际为 {data['total_categories']}"
    assert len(data['features']) == 7, f"特性数量应为 7,实际为 {len(data['features'])}"

    print("\nget_server_version() 验证通过!")

if __name__ == "__main__":
    try:
        test_tool_modules_metadata()
        test_list_all_tools()
        test_get_server_version()

        print("\n" + "=" * 60)
        print("所有测试通过!")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
