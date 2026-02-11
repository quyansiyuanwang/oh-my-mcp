"""
Subagent 配置管理使用示例

演示如何使用配置管理类持久化保存和管理 API 密钥
"""

import json
import os
import sys

# 添加项目路径到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "src"))


def example_1_set_config():
    """示例 1: 设置配置"""
    print("=" * 60)
    print("示例 1: 设置 API 配置")
    print("=" * 60)

    from mcp_server.tools.subagent_config import SubagentConfig

    config = SubagentConfig()

    # 设置 OpenAI API
    print("\n1. 设置 OpenAI 配置...")
    config.set_api_key("openai", "sk-proj-test-key-for-demo-purposes-only-12345678")
    print(f"✓ OpenAI API 密钥已保存")

    # 设置带自定义端点的配置
    print("\n2. 设置 OpenAI 配置（自定义端点）...")
    config.set_api_key("openai", "sk-proj-test-key-for-demo-purposes-only-12345678")
    config.set_api_base("openai", "https://api.openai-proxy.com/v1")
    print(f"✓ OpenAI API 密钥和自定义端点已保存")

    # 设置 Anthropic
    print("\n3. 设置 Anthropic 配置...")
    config.set_api_key("anthropic", "sk-ant-test-key-for-demo-purposes-only")
    print(f"✓ Anthropic API 密钥已保存")

    print(f"\n配置文件: {config.get_config_path()}")


def example_2_get_config():
    """示例 2: 查询配置"""
    print("\n" + "=" * 60)
    print("示例 2: 查询配置信息")
    print("=" * 60)

    from mcp_server.tools.subagent_config import SubagentConfig

    config = SubagentConfig()

    # 查询 OpenAI 配置
    print("\n1. 查询 OpenAI 配置...")
    api_key = config.get_api_key("openai")
    api_base = config.get_api_base("openai")

    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✓ OpenAI 已配置")
        print(f"  密钥预览: {masked_key}")
        print(f"  API 端点: {api_base}")

        # 检测来源
        env_key = os.getenv("OPENAI_API_KEY")
        source = "environment" if env_key else "config_file"
        print(f"  配置来源: {source}")
    else:
        print("✗ OpenAI 未配置")

    # 查询 Anthropic 配置
    print("\n2. 查询 Anthropic 配置...")
    api_key = config.get_api_key("anthropic")

    if api_key:
        print(f"✓ Anthropic 已配置")
    else:
        print(f"✗ Anthropic 未配置")


def example_3_list_config():
    """示例 3: 列出所有配置"""
    print("\n" + "=" * 60)
    print("示例 3: 列出所有配置")
    print("=" * 60)

    from mcp_server.tools.subagent_config import SubagentConfig

    config = SubagentConfig()

    print(f"\n配置文件: {config.get_config_path()}")

    providers_info = config.list_providers()
    print(f"已配置提供商数: {len(providers_info)}\n")

    if providers_info:
        for provider, info in providers_info.items():
            print(f"📌 {provider.upper()}")
            print(f"   密钥: {info['api_key']}")
            print(f"   端点: {info['api_base']}")
            print(f"   来源: {info['source']}")
            print()
    else:
        print("暂无配置的提供商")
        print("提示: 使用 config.set_api_key() 配置 API 密钥")


def example_4_test_with_config():
    """示例 4: 使用配置的密钥（验证读取）"""
    print("\n" + "=" * 60)
    print("示例 4: 使用配置的密钥")
    print("=" * 60)

    from mcp_server.tools.subagent_config import SubagentConfig

    config = SubagentConfig()

    # 检查配置
    api_key = config.get_api_key("openai")
    api_base = config.get_api_base("openai")

    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"\n✓ OpenAI 已配置")

        # 检测来源
        env_key = os.getenv("OPENAI_API_KEY")
        source = "environment" if env_key else "config_file"

        print(f"  来源: {source}")
        print(f"  端点: {api_base}")
        print(f"  密钥: {masked_key}")

        print("\n准备使用配置的密钥...")
        print("注意: 实际 AI 调用需要通过 MCP 工具进行")
        print("      示例: subagent_call(provider='openai', model='gpt-3.5-turbo', ...)")

    else:
        print(f"\n✗ OpenAI 未配置")
        print("请先使用 config.set_api_key() 配置 API 密钥")


