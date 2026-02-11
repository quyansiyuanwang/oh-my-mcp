"""
Web and network tools for the MCP server.

Provides tools for:
- Multi-engine web search (DuckDuckGo, Bing, Google, Baidu)
- Advanced search with caching and rate limiting
- Webpage fetching and parsing
- URL validation and parsing
- HTTP operations
- Link extraction
"""

import json
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from ...utils import (
    logger,
    retry,
    validate_url as _validate_url,
    NetworkError,
    ValidationError,
    sanitize_path,
    format_bytes,
)
from ..search_engine import get_search_manager
from ..registry import tool_handler

# 获取搜索管理器实例
search_manager = get_search_manager()


# Helper function for fetching webpages (not a tool itself)
@retry(max_attempts=3, delay=1.0, exceptions=(requests.RequestException,))
def _fetch_webpage_helper(url: str, timeout: int = 10) -> str:
    """Helper function to fetch webpage HTML."""
    if not _validate_url(url):
        raise ValidationError(f"Invalid URL: {url}")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text

    except requests.RequestException as e:
        logger.error(f"Failed to fetch webpage {url}: {e}")
        raise NetworkError(f"Failed to fetch webpage: {e}") from e


@tool_handler
def web_search(query: str, max_results: int = 10) -> str:
    """
    Search the web using multiple search engines with智能 fallback.

    Features:
    - Automatic fallback between search engines (DuckDuckGo -> Bing)
    - Intelligent caching to reduce API calls
    - Rate limiting protection
    - Result deduplication

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 10, max: 20)

    Returns:
        JSON string containing search results with title, link, and snippet
    """
    max_results = min(max_results, 20)

    # 使用默认引擎列表进行搜索
    result = search_manager.search(
        query=query,
        max_results=max_results,
        engines=["duckduckgo", "bing"],  # 默认引擎顺序
        parallel=False,  # 串行搜索（故障转移）
        use_cache=True,
        is_news=False,
    )

    # 格式化返回结果
    if result["success"]:
        return json.dumps(
            {
                "results": result["results"],
                "count": result["count"],
                "query": query,
                "search_engine": (
                    result["engines_used"][0] if result["engines_used"] else "Unknown"
                ),
                "cached": result.get("cached", False),
            },
            ensure_ascii=False,
            indent=2,
        )
    else:
        return json.dumps(
            {
                "results": [],
                "message": "No results found",
                "error": result.get("error"),
                "errors": result.get("errors"),
            },
            ensure_ascii=False,
        )


@tool_handler
def web_search_advanced(
    query: str,
    max_results: int = 10,
    engines: str = "duckduckgo,bing",
    parallel: bool = False,
    use_cache: bool = True,
) -> str:
    """
    Advanced web search with multi-engine support and parallel searching.

    Features:
    - Support for multiple search engines: DuckDuckGo, Bing, Google, Baidu
    - Parallel searching across multiple engines
    - Intelligent result merging and deduplication
    - Smart caching mechanism
    - Rate limiting protection

    Args:
        query: Search query string
        max_results: Maximum number of results (default: 10, max: 50)
        engines: Comma-separated list of engines (default: "duckduckgo,bing")
                 Available: duckduckgo, bing, google, baidu
        parallel: Search engines in parallel (default: False)
        use_cache: Use cached results if available (default: True)

    Returns:
        JSON string containing combined search results

    Example:
        web_search_advanced("Python programming", 15, "duckduckgo,google", True)
    """
    max_results = min(max_results, 50)
    engine_list = [e.strip().lower() for e in engines.split(",")]

    # 执行搜索
    result = search_manager.search(
        query=query,
        max_results=max_results,
        engines=engine_list,
        parallel=parallel,
        use_cache=use_cache,
        is_news=False,
    )

    return json.dumps(
        {
            "success": result["success"],
            "results": result["results"],
            "count": result["count"],
            "query": query,
            "engines_used": result["engines_used"],
            "parallel": parallel,
            "cached": result.get("cached", False),
            "errors": result.get("errors"),
        },
        ensure_ascii=False,
        indent=2,
    )


