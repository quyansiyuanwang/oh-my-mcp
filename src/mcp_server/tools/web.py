"""
Web and network tools for the MCP server.

Provides tools for:
- Web search (DuckDuckGo with fallback)
- Webpage fetching and parsing
- URL validation and parsing
- HTTP operations
- Link extraction
"""

import re
from typing import Optional
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from .utils import (
    logger,
    retry,
    validate_url as _validate_url,
    NetworkError,
    ValidationError,
    truncate_text,
    sanitize_path,
    FileOperationError,
)

# Module metadata
CATEGORY_NAME = "Web & Network"
CATEGORY_DESCRIPTION = "Web search, page fetching, HTML parsing, downloads, HTTP API client, DNS lookup"
TOOLS = [
    "web_search",
    "fetch_webpage",
    "fetch_webpage_text",
    "parse_html",
    "download_file",
    "get_page_title",
    "get_page_links",
    "check_url_status",
    "get_headers",
    "validate_url_format",
    "parse_url_components",
    "web_search_news",
    "http_request",
    "get_network_info",
    "dns_lookup",
]


def register_tools(mcp):
    """Register all web tools with the MCP server."""

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

    @mcp.tool()
    def web_search(query: str, max_results: int = 10) -> str:
        """
        Search the web using DuckDuckGo.

        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10, max: 20)

        Returns:
            JSON string containing search results with title, link, and snippet
        """
        try:
            from duckduckgo_search import DDGS

            max_results = min(max_results, 20)

            with DDGS() as ddgs:
                results = []
                for i, result in enumerate(ddgs.text(query, max_results=max_results)):
                    if i >= max_results:
                        break
                    results.append(
                        {
                            "title": result.get("title", ""),
                            "link": result.get("href", ""),
                            "snippet": result.get("body", ""),
                        }
                    )

                if not results:
                    return '{"results": [], "message": "No results found"}'

                import json

                return json.dumps(
                    {"results": results, "count": len(results), "query": query},
                    ensure_ascii=False,
                    indent=2,
                )

        except ImportError:
            return '{"error": "duckduckgo-search not installed. Install with: pip install duckduckgo-search"}'
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f'{{"error": "Search failed: {str(e)}"}}'

    @mcp.tool()
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

    @mcp.tool()
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

    @mcp.tool()
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

            import json

            return json.dumps(
                {"selector": selector, "count": len(results), "elements": results},
                ensure_ascii=False,
                indent=2,
            )

        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            return f'{{"error": "Parsing failed: {str(e)}"}}'

    @mcp.tool()
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

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            response.raise_for_status()

            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = path.stat().st_size
            from .utils import format_bytes

            return f"File downloaded successfully to {save_path} ({format_bytes(file_size)})"

        except Exception as e:
            logger.error(f"File download failed: {e}")
            raise NetworkError(f"Download failed: {e}") from e

    @mcp.tool()
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

    @mcp.tool()
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

            import json

            return json.dumps(
                {"source_url": url, "count": len(links), "links": links},
                ensure_ascii=False,
                indent=2,
            )

        except Exception as e:
            logger.error(f"Failed to extract links: {e}")
            return f'{{"error": "Failed to extract links: {str(e)}"}}'

    @mcp.tool()
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
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.head(
                url, headers=headers, timeout=timeout, allow_redirects=True
            )

            import json

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

    @mcp.tool()
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
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.head(
                url, headers=headers, timeout=timeout, allow_redirects=True
            )

            import json

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

    @mcp.tool()
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

        import json

        return json.dumps(result, indent=2)

    @mcp.tool()
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

            import json

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

    @mcp.tool()
    def web_search_news(query: str, max_results: int = 10) -> str:
        """
        Search for news articles using DuckDuckGo News.

        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10, max: 20)

        Returns:
            JSON string containing news search results
        """
        try:
            from duckduckgo_search import DDGS

            max_results = min(max_results, 20)

            with DDGS() as ddgs:
                results = []
                for i, result in enumerate(ddgs.news(query, max_results=max_results)):
                    if i >= max_results:
                        break
                    results.append(
                        {
                            "title": result.get("title", ""),
                            "link": result.get("url", ""),
                            "snippet": result.get("body", ""),
                            "date": result.get("date", ""),
                            "source": result.get("source", ""),
                        }
                    )

                if not results:
                    return '{"results": [], "message": "No news results found"}'

                import json

                return json.dumps(
                    {
                        "results": results,
                        "count": len(results),
                        "query": query,
                        "type": "news",
                    },
                    ensure_ascii=False,
                    indent=2,
                )

        except ImportError:
            return '{"error": "duckduckgo-search not installed. Install with: pip install duckduckgo-search"}'
        except Exception as e:
            logger.error(f"News search failed: {e}")
            return f'{{"error": "News search failed: {str(e)}"}}'

    @mcp.tool()
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
        import json

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
                return json.dumps(
                    {"error": f"Response too large: {len(response.content)} bytes"}
                )

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

    @mcp.tool()
    def get_network_info() -> str:
        """
        Get network interface information.

        Returns:
            JSON string with network interfaces, IP addresses, and MAC addresses
        """
        import json
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

    @mcp.tool()
    def dns_lookup(hostname: str, record_type: str = "A") -> str:
        """
        Perform DNS lookup.

        Args:
            hostname: Hostname or domain name
            record_type: DNS record type - A, AAAA, MX, NS, TXT (default: A)

        Returns:
            JSON string with DNS records
        """
        import json
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
