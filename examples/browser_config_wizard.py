"""
浏览器配置向导

交互式配置浏览器驱动路径、代理等设置
"""

import sys
from pathlib import Path

# 添加 src 到 path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server.tools.browser.browser_config import get_browser_config


def print_header():
    """打印标题"""
    print("=" * 60)
    print("浏览器自动化配置向导")
    print("=" * 60)
    print()


def print_section(title: str):
    """打印分节标题"""
    print(f"【{title}】")


def main():
    """运行配置向导"""
    print_header()

    config = get_browser_config()
    current = config.get_all_settings()

    print(f"配置文件位置: {current['config_file']}")
    print()

    # Chrome驱动路径
    print_section("1. Chrome 驱动路径")
    current_chrome = current["driver_paths"]["chrome"] or "未配置（将自动下载）"
    print(f"当前值: {current_chrome}")
    chrome_path = input("新路径（直接回车保持不变）: ").strip()
    if chrome_path:
        try:
            config.set_chrome_driver_path(chrome_path)
            print(f"✓ 已保存: {chrome_path}")
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    print()

    # Edge驱动路径
    print_section("2. Edge 驱动路径")
    current_edge = current["driver_paths"]["edge"] or "未配置（将自动下载）"
    print(f"当前值: {current_edge}")
    edge_path = input("新路径（直接回车保持不变）: ").strip()
    if edge_path:
        try:
            config.set_edge_driver_path(edge_path)
            print(f"✓ 已保存: {edge_path}")
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    print()

    # 默认浏览器
    print_section("3. 默认浏览器")
    print(f"当前值: {current['default_browser']}")
    browser = input("选择 (chrome/edge，直接回车保持不变): ").strip().lower()
    if browser in ("chrome", "edge"):
        try:
            config.set_default_browser(browser)
            print(f"✓ 已保存: {browser}")
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    elif browser and browser not in ("chrome", "edge"):
        print("✗ 无效选项，必须是 chrome 或 edge")
    print()

    # 默认无头模式
    print_section("4. 默认无头模式")
    print(f"当前值: {'启用' if current['default_headless'] else '禁用'}")
    headless = input("启用无头模式? (yes/no，直接回车保持不变): ").strip().lower()
    if headless in ("yes", "y", "true", "1"):
        try:
            config.set_default_headless(True)
            print("✓ 已保存: 启用")
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    elif headless in ("no", "n", "false", "0"):
        try:
            config.set_default_headless(False)
            print("✓ 已保存: 禁用")
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    print()

    # 代理设置
    print_section("5. 代理服务器")
    current_proxy = current["proxy"] or "未配置"
    print(f"当前值: {current_proxy}")
    print("提示: 格式如 http://proxy.example.com:8080")
    proxy = input("代理URL（直接回车保持不变）: ").strip()
    if proxy:
        try:
            config.set_proxy(proxy)
            print(f"✓ 已保存: {proxy}")
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    print()

    # 自动兜底
    print_section("6. Chrome 到 Edge 自动兜底")
    print(f"当前值: {'启用' if current['auto_fallback'] else '禁用'}")
    print("说明: 当 Chrome 驱动获取失败时，自动切换到 Edge")
    fallback = input("启用自动兜底? (yes/no，直接回车保持不变): ").strip().lower()
    if fallback in ("yes", "y", "true", "1"):
        try:
            config.set_auto_fallback(True)
            print("✓ 已保存: 启用")
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    elif fallback in ("no", "n", "false", "0"):
        try:
            config.set_auto_fallback(False)
            print("✓ 已保存: 禁用")
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    print()

    # 截图保存目录
    print_section("7. 截图保存目录")
    current_screenshot = current["screenshot_dir"] or "未配置（截图将返回 base64）"
    print(f"当前值: {current_screenshot}")
    print("提示: 配置后截图自动保存到此目录，文件名含时间戳")
    print("示例: ~/.oh-my-mcp/screenshots 或 D:\\Screenshots")
    screenshot_dir = input("截图目录（直接回车保持不变）: ").strip()
    if screenshot_dir:
        try:
            config.set_screenshot_dir(screenshot_dir)
            print(f"✓ 已保存: {config.get_screenshot_dir()}")
        except Exception as e:
            print(f"✗ 保存失败: {e}")
    print()

    # 显示最终配置
    print("=" * 60)
    print("配置完成！")
    print()
    print("当前配置:")
    final_config = config.get_all_settings()

    print(f"  配置文件: {final_config['config_file']}")
    print(f"  Chrome 驱动: {final_config['driver_paths']['chrome'] or '未配置'}")
    print(f"  Edge 驱动: {final_config['driver_paths']['edge'] or '未配置'}")
    print(f"  默认浏览器: {final_config['default_browser']}")
    print(f"  无头模式: {'是' if final_config['default_headless'] else '否'}")
    print(f"  代理: {final_config['proxy'] or '未配置'}")
    print(f"  自动兜底: {'是' if final_config['auto_fallback'] else '否'}")
    print(f"  截图目录: {final_config['screenshot_dir'] or '未配置'}")
    print()
    print(f"配置已保存到: {config.config_path}")
    print("=" * 60)
    print()
    print("使用方式:")
    print("  1. 环境变量优先级更高（如 CHROME_DRIVER_PATH）")
    print("  2. 配置文件提供默认值")
    print("  3. 未配置时自动下载驱动（需要网络连接）")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n配置已取消")
    except Exception as e:
        print(f"\n\n错误: {e}")
        import traceback

        traceback.print_exc()