@tool_handler
def web_search_news(query: str, max_results: int = 10) -> str:
    """
    Search for news articles using multiple search engines with fallback.

    Features:
    - Automatic fallback between news search engines
    - Intelligent caching
    - Rate limiting protection
    - Result deduplication

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 10, max: 20)

    Returns:
        JSON string containing news search results
    """
    max_results = min(max_results, 20)

    # 使用新闻搜索
    result = search_manager.search(
        query=query,
        max_results=max_results,
        engines=["duckduckgo", "bing", "google"],
        parallel=False,
        use_cache=True,
        is_news=True,
    )

    # 格式化返回结果
    if result["success"]:
        return json.dumps(
            {
                "results": result["results"],
                "count": result["count"],
                "query": query,
                "type": "news",
                "search_engine": (
                    result["engines_used"][0] if result["engines_used"] else "Unknown"
                ),
                "cached": result.get("cached", False),
            },
            ensure_ascii=False,
            indent=2,
        )
    else:
        return json.dumps(
            {
                "results": [],
                "message": "No news results found",
                "error": result.get("error"),
                "errors": result.get("errors"),
            },
            ensure_ascii=False,
        )


@tool_handler
def clear_search_cache() -> str:
    """
    Clear the search cache.

    This will remove all cached search results, forcing fresh searches.

    Returns:
        JSON string with operation result
    """
    try:
        search_manager.cache.clear()
        return json.dumps(
            {"success": True, "message": "Search cache cleared successfully"},
            indent=2,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool_handler
def get_search_stats() -> str:
    """
    Get search cache and rate limiter statistics.

    Returns:
        JSON string with cache stats, hit rate, and rate limiter info
    """
    try:
        cache_stats = search_manager.cache.get_stats()
        return json.dumps(
            {
                "success": True,
                "cache": cache_stats,
                "rate_limiter": {
                    "max_requests": search_manager.rate_limiter.max_requests,
                    "window_seconds": search_manager.rate_limiter.window_seconds,
                },
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


@tool_handler
def fetch_webpage(url: str, timeout: int = 10) -> str:
    """
    Fetch the HTML content of a webpage.

    Args:
        url: URL of the webpage to fetch
        timeout: Request timeout in seconds (default: 10)

    Returns:
        HTML content of the webpage
    """
    try:
        return _fetch_webpage_helper(url, timeout)
    except Exception as e:
        logger.error(f"fetch_webpage tool failed: {e}")
        raise


@tool_handler
def fetch_webpage_text(url: str, timeout: int = 10) -> str:
    """
    Fetch and extract clean text content from a webpage.

    Args:
        url: URL of the webpage to fetch
        timeout: Request timeout in seconds (default: 10)

    Returns:
        Clean text content extracted from the webpage
    """
    try:
        html = _fetch_webpage_helper(url, timeout)
        soup = BeautifulSoup(html, "lxml")

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        return text

    except Exception as e:
        logger.error(f"Failed to extract text from {url}: {e}")
        raise NetworkError(f"Failed to extract text: {e}") from e


@tool_handler
def parse_html(html: str, selector: str) -> str:
    """
    Parse HTML and extract elements using CSS selector.

    Args:
        html: HTML content to parse
        selector: CSS selector to find elements

    Returns:
        JSON string containing matched elements' text content
    """
    try:
        soup = BeautifulSoup(html, "lxml")
        elements = soup.select(selector)

        results = []
        for elem in elements:
            results.append(
                {
                    "tag": elem.name,
                    "text": elem.get_text(strip=True),
                    "attributes": dict(elem.attrs),
                }
            )

        return json.dumps(
            {"selector": selector, "count": len(results), "elements": results},
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"HTML parsing failed: {e}")
        return f'{{"error": "Parsing failed: {str(e)}"}}'


@tool_handler
def download_file(url: str, save_path: str, timeout: int = 30) -> str:
    """
    Download a file from URL and save to disk.

    Args:
        url: URL of the file to download
        save_path: Local path where file should be saved
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Success message with file path and size
    """
    if not _validate_url(url):
        raise ValidationError(f"Invalid URL: {url}")

    try:
        path = sanitize_path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()

        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size = path.stat().st_size

        return f"File downloaded successfully to {save_path} ({format_bytes(file_size)})"

    except Exception as e:
        logger.error(f"File download failed: {e}")
        raise NetworkError(f"Download failed: {e}") from e


@tool_handler
def get_page_title(url: str, timeout: int = 10) -> str:
    """
    Extract the title from a webpage.

    Args:
        url: URL of the webpage
        timeout: Request timeout in seconds (default: 10)

    Returns:
        Page title or error message
    """
    try:
        html = _fetch_webpage_helper(url, timeout)
        soup = BeautifulSoup(html, "lxml")

        title = soup.find("title")
        if title:
            return title.get_text(strip=True)

        return "No title found"

    except Exception as e:
        logger.error(f"Failed to get page title: {e}")
        return f"Error: {str(e)}"


@tool_handler
def get_page_links(url: str, timeout: int = 10, absolute: bool = True) -> str:
    """
    Extract all links from a webpage.

    Args:
        url: URL of the webpage
        timeout: Request timeout in seconds (default: 10)
        absolute: Convert relative URLs to absolute (default: True)

    Returns:
        JSON string containing list of links
    """
    try:
        html = _fetch_webpage_helper(url, timeout)
        soup = BeautifulSoup(html, "lxml")

        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]

            if absolute and not href.startswith(("http://", "https://", "//")):
                href = urljoin(url, href)

            links.append({"url": href, "text": a_tag.get_text(strip=True)})

        return json.dumps(
            {"source_url": url, "count": len(links), "links": links},
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Failed to extract links: {e}")
        return f'{{"error": "Failed to extract links: {str(e)}"}}'


@tool_handler
def check_url_status(url: str, timeout: int = 10) -> str:
    """
    Check the HTTP status of a URL.

    Args:
        url: URL to check
        timeout: Request timeout in seconds (default: 10)

    Returns:
        JSON string with status code and message
    """
    if not _validate_url(url):
        return f'{{"error": "Invalid URL: {url}"}}'

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)

        return json.dumps(
            {
                "url": url,
                "status_code": response.status_code,
                "status_text": response.reason,
                "accessible": response.status_code < 400,
                "final_url": response.url if response.url != url else None,
            },
            indent=2,
        )

    except requests.RequestException as e:
        logger.error(f"Status check failed for {url}: {e}")
        return f'{{"error": "Status check failed: {str(e)}"}}'


@tool_handler
def get_headers(url: str, timeout: int = 10) -> str:
    """
    Get HTTP headers from a URL.

    Args:
        url: URL to get headers from
        timeout: Request timeout in seconds (default: 10)

    Returns:
        JSON string containing HTTP headers
    """
    if not _validate_url(url):
        return f'{{"error": "Invalid URL: {url}"}}'

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)

        return json.dumps(
            {
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
            },
            indent=2,
        )

    except requests.RequestException as e:
        logger.error(f"Failed to get headers from {url}: {e}")
        return f'{{"error": "Failed to get headers: {str(e)}"}}'


@tool_handler
def validate_url_format(url: str) -> str:
    """
    Validate if a string is a properly formatted URL.

    Args:
        url: URL string to validate

    Returns:
        JSON string with validation result and details
    """
    is_valid = _validate_url(url)

    result = {"url": url, "valid": is_valid}

    if is_valid:
        parsed = urlparse(url)
        result["details"] = {
            "scheme": parsed.scheme,
            "domain": parsed.netloc,
            "path": parsed.path,
            "query": parsed.query,
            "fragment": parsed.fragment,
        }
    else:
        result["error"] = "Invalid URL format"

    return json.dumps(result, indent=2)


@tool_handler
def parse_url_components(url: str) -> str:
    """
    Parse a URL and extract its components.

    Args:
        url: URL to parse

    Returns:
        JSON string containing URL components
    """
    try:
        parsed = urlparse(url)

        return json.dumps(
            {
                "original": url,
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "hostname": parsed.hostname,
                "port": parsed.port,
                "path": parsed.path,
                "params": parsed.params,
                "query": parsed.query,
                "fragment": parsed.fragment,
                "username": parsed.username,
                "password": "***" if parsed.password else None,
            },
            indent=2,
        )

    except Exception as e:
        return f'{{"error": "Failed to parse URL: {str(e)}"}}'


@tool_handler
def http_request(
    url: str,
    method: str = "GET",
    headers: str = "{}",
    body: str = None,
    timeout: int = 10,
) -> str:
    """
    Make HTTP request with custom headers and body.

    Args:
        url: Target URL
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        headers: JSON string of headers
        body: Request body (for POST/PUT/PATCH)
        timeout: Request timeout in seconds (default: 10)

    Returns:
        JSON string with status, headers, and body
    """
    try:
        # 验证 URL
        if not _validate_url(url):
            raise ValidationError(f"Invalid URL: {url}")

        # 解析 headers
        try:
            headers_dict = json.loads(headers)
        except json.JSONDecodeError:
            raise ValidationError("Headers must be valid JSON")

        # 验证 method
        method = method.upper()
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"]:
            raise ValidationError(f"Unsupported method: {method}")

        # 发送请求
        response = requests.request(
            method=method,
            url=url,
            headers=headers_dict,
            data=body,
            timeout=timeout,
            allow_redirects=True,
        )

        # 限制响应大小
        MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB
        if len(response.content) > MAX_RESPONSE_SIZE:
            return json.dumps({"error": f"Response too large: {len(response.content)} bytes"})

        # 过滤敏感头
        safe_headers = {
            k: v
            for k, v in response.headers.items()
            if k.lower() not in ["authorization", "cookie", "set-cookie"]
        }

        logger.info(f"HTTP {method} request to {url}: {response.status_code}")

        return json.dumps(
            {
                "success": True,
                "status_code": response.status_code,
                "status_text": response.reason,
                "headers": dict(safe_headers),
                "body": response.text,
                "size": len(response.content),
                "url": response.url,  # 最终 URL（处理重定向）
            },
            indent=2,
            ensure_ascii=False,
        )

    except requests.RequestException as e:
        logger.error(f"HTTP request failed: {e}")
        return json.dumps({"error": f"Request failed: {str(e)}"})
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return json.dumps({"error": str(e)})


@tool_handler
def get_network_info() -> str:
    """
    Get network interface information.

    Returns:
        JSON string with network interfaces, IP addresses, and MAC addresses
    """
    import psutil

    try:
        interfaces = []
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        for interface_name, addr_list in addrs.items():
            interface_info = {
                "name": interface_name,
                "addresses": [],
                "is_up": stats[interface_name].isup if interface_name in stats else False,
            }

            for addr in addr_list:
                addr_info = {"family": str(addr.family)}
                if addr.family.name == "AF_INET":
                    addr_info["type"] = "IPv4"
                    addr_info["address"] = addr.address
                    addr_info["netmask"] = addr.netmask
                elif addr.family.name == "AF_INET6":
                    addr_info["type"] = "IPv6"
                    addr_info["address"] = addr.address
                    addr_info["netmask"] = addr.netmask
                elif addr.family.name == "AF_LINK":
                    addr_info["type"] = "MAC"
                    addr_info["address"] = addr.address

                interface_info["addresses"].append(addr_info)

            interfaces.append(interface_info)

        logger.info(f"Retrieved network info for {len(interfaces)} interfaces")

        return json.dumps(
            {"success": True, "interfaces": interfaces, "count": len(interfaces)},
            indent=2,
        )

    except Exception as e:
        logger.error(f"Failed to get network info: {e}")
        return json.dumps({"error": str(e)})


@tool_handler
def dns_lookup(hostname: str, record_type: str = "A") -> str:
    """
    Perform DNS lookup.

    Args:
        hostname: Hostname or domain name
        record_type: DNS record type - A, AAAA, MX, NS, TXT (default: A)

    Returns:
        JSON string with DNS records
    """
    import socket

    try:
        record_type = record_type.upper()
        results = []

        if record_type == "A":
            # IPv4 addresses
            try:
                addrs = socket.getaddrinfo(hostname, None, socket.AF_INET)
                results = list(set(addr[4][0] for addr in addrs))
            except socket.gaierror as e:
                return json.dumps({"error": f"DNS lookup failed: {e}"})

        elif record_type == "AAAA":
            # IPv6 addresses
            try:
                addrs = socket.getaddrinfo(hostname, None, socket.AF_INET6)
                results = list(set(addr[4][0] for addr in addrs))
            except socket.gaierror as e:
                return json.dumps({"error": f"DNS lookup failed: {e}"})

        else:
            return json.dumps(
                {
                    "error": f"Record type {record_type} not supported. Use A or AAAA. For MX/NS/TXT, use specialized DNS tools."
                }
            )

        logger.info(f"DNS lookup for {hostname} ({record_type}): {len(results)} records")

        return json.dumps(
            {
                "success": True,
                "hostname": hostname,
                "record_type": record_type,
                "records": results,
                "count": len(results),
            },
            indent=2,
        )

    except Exception as e:
        logger.error(f"DNS lookup failed: {e}")
        return json.dumps({"error": str(e)})
