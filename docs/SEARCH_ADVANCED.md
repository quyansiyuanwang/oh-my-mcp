# Web Search Tools v2.0

English | [中文](SEARCH_ADVANCED.zh.md)

The web search suite was upgraded to a multi-engine, cached, parallel-capable
search system with rate limiting and automatic failover.

## Feature overview

| Feature | Description |
|---|---|
| Multi-engine | DuckDuckGo, Bing, Google, Baidu |
| Smart caching | results cached 1 hour (TTL 3600s, 1000 entries, LRU) |
| Parallel search | query multiple engines simultaneously |
| Result dedup | URL normalization + title similarity |
| Rate limiting | 10 requests / 60s sliding window |
| Failover | automatic switch to backup engines |

## Engines

- **DuckDuckGo** — privacy-focused, no ads; default first choice.
- **Bing** — comprehensive, stable; general and news.
- **Google** — richest results; handle anti-scraping.
- **Baidu** — best for Chinese content.

## Tools

```python
web_search(query: str, max_results: int = 10) -> str
# basic search with automatic failover (DuckDuckGo -> Bing)

web_search_advanced(
    query: str,
    max_results: int = 10,            # 1-50
    engines: str = "duckduckgo,bing", # engine list
    parallel: bool = False,
    use_cache: bool = True,
) -> str

web_search_news(query: str, max_results: int = 10) -> str
clear_search_cache() -> str
get_search_stats() -> str
```

`web_search_advanced` returns `results` (each with `title`, `link`,
`snippet`, `engine`), `count`, `engines_used`, `parallel`, `cached`,
`errors`.

## Recommended usage

- Daily: `web_search("query")`
- Important queries: `web_search_advanced(query, engines="duckduckgo,google,bing", parallel=True, max_results=30)`
- Chinese content: `engines="baidu,google"`
- News: `web_search_news("latest news", max_results=20)`

Parallel search cuts latency from 2–5s to 1–2s and roughly triples result
coverage; deduplication (URL normalization + title similarity) removes
duplicates while keeping each result's source engine.

## Caching and rate limits

- Cache hits drop responses from seconds to milliseconds and cut API calls
  by 90%+; disable per call with `use_cache=False`, clear with
  `clear_search_cache()`, inspect with `get_search_stats()`.
- Exceeding 10 requests per 60s returns
  `{"success": false, "error": "Rate limit exceeded. Please wait 15.3 seconds"}` —
  wait, or rely on the cache.

## Failover

Engines are tried in priority order; a single-engine attempt times out after
15s and failed engines are skipped. If DuckDuckGo hits a rate limit the
search automatically falls back to Bing.

## Migrating from v1.0

`web_search("query", max_results=10)` is fully compatible. New capabilities
are opt-in via `web_search_advanced`.
