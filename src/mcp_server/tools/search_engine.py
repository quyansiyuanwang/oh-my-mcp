"""
高级搜索引擎管理模块

提供功能:
- 多搜索引擎支持 (DuckDuckGo, Bing, Google, Baidu)
- 智能缓存机制
- 请求限流保护
- 并行搜索
- 结果去重
"""

import hashlib
import json
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup

from ..utils import logger


class SearchCache:
    """搜索缓存管理器"""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        """
        初始化缓存

        Args:
            ttl_seconds: 缓存过期时间(秒)，默认1小时
            max_size: 最大缓存条目数
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.cache: dict[str, dict[str, Any]] = {}
        self.lock = Lock()
        self.hits = 0  # 缓存命中次数
        self.misses = 0  # 缓存未命中次数

    def _generate_key(self, query: str, engine: str, params: dict[str, Any]) -> str:
        """生成缓存键"""
        data = f"{engine}:{query}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()

    def get(
        self, query: str, engine: str, params: dict[str, Any]
    ) -> Optional[list[dict[str, Any]]]:
        """获取缓存的搜索结果"""
        key = self._generate_key(query, engine, params)

        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                # 检查是否过期
                if datetime.now() < entry["expires_at"]:
                    self.hits += 1
                    logger.info(f"Cache hit for {engine}:{query}")
                    result_list: list[dict[str, Any]] = entry["results"]
                    return result_list
                else:
                    # 删除过期条目
                    del self.cache[key]
                    self.misses += 1
                    logger.info(f"Cache expired for {engine}:{query}")
            else:
                self.misses += 1

        return None

    def set(
        self, query: str, engine: str, params: dict[str, Any], results: list[dict[str, Any]]
    ) -> None:
        """设置缓存"""
        key = self._generate_key(query, engine, params)

        with self.lock:
            # 如果缓存满了，删除最老的条目
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["created_at"])
                del self.cache[oldest_key]
                logger.info("Cache full, removed oldest entry")

            self.cache[key] = {
                "results": results,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(seconds=self.ttl_seconds),
            }
            logger.info(f"Cached results for {engine}:{query}")

    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            total = len(self.cache)
            expired = sum(
                1 for entry in self.cache.values() if datetime.now() >= entry["expires_at"]
            )
            return {
                "total_entries": total,
                "expired_entries": expired,
                "active_entries": total - expired,
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
            }


class RateLimiter:
    """请求限流器"""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        初始化限流器

        Args:
            max_requests: 窗口期内最大请求数
            window_seconds: 时间窗口(秒)
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = {}
        self.lock = Lock()

    def is_allowed(self, key: str = "default") -> bool:
        """检查是否允许请求"""
        now = time.time()

        with self.lock:
            if key not in self.requests:
                self.requests[key] = []

            # 清理过期的请求记录
            cutoff = now - self.window_seconds
            self.requests[key] = [t for t in self.requests[key] if t > cutoff]

            # 检查是否超过限制
            if len(self.requests[key]) >= self.max_requests:
                logger.warning(
                    f"Rate limit exceeded for {key}: {len(self.requests[key])}/{self.max_requests}"
                )
                return False

            # 记录本次请求
            self.requests[key].append(now)
            return True

    def wait_time(self, key: str = "default") -> float:
        """获取需要等待的时间(秒)"""
        now = time.time()

        with self.lock:
            if key not in self.requests or len(self.requests[key]) < self.max_requests:
                return 0.0

            # 找到最老的请求
            oldest = min(self.requests[key])
            wait_until = oldest + self.window_seconds
            return max(0.0, wait_until - now)

    def reset(self, key: Optional[str] = None) -> None:
        """重置限流器"""
        with self.lock:
            if key:
                self.requests.pop(key, None)
            else:
                self.requests.clear()
            logger.info(f"Rate limiter reset for {key if key else 'all keys'}")


class SearchEngine:
    """搜索引擎基类"""

    def __init__(self, name: str):
        self.name = name

    def search(self, query: str, max_results: int = 10, **kwargs: Any) -> list[dict[str, Any]]:
        """执行搜索"""
        raise NotImplementedError


class DuckDuckGoEngine(SearchEngine):
    """DuckDuckGo 搜索引擎"""

    def __init__(self) -> None:
        super().__init__("DuckDuckGo")

    def search(
        self, query: str, max_results: int = 10, is_news: bool = False, **kwargs: Any
    ) -> list[dict[str, Any]]:
        try:
            from ddgs import DDGS

            with DDGS() as ddgs:
                results = []
                search_method = ddgs.news if is_news else ddgs.text

                for i, result in enumerate(search_method(query, max_results=max_results)):
                    if i >= max_results:
                        break

                    if is_news:
                        results.append(
                            {
                                "title": result.get("title", ""),
                                "link": result.get("url", ""),
                                "snippet": result.get("body", ""),
                                "date": result.get("date", ""),
                                "source": result.get("source", ""),
                                "engine": self.name,
                            }
                        )
                    else:
                        results.append(
                            {
                                "title": result.get("title", ""),
                                "link": result.get("href", ""),
                                "snippet": result.get("body", ""),
                                "engine": self.name,
                            }
                        )

                logger.info(f"{self.name} search successful: {len(results)} results")
                return results

        except Exception as e:
            logger.error(f"{self.name} search failed: {e}")
            return []


class BingEngine(SearchEngine):
    """Bing 搜索引擎"""

    def __init__(self) -> None:
        super().__init__("Bing")

    def search(
        self, query: str, max_results: int = 10, is_news: bool = False, **kwargs: Any
    ) -> list[dict[str, Any]]:
        try:
            encoded_query = urllib.parse.quote(query)
            if is_news:
                search_url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss"
            else:
                search_url = f"https://www.bing.com/search?q={encoded_query}&format=rss"

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "xml")
            results = []

            items = soup.find_all("item", limit=max_results)
            for item in items:
                title = item.find("title")
                link = item.find("link")
                description = item.find("description")
                pubDate = item.find("pubDate")
                source = item.find("source")

                result: dict[str, Any] = {
                    "title": title.text if title else "",
                    "link": link.text if link else "",
                    "snippet": (
                        BeautifulSoup(
                            description.text if description else "", "html.parser"
                        ).get_text()
                        if description
                        else ""
                    ),
                    "engine": self.name,
                }

                if is_news:
                    result["date"] = pubDate.text if pubDate else ""
                    result["source"] = source.text if source else ""

                results.append(result)

            logger.info(f"{self.name} search successful: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"{self.name} search failed: {e}")
            return []


class GoogleEngine(SearchEngine):
    """Google 搜索引擎 (通过 Google Custom Search)"""

    def __init__(self) -> None:
        super().__init__("Google")

    def search(
        self, query: str, max_results: int = 10, is_news: bool = False, **kwargs: Any
    ) -> list[dict[str, Any]]:
        try:
            # 使用 Google Custom Search JSON API 或 RSS
            # 这里使用简单的 RSS 方式作为演示
            encoded_query = urllib.parse.quote(query)

            # Google News RSS
            if is_news:
                search_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            else:
                # 使用 Google 搜索的 HTML 抓取（受限但免费）
                search_url = f"https://www.google.com/search?q={encoded_query}&num={max_results}"

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()

            results = []

            if is_news:
                # 解析 RSS
                soup = BeautifulSoup(response.text, "xml")
                items = soup.find_all("item", limit=max_results)

                for item in items:
                    title = item.find("title")
                    link = item.find("link")
                    description = item.find("description")
                    pubDate = item.find("pubDate")

                    results.append(
                        {
                            "title": title.text if title else "",
                            "link": link.text if link else "",
                            "snippet": (
                                BeautifulSoup(
                                    description.text if description else "", "html.parser"
                                ).get_text()
                                if description
                                else ""
                            ),
                            "date": pubDate.text if pubDate else "",
                            "source": "Google News",
                            "engine": self.name,
                        }
                    )
            else:
                # 解析 HTML（简化版）
                soup = BeautifulSoup(response.text, "html.parser")
                search_results = soup.find_all("div", class_="g", limit=max_results)

                for item in search_results:
                    title_elem = item.find("h3")
                    link_elem = item.find("a")
                    snippet_elem = item.find("div", class_=["VwiC3b", "s"])

                    if title_elem and link_elem:
                        results.append(
                            {
                                "title": title_elem.get_text(),
                                "link": link_elem.get("href", ""),
                                "snippet": snippet_elem.get_text() if snippet_elem else "",
                                "engine": self.name,
                            }
                        )

            logger.info(f"{self.name} search successful: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"{self.name} search failed: {e}")
            return []


class BaiduEngine(SearchEngine):
    """Baidu 搜索引擎"""

    def __init__(self) -> None:
        super().__init__("Baidu")

    def search(
        self, query: str, max_results: int = 10, is_news: bool = False, **kwargs: Any
    ) -> list[dict[str, Any]]:
        try:
            encoded_query = urllib.parse.quote(query, encoding="gbk", errors="ignore")

            if is_news:
                search_url = f"https://www.baidu.com/s?tn=news&rtt=1&bsst=1&wd={encoded_query}"
            else:
                search_url = f"https://www.baidu.com/s?wd={encoded_query}&rn={max_results}"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.baidu.com/",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Cache-Control": "max-age=0",
            }

            response = requests.get(search_url, headers=headers, timeout=15)
            response.encoding = "utf-8"
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            # 解析百度搜索结果 - 尝试多种选择器模式
            # 百度的 DOM 结构：可能是 .result, .c-container, 或其他类名
            search_results = soup.find_all("div", class_="result", limit=max_results)
            if not search_results:
                # 尝试新版百度页面结构
                search_results = soup.find_all("div", class_="c-container", limit=max_results)
            if not search_results:
                # 再尝试通用结构
                search_results = soup.find_all("div", attrs={"mu": True}, limit=max_results)

            for item in search_results:
                # 尝试多种标题选择器
                title_elem = item.find("h3") or item.find("a", class_="c-title")
                # 尝试多种链接选择器
                link_elem = item.find("a") or title_elem
                # 尝试多种摘要选择器
                snippet_elem = (
                    item.find("div", class_="c-abstract")
                    or item.find("div", class_="c-span9")
                    or item.find("div", class_="c-span-last")
                )

                if title_elem and link_elem:
                    title = title_elem.get_text().strip()
                    href = link_elem.get("href", "")
                    link = str(href) if href else ""

                    # 百度链接可能是重定向链接，需要提取真实URL
                    if link.startswith("http://www.baidu.com/link?url=") or link.startswith(
                        "https://www.baidu.com/link?url="
                    ):
                        # 尝试从 mu 属性获取真实URL
                        real_link_attr = item.get("mu")
                        real_link = str(real_link_attr) if real_link_attr else ""
                        if real_link:
                            link = (
                                real_link if real_link.startswith("http") else f"http://{real_link}"
                            )
                    elif not link.startswith("http"):
                        link = (
                            f"https://www.baidu.com{link}"
                            if link.startswith("/")
                            else f"https://{link}"
                        )

                    result: dict[str, Any] = {
                        "title": title,
                        "link": link,
                        "snippet": (
                            snippet_elem.get_text().strip()
                            if snippet_elem
                            else "No description available"
                        ),
                        "engine": self.name,
                    }

                    if is_news:
                        date_elem = item.find("span", class_="c-color-gray2")
                        source_elem = item.find("span", class_="c-gap-right")
                        result["date"] = date_elem.get_text() if date_elem else ""
                        result["source"] = source_elem.get_text() if source_elem else "Baidu"

                    results.append(result)

            logger.info(f"{self.name} search successful: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"{self.name} search failed: {e}")
            return []


class SearchManager:
    """搜索管理器 - 协调多个搜索引擎"""

    def __init__(
        self,
        cache_ttl: int = 3600,
        cache_size: int = 1000,
        rate_limit_requests: int = 10,
        rate_limit_window: int = 60,
    ):
        self.cache = SearchCache(ttl_seconds=cache_ttl, max_size=cache_size)
        self.rate_limiter = RateLimiter(
            max_requests=rate_limit_requests, window_seconds=rate_limit_window
        )

        # 初始化搜索引擎
        self.engines: dict[str, SearchEngine] = {
            "duckduckgo": DuckDuckGoEngine(),
            "bing": BingEngine(),
            "google": GoogleEngine(),
            "baidu": BaiduEngine(),
        }

    def search(
        self,
        query: str,
        max_results: int = 10,
        engines: Optional[list[str]] = None,
        parallel: bool = False,
        use_cache: bool = True,
        is_news: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        执行搜索

        Args:
            query: 搜索查询
            max_results: 最大结果数
            engines: 使用的搜索引擎列表，None 表示使用默认顺序
            parallel: 是否并行搜索多个引擎
            use_cache: 是否使用缓存
            is_news: 是否搜索新闻
            **kwargs: 其他参数

        Returns:
            搜索结果字典
        """
        if engines is None:
            engines = ["duckduckgo", "bing"]  # 默认引擎

        # 注意：限流检查移到了每个引擎内部，实现引擎级独立限流

        results: list[dict[str, Any]] = []
        errors: list[str] = []
        engines_used: list[str] = []
        from_cache = False

        if parallel and len(engines) > 1:
            # 并行搜索
            results = self._parallel_search(query, max_results, engines, use_cache, is_news)
            engines_used = [r["engine"] for r in results if "engine" in r]
            engines_used = list(dict.fromkeys(engines_used))  # 去重
        else:
            # 串行搜索（带故障转移）
            for engine_name in engines:
                if engine_name not in self.engines:
                    errors.append(f"Unknown engine: {engine_name}")
                    continue

                # 检查该引擎的限流状态
                rate_key = f"{engine_name}:{query}"
                if not self.rate_limiter.is_allowed(rate_key):
                    wait_time = self.rate_limiter.wait_time(rate_key)
                    errors.append(f"{engine_name}: Rate limit exceeded (wait {wait_time:.1f}s)")
                    logger.warning(f"{engine_name} rate limited for query: {query}")
                    continue  # 尝试下一个引擎

                # 尝试从缓存获取
                if use_cache:
                    cached = self.cache.get(
                        query, engine_name, {"max_results": max_results, "is_news": is_news}
                    )
                    if cached:
                        results = cached
                        engines_used.append(engine_name)
                        from_cache = True
                        logger.info(f"Cache hit for {engine_name}:{query}")
                        break

                # 执行搜索
                engine = self.engines[engine_name]
                try:
                    engine_results = engine.search(query, max_results, is_news=is_news, **kwargs)

                    if engine_results:
                        results = engine_results
                        engines_used.append(engine_name)

                        # 缓存结果
                        if use_cache:
                            self.cache.set(
                                query,
                                engine_name,
                                {"max_results": max_results, "is_news": is_news},
                                results,
                            )
                        break

                except Exception as e:
                    errors.append(f"{engine_name}: {str(e)}")
                    logger.error(f"{engine_name} search error: {e}")

        # 去重
        if results:
            results = self._deduplicate_results(results)

        return {
            "success": len(results) > 0,
            "results": results,
            "count": len(results),
            "query": query,
            "engines_used": engines_used,
            "parallel": parallel,
            "from_cache": from_cache,
            "cached": use_cache and len(results) > 0,
            "errors": errors if errors else None,
        }

    def _parallel_search(
        self,
        query: str,
        max_results: int,
        engines: list[str],
        use_cache: bool,
        is_news: bool,
    ) -> list[dict[str, Any]]:
        """并行搜索多个引擎"""
        all_results: list[dict[str, Any]] = []

        def search_engine(engine_name: str) -> list[dict[str, Any]]:
            if engine_name not in self.engines:
                return []

            # 检查该引擎的限流状态
            rate_key = f"{engine_name}:{query}"
            if not self.rate_limiter.is_allowed(rate_key):
                wait_time = self.rate_limiter.wait_time(rate_key)
                logger.warning(
                    f"{engine_name} rate limited for query: {query} (wait {wait_time:.1f}s)"
                )
                return []  # 该引擎被限流，不影响其他引擎

            # 检查缓存
            if use_cache:
                cached = self.cache.get(
                    query, engine_name, {"max_results": max_results, "is_news": is_news}
                )
                if cached:
                    return cached

            # 执行搜索
            engine = self.engines[engine_name]
            try:
                results = engine.search(query, max_results, is_news=is_news)
                if results and use_cache:
                    self.cache.set(
                        query,
                        engine_name,
                        {"max_results": max_results, "is_news": is_news},
                        results,
                    )
                return results
            except Exception as e:
                logger.error(f"Parallel search error for {engine_name}: {e}")
                return []

        # 使用线程池并行执行
        with ThreadPoolExecutor(max_workers=len(engines)) as executor:
            future_to_engine = {
                executor.submit(search_engine, engine): engine for engine in engines
            }

            for future in as_completed(future_to_engine):
                try:
                    results = future.result()
                    if results:
                        all_results.extend(results)
                except Exception as e:
                    logger.error(f"Parallel search future error: {e}")

        return all_results[:max_results]  # 限制总结果数

    def _deduplicate_results(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """去重搜索结果"""
        seen_urls: set[str] = set()
        seen_titles: set[str] = set()
        unique_results: list[dict[str, Any]] = []

        for result in results:
            url = result.get("link", "").strip()
            title = result.get("title", "").strip().lower()

            # 标准化 URL
            url_normalized = url.split("?")[0].rstrip("/")  # 移除查询参数和尾部斜杠

            # 检查 URL 和标题是否已存在
            if url_normalized and url_normalized not in seen_urls:
                if title not in seen_titles:
                    seen_urls.add(url_normalized)
                    seen_titles.add(title)
                    unique_results.append(result)

        logger.info(f"Deduplicated: {len(results)} -> {len(unique_results)} results")
        return unique_results

    def get_cache_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.cache.hits + self.cache.misses
        hit_rate = (self.cache.hits / total_requests * 100) if total_requests > 0 else 0.0

        return {
            "size": len(self.cache.cache),
            "max_size": self.cache.max_size,
            "hits": self.cache.hits,
            "misses": self.cache.misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self.cache.ttl_seconds,
        }

    def clear_cache(self) -> int:
        """清除所有缓存"""
        with self.cache.lock:
            count = len(self.cache.cache)
            self.cache.cache.clear()
            logger.info(f"Cleared {count} cache entries")
            return count


# 全局搜索管理器实例
_search_manager: Optional[SearchManager] = None


def get_search_manager() -> SearchManager:
    """获取全局搜索管理器实例"""
    global _search_manager
    if _search_manager is None:
        _search_manager = SearchManager()
    return _search_manager