def example_5_priority_demo():
    """示例 5: 演示配置优先级"""
    print("\n" + "=" * 60)
    print("示例 5: 配置优先级演示")
    print("=" * 60)

    from mcp_server.tools.subagent_config import SubagentConfig

    config = SubagentConfig()

    # 1. 设置配置文件中的密钥
    print("\n1. 在配置文件中设置密钥...")
    config.set_api_key("openai", "sk-config-file-key-12345678")

    api_key = config.get_api_key("openai")
    masked_key = api_key[:10] + "..." if api_key else "None"
    env_key = os.getenv("OPENAI_API_KEY")
    source = "environment" if env_key else "config_file"
    print(f"   当前使用: {source} - {masked_key}")

    # 2. 设置环境变量（更高优先级）
    print("\n2. 设置环境变量（覆盖配置文件）...")
    os.environ["OPENAI_API_KEY"] = "sk-env-var-key-87654321"

    api_key = config.get_api_key("openai")
    masked_key = api_key[:10] + "..." if api_key else "None"
    env_key = os.getenv("OPENAI_API_KEY")
    source = "environment" if env_key else "config_file"
    print(f"   当前使用: {source} - {masked_key}")

    # 3. 清除环境变量
    print("\n3. 清除环境变量...")
    del os.environ["OPENAI_API_KEY"]

    api_key = config.get_api_key("openai")
    masked_key = api_key[:10] + "..." if api_key else "None"
    env_key = os.getenv("OPENAI_API_KEY")
    source = "environment" if env_key else "config_file"
    print(f"   当前使用: {source} - {masked_key}")

    print("\n优先级顺序: 环境变量 > 配置文件 > 默认值")


def example_6_custom_config_file():
    """示例 6: 使用自定义配置文件"""
    print("\n" + "=" * 60)
    print("示例 6: 使用自定义配置文件路径")
    print("=" * 60)

    from mcp_server.tools.subagent_config import SubagentConfig
    import tempfile

    # 创建临时配置文件
    temp_config = os.path.join(tempfile.gettempdir(), "test_subagent_config.json")

    print(f"\n创建临时配置: {temp_config}")

    # 使用自定义配置文件
    config = SubagentConfig(config_path=temp_config)

    # 设置配置
    print("\n设置配置...")
    config.set_api_key("openai", "sk-custom-config-key-12345678")
    config.set_api_base("openai", "https://custom-endpoint.com/v1")

    # 读取配置
    print("\n读取配置...")
    api_key = config.get_api_key("openai")
    api_base = config.get_api_base("openai")

    masked_key = api_key[:10] + "..." if api_key else "None"
    print(f"  API Key: {masked_key}")
    print(f"  API Base: {api_base}")
    print(f"  配置文件: {config.get_config_path()}")

    # 清理
    if os.path.exists(temp_config):
        os.remove(temp_config)
        print(f"\n清理临时文件: {temp_config}")


def example_7_export_config():
    """示例 7: 导出配置"""
    print("\n" + "=" * 60)
    print("示例 7: 导出配置（脱敏）")
    print("=" * 60)

    from mcp_server.tools.subagent_config import SubagentConfig

    config = SubagentConfig()

    # 导出配置（密钥已脱敏）
    print("\n当前配置导出（密钥已脱敏）:")
    print(config.export_config())


def example_8_remove_config():
    """示例 8: 删除配置"""
    print("\n" + "=" * 60)
    print("示例 8: 删除配置")
    print("=" * 60)

    from mcp_server.tools.subagent_config import SubagentConfig

    config = SubagentConfig()

    # 查看当前配置
    print("\n删除前:")
    api_key = config.get_api_key("openai")
    if api_key:
        masked_key = api_key[:10] + "..." if api_key else "None"
        print(f"  OpenAI: {masked_key}")
    else:
        print("  OpenAI: 未配置")

    # 删除配置
    if api_key:
        print("\n删除 OpenAI 配置...")
        config.remove_api_key("openai")

    # 再次查看
    print("\n删除后:")
    api_key = config.get_api_key("openai")
    if api_key:
        masked_key = api_key[:10] + "..." if api_key else "None"
        print(f"  OpenAI: {masked_key}")
    else:
        print("  OpenAI: 未配置")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Subagent 配置管理示例")
    print("=" * 60)

    try:
        # 示例 1: 设置配置
        example_1_set_config()

        # 示例 2: 查询配置
        example_2_get_config()

        # 示例 3: 列出所有配置
        example_3_list_config()

        # 示例 4: 使用配置进行调用
        example_4_test_with_config()

        # 示例 5: 优先级演示
        example_5_priority_demo()

        # 示例 6: 自定义配置文件
        example_6_custom_config_file()

        # 示例 7: 导出配置
        example_7_export_config()

        # 示例 8: 删除配置
        example_8_remove_config()

        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        print("\n配置文件位置:")
        from mcp_server.tools.subagent_config import get_config

        print(f"  {get_config().get_config_path()}")
        print("\n提示: 可以手动编辑配置文件或使用删除命令清理测试数据")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
