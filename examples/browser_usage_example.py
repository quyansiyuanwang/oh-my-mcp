"""
浏览器自动化示例

演示如何使用 MCP Server 的浏览器自动化工具进行网页操作。
使用 Selenium 驱动 Chrome 或 Edge 浏览器进行自动化交互。

注意：运行此示例需要安装 Chrome 或 Edge 浏览器。
webdriver-manager 会自动下载对应的驱动程序。
"""

import json
import time


def example_basic_navigation():
    """示例：基本的浏览器导航操作"""
    from mcp_server.tools.browser.handlers import (
        browser_back,
        browser_navigate,
        browser_open,
        browser_refresh,
    )

    print("=== 基本浏览器导航示例 ===\n")

    # 打开浏览器并导航到网页
    print("1. 打开浏览器...")
    result = browser_open("https://www.python.org", browser="chrome", headless=False)
    data = json.loads(result)

    if "error" in data:
        print(f"错误: {data['error']}")
        return None

    session_id = data["session_id"]
    print(f"   会话 ID: {session_id}")
    print(f"   当前 URL: {data['current_url']}")
    print(f"   页面标题: {data['title']}")

    time.sleep(2)

    # 导航到另一个页面
    print("\n2. 导航到 Google...")
    result = browser_navigate(session_id, "https://www.google.com")
    data = json.loads(result)
    print(f"   当前 URL: {data.get('current_url', 'N/A')}")

    time.sleep(2)

    # 返回上一页
    print("\n3. 返回上一页...")
    result = browser_back(session_id)
    data = json.loads(result)
    print(f"   当前 URL: {data.get('current_url', 'N/A')}")

    time.sleep(1)

    # 刷新页面
    print("\n4. 刷新页面...")
    result = browser_refresh(session_id)
    data = json.loads(result)
    print(f"   刷新完成: {data.get('success', False)}")

    return session_id


def example_element_interaction(session_id: str):
    """示例：元素交互操作"""
    from mcp_server.tools.browser.handlers import (
        browser_find_elements,
        browser_get_text,
        browser_navigate,
        browser_type,
    )

    print("\n=== 元素交互示例 ===\n")

    # 导航到示例网站
    print("1. 导航到示例表单页面...")
    result = browser_navigate(session_id, "https://www.google.com")
    data = json.loads(result)

    time.sleep(2)

    # 查找搜索框
    print("\n2. 查找页面元素...")
    result = browser_find_elements(session_id, "input", by="tag", limit=5)
    data = json.loads(result)
    print(f"   找到 {data.get('element_count', 0)} 个 input 元素")

    # 在搜索框输入文本
    print("\n3. 在搜索框输入文本...")
    # Google 搜索框的选择器
    result = browser_type(
        session_id,
        "textarea[name='q'], input[name='q']",
        "Python MCP Server",
        by="css",
    )
    data = json.loads(result)
    print(f"   输入完成: {data.get('success', False)}")

    time.sleep(1)

    # 点击搜索按钮（或按回车）
    print("\n4. 提交搜索...")
    from mcp_server.tools.browser.handlers import browser_execute_js

    result = browser_execute_js(
        session_id,
        "document.querySelector('textarea[name=q], input[name=q]').form.submit()",
    )

    time.sleep(3)

    # 获取搜索结果文本
    print("\n5. 获取页面内容...")
    result = browser_get_text(session_id, "body", max_length=500)
    data = json.loads(result)
    if not data.get("error"):
        print(f"   页面文本预览: {data.get('text', '')[:200]}...")


def example_screenshot(session_id: str):
    """示例：截图功能"""
    from mcp_server.tools.browser.handlers import browser_navigate, browser_screenshot

    print("\n=== 截图示例 ===\n")

    # 导航到要截图的页面
    print("1. 导航到 Python 官网...")
    browser_navigate(session_id, "https://www.python.org")
    time.sleep(2)

    # 普通截图（返回 base64）
    print("2. 进行截图...")
    result = browser_screenshot(session_id)
    data = json.loads(result)

    if "error" not in data:
        print("   截图成功!")
        print(f"   格式: {data.get('format', 'N/A')}")
        print(f"   大小: {data.get('size_bytes', 0)} bytes")
        print(f"   Base64 长度: {len(data.get('base64', ''))} 字符")

    # 保存截图到文件
    print("\n3. 保存截图到文件...")
    result = browser_screenshot(session_id, save_path="python_org_screenshot.png")
    data = json.loads(result)

    if "error" not in data:
        print(f"   已保存到: {data.get('saved_to', 'N/A')}")


