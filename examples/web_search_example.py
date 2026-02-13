"""
网络搜索和页面抓取示例

演示如何使用 MCP Server 的网络工具进行搜索和页面抓取。
"""

import json

from mcp_server.tools.web.handlers import (
    fetch_webpage_text,
    get_page_links,
    get_page_title,
    web_search,
)


def example_web_search():
    """示例：使用 DuckDuckGo 搜索"""
    print("=== 网络搜索示例 ===\n")

    # 搜索 Python 相关内容
    query = "Python programming language"
    max_results = 5

    print(f"搜索: {query}")
    result = web_search(query, max_results)
    data = json.loads(result)

    if "error" in data:
        print(f"错误: {data['error']}")
        return

    print(f"\n找到 {len(data.get('results', []))} 个结果:\n")
    for i, item in enumerate(data.get("results", []), 1):
        print(f"{i}. {item['title']}")
        print(f"   {item['link']}")
        print(f"   {item['snippet'][:100]}...\n")


def example_fetch_webpage():
    """示例：抓取网页内容"""
    print("\n=== 网页抓取示例 ===\n")

    url = "https://www.python.org"
    print(f"抓取: {url}")

    # 获取页面标题
    title_result = get_page_title(url)
    title_data = json.loads(title_result)
    print(f"标题: {title_data.get('title', 'N/A')}")

    # 获取页面文本内容
    text_result = fetch_webpage_text(url)
    text_data = json.loads(text_result)

    if "error" not in text_data:
        content = text_data.get("content", "")
        print("\n内容预览 (前 200 字符):")
        print(content[:200] + "...")

    # 获取页面链接
    links_result = get_page_links(url)
    links_data = json.loads(links_result)

    if "error" not in links_data:
        links = links_data.get("links", [])
        print(f"\n找到 {len(links)} 个链接")
        print("前 5 个链接:")
        for link in links[:5]:
            print(f"  - {link}")


def main():
    """运行所有示例"""
    try:
        example_web_search()
        example_fetch_webpage()
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