def example_javascript_execution(session_id: str):
    """示例：JavaScript 执行"""
    from mcp_server.tools.browser.handlers import browser_execute_js, browser_navigate

    print("\n=== JavaScript 执行示例 ===\n")

    browser_navigate(session_id, "https://www.python.org")
    time.sleep(2)

    # 获取页面标题
    print("1. 通过 JS 获取页面标题...")
    result = browser_execute_js(session_id, "return document.title;")
    data = json.loads(result)
    print(f"   标题: {data.get('result', 'N/A')}")

    # 获取所有链接数量
    print("\n2. 通过 JS 统计链接数量...")
    result = browser_execute_js(session_id, "return document.links.length;")
    data = json.loads(result)
    print(f"   链接数量: {data.get('result', 'N/A')}")

    # 滚动页面
    print("\n3. 通过 JS 滚动到页面底部...")
    result = browser_execute_js(
        session_id, "window.scrollTo(0, document.body.scrollHeight); return 'done';"
    )
    data = json.loads(result)
    print(f"   滚动结果: {data.get('result', 'N/A')}")

    time.sleep(1)


def example_console_logs(session_id: str):
    """示例：获取控制台日志"""
    from mcp_server.tools.browser.handlers import (
        browser_execute_js,
        browser_get_console_logs,
    )

    print("\n=== 控制台日志示例 ===\n")

    # 执行一些 console.log
    print("1. 执行 console.log...")
    browser_execute_js(session_id, "console.log('Hello from MCP Server!');")
    browser_execute_js(session_id, "console.warn('This is a warning');")
    browser_execute_js(session_id, "console.error('This is an error');")

    time.sleep(1)

    # 获取所有日志
    print("\n2. 获取控制台日志...")
    result = browser_get_console_logs(session_id, level="all")
    data = json.loads(result)

    logs = data.get("logs", [])
    print(f"   日志数量: {len(logs)}")

    for log in logs[-5:]:  # 显示最近 5 条
        print(f"   [{log.get('level', 'INFO')}] {log.get('message', '')[:50]}")


def example_cookies(session_id: str):
    """示例：Cookie 管理"""
    from mcp_server.tools.browser.handlers import (
        browser_delete_cookies,
        browser_get_cookies,
        browser_navigate,
        browser_set_cookie,
    )

    print("\n=== Cookie 管理示例 ===\n")

    browser_navigate(session_id, "https://www.python.org")
    time.sleep(1)

    # 获取现有 Cookie
    print("1. 获取现有 Cookie...")
    result = browser_get_cookies(session_id)
    data = json.loads(result)
    cookies = data.get("cookies", [])
    print(f"   Cookie 数量: {len(cookies)}")
    for cookie in cookies[:3]:
        print(f"   - {cookie.get('name')}: {cookie.get('value', '')[:20]}...")

    # 设置自定义 Cookie
    print("\n2. 设置自定义 Cookie...")
    result = browser_set_cookie(session_id, "mcp_test", "hello_world")
    data = json.loads(result)
    print(f"   设置结果: {data.get('success', False)}")

    # 验证 Cookie 已设置
    print("\n3. 验证 Cookie...")
    result = browser_get_cookies(session_id, name="mcp_test")
    data = json.loads(result)
    print(f"   找到 mcp_test: {len(data.get('cookies', [])) > 0}")

    # 删除 Cookie
    print("\n4. 删除自定义 Cookie...")
    result = browser_delete_cookies(session_id, name="mcp_test")
    data = json.loads(result)
    print(f"   删除结果: {data.get('success', False)}")


def example_multi_tab(session_id: str):
    """示例：多标签页管理"""
    from mcp_server.tools.browser.handlers import (
        browser_close_tab,
        browser_list_tabs,
        browser_new_tab,
        browser_switch_tab,
    )

    print("\n=== 多标签页管理示例 ===\n")

    # 打开新标签页
    print("1. 打开新标签页...")
    result = browser_new_tab(session_id, "https://www.google.com")
    data = json.loads(result)
    print(f"   标签页数量: {data.get('tab_count', 0)}")

    time.sleep(1)

    # 再打开一个标签页
    print("\n2. 再打开一个标签页...")
    result = browser_new_tab(session_id, "https://github.com")
    data = json.loads(result)
    print(f"   标签页数量: {data.get('tab_count', 0)}")

    time.sleep(1)

    # 列出所有标签页
    print("\n3. 列出所有标签页...")
    result = browser_list_tabs(session_id)
    data = json.loads(result)

    for tab in data.get("tabs", []):
        current = " (当前)" if tab.get("is_current") else ""
        print(f"   Tab {tab.get('index')}: {tab.get('title', 'N/A')[:30]}{current}")

    # 切换到第一个标签页
    print("\n4. 切换到第一个标签页...")
    result = browser_switch_tab(session_id, 0)
    data = json.loads(result)
    print(f"   当前 URL: {data.get('current_url', 'N/A')}")

    # 关闭最后一个标签页
    print("\n5. 关闭最后一个标签页...")
    result = browser_close_tab(session_id, tab_index=2)
    data = json.loads(result)
    print(f"   剩余标签页: {data.get('tab_count', 0)}")


def example_form_filling(session_id: str):
    """示例：表单自动填写"""
    from mcp_server.tools.browser.handlers import browser_fill_form, browser_navigate

    print("\n=== 表单自动填写示例 ===\n")

    # 导航到表单页面（使用 httpbin 的表单测试页面）
    print("1. 导航到测试表单...")
    browser_navigate(session_id, "https://httpbin.org/forms/post")
    time.sleep(2)

    # 一次性填写多个字段
    print("\n2. 自动填写表单...")
    form_data = json.dumps(
        {
            "input[name='custname']": "张三",
            "input[name='custtel']": "13800138000",
            "input[name='custemail']": "zhangsan@example.com",
            "textarea[name='comments']": "这是一条测试评论，由 MCP Server 自动填写。",
        }
    )

    result = browser_fill_form(session_id, form_data)
    data = json.loads(result)

    print(f"   处理字段数: {data.get('fields_processed', 0)}")
    for res in data.get("results", []):
        status = "✓" if res.get("status") != "error" else "✗"
        print(f"   {status} {res.get('selector')}: {res.get('status')}")


def example_network_monitoring(session_id: str):
    """示例：网络请求监控"""
    from mcp_server.tools.browser.handlers import (
        browser_enable_network_log,
        browser_get_network_logs,
        browser_navigate,
    )

    print("\n=== 网络请求监控示例 ===\n")

    # 启用网络日志
    print("1. 启用网络请求监控...")
    result = browser_enable_network_log(session_id)
    data = json.loads(result)
    print(f"   启用结果: {data.get('success', False)}")

    # 导航到页面（这会产生网络请求）
    print("\n2. 导航到页面（产生网络请求）...")
    browser_navigate(session_id, "https://httpbin.org/get")
    time.sleep(2)

    # 获取网络日志
    print("\n3. 获取网络请求日志...")
    result = browser_get_network_logs(session_id, limit=10)
    data = json.loads(result)

    logs = data.get("logs", [])
    print(f"   捕获请求数: {len(logs)}")

    for log in logs[:5]:
        log_type = log.get("type", "unknown")
        if log_type == "request":
            print(f"   → {log.get('method', 'GET')} {log.get('url', '')[:50]}...")
        else:
            print(f"   ← {log.get('status', 0)} {log.get('url', '')[:50]}...")


def cleanup(session_id: str):
    """清理：关闭浏览器"""
    from mcp_server.tools.browser.handlers import browser_close

    print("\n=== 清理 ===\n")
    print("关闭浏览器...")
    result = browser_close(session_id)
    data = json.loads(result)
    print(f"   结果: {data.get('message', data.get('error', 'Unknown'))}")


def main():
    """运行所有示例"""
    session_id = None

    try:
        # 基本导航（返回 session_id）
        session_id = example_basic_navigation()

        if session_id:
            # 元素交互
            example_element_interaction(session_id)

            # 截图
            example_screenshot(session_id)

            # JavaScript 执行
            example_javascript_execution(session_id)

            # 控制台日志
            example_console_logs(session_id)

            # Cookie 管理
            example_cookies(session_id)

            # 多标签页
            example_multi_tab(session_id)

            # 表单填写
            example_form_filling(session_id)

            # 网络监控
            example_network_monitoring(session_id)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback

        traceback.print_exc()

    finally:
        if session_id:
            cleanup(session_id)


if __name__ == "__main__":
    print("=" * 60)
    print("MCP Server 浏览器自动化示例")
    print("=" * 60)
    print()
    print("注意：此示例会打开真实的浏览器窗口")
    print("请确保已安装 Chrome 或 Edge 浏览器")
    print()
    main()
