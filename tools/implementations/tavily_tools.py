"""
Tavily Tool Implementations
============================

Six client tools backed by the Tavily Python SDK, used as the platform's
web-access surface for non-Anthropic providers (MiniMax, OpenAI, DeepSeek).

Anthropic's native provider uses Anthropic's own server-side web_search and
web_fetch tools (see AI_infrastructure/core/unified_ai_client.py:516-544).
This module is the platform's client-side equivalent: same conceptual surface
(URL in, text out) but executed on our infrastructure via Tavily's REST API.

Tools in this module:
    tavily_search        - search the public web
    tavily_extract       - fetch + clean text from one or more URLs
    tavily_crawl         - recursively crawl a website
    tavily_map           - discover URLs on a site without reading them
    tavily_research      - start an async deep-research task
    tavily_get_research  - poll an async research task

Credentials are resolved through the platform's 4-tier resolver
(AI_infrastructure/shared/org_credentials_loader.py):
    1. user_platform_credentials (per-user)
    2. organisation_platform_credentials (org vault, Fernet-encrypted)
    3. sub-user inheritance (owner creds inherited)
    4. TAVILY_API_KEY env var (Render/host-level fallback)

This module is intentionally NOT a plugin (does not live under
UI/modules_external/) because Tavily is a server-side integration, not a
UI module.
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path so the AI_agents root is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Defer Tavily SDK import to function call time so a missing SDK does not
# break module import (e.g. on a host where the package has not been pip-installed
# yet). This matches the pattern used in other tool modules that depend on
# optional third-party packages.


_TAVILY_CLIENT_CACHE: Dict[int, Any] = {}


def _get_tavily_client(user_id: Optional[int] = None):
    """
    Resolve the Tavily API key through the 4-tier resolver and return a
    cached TavilyClient instance.

    Args:
        user_id: The authenticated user ID. Used for Tier 1/2/3 lookup.
                 If None, only the env-var Tier 4 fallback is consulted.

    Returns:
        tavily.TavilyClient instance.

    Raises:
        RuntimeError: If no API key is found in any tier.
    """
    cache_key = user_id or 0
    if cache_key in _TAVILY_CLIENT_CACHE:
        return _TAVILY_CLIENT_CACHE[cache_key]

    api_key: Optional[str] = None

    # Try the 4-tier resolver if we have a user_id
    if user_id is not None:
        try:
            from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
            api_key = resolve_credentials(user_id, "tavily")
        except Exception:
            # Resolver unavailable (e.g. during a local test or cold start) -
            # fall through to env var. Do not raise here; let the env-var
            # check below decide.
            api_key = None

    if not api_key:
        api_key = os.environ.get("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Tavily API key not found. Set TAVILY_API_KEY in the host "
            "environment (e.g. Render env vars), or add a 'tavily' row to "
            "organisation_platform_credentials for the user's org."
        )

    # Import the SDK at call time so a missing tavily package does not break
    # the rest of the registry on import.
    try:
        from tavily import TavilyClient
    except ImportError as e:
        raise RuntimeError(
            "tavily-python is not installed. Add `tavily-python` to "
            "requirements.txt and run `pip install -r requirements.txt`."
        ) from e

    client = TavilyClient(api_key=api_key)
    _TAVILY_CLIENT_CACHE[cache_key] = client
    return client


def _is_truthy(value: Any) -> bool:
    """Coerce string truthy/falsy to bool (the model often sends 'true'/'false')."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def _coerce_int(value: Any, default: int, min_val: int = 1, max_val: int = 1000) -> int:
    """Coerce and clamp an integer parameter."""
    if value is None or value == "":
        return default
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    return max(min_val, min(max_val, n))


def _tavily_call(tool_name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrap a Tavily SDK call with logging, error envelope, and user feedback
    for the intelligence logger.
    """
    user_id = kwargs.get("_user_id")
    client = _get_tavily_client(user_id=user_id)
    method = getattr(client, tool_name.replace("tavily_", ""))
    start = time.time()
    try:
        result = method(**{k: v for k, v in kwargs.items() if not k.startswith("_")})
        elapsed_ms = int((time.time() - start) * 1000)
        print(f"[TAVILY] {tool_name} OK in {elapsed_ms}ms (user_id={user_id})")
        # Normalise the response to a platform-standard envelope
        if isinstance(result, dict):
            return {"success": True, "provider": "tavily", "tool": tool_name, **result}
        return {"success": True, "provider": "tavily", "tool": tool_name, "data": result}
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        print(f"[TAVILY] {tool_name} FAILED in {elapsed_ms}ms: {e}")
        return {
            "success": False,
            "provider": "tavily",
            "tool": tool_name,
            "error": str(e),
            "details": repr(e),
        }


# ============================================================================
# 1. tavily_search
# ============================================================================
def tavily_search(query: str, max_results: Any = 5, search_depth: str = "basic",
                  topic: str = "general", include_answer: Any = False,
                  include_raw_content: Any = False,
                  include_domains: Optional[List[str]] = None,
                  **kwargs):
    """
    Search the public web via Tavily.

    Args:
        query: The search query (1-400 chars).
        max_results: 1-20 (default 5).
        search_depth: 'basic' (default) or 'advanced'.
        topic: 'general' (default) or 'news'.
        include_answer: Include Tavily's short synthesised answer (default False).
        include_raw_content: Include full page text per result (default False).
        include_domains: Optional list of domain strings to restrict to.
        **kwargs: Reserved (_user_id, _session_id, etc.).

    Returns:
        {"success": True, "query": ..., "results": [...], "answer"?: ...}
    """
    params = {
        "query": query,
        "max_results": _coerce_int(max_results, default=5, min_val=1, max_val=20),
        "search_depth": search_depth if search_depth in ("basic", "advanced") else "basic",
        "topic": topic if topic in ("general", "news") else "general",
        "include_answer": _is_truthy(include_answer),
        "include_raw_content": _is_truthy(include_raw_content),
    }
    if include_domains:
        params["include_domains"] = include_domains
    return _tavily_call("tavily_search", {**params, **kwargs})


# ============================================================================
# 2. tavily_extract
# ============================================================================
def tavily_extract(urls: List[str], include_images: Any = False, **kwargs):
    """
    Fetch and clean-extract content from one or more URLs (up to 20 per call).

    Args:
        urls: List of 1-20 http(s) URLs.
        include_images: Include images found on the pages (default False).
        **kwargs: Reserved.

    Returns:
        {"success": True, "results": [{url, raw_content, images?}],
         "failed_results": [...]}
    """
    if isinstance(urls, str):
        # Tolerate the model passing a single URL as a string
        urls = [urls]
    if not urls:
        return {"success": False, "error": "urls is required (1-20 URLs)"}
    if len(urls) > 20:
        urls = urls[:20]
    return _tavily_call(
        "tavily_extract",
        {"urls": list(urls), "include_images": _is_truthy(include_images), **kwargs},
    )


# ============================================================================
# 3. tavily_crawl
# ============================================================================
def tavily_crawl(url: str, max_depth: Any = 2, limit: Any = 10,
                 instructions: Optional[str] = None, **kwargs):
    """
    Recursively crawl a website starting from `url`.

    Args:
        url: Starting URL (http/https).
        max_depth: 1-5 link-hops from start (default 2).
        limit: 1-50 max pages (default 10).
        instructions: Optional natural-language guidance.
        **kwargs: Reserved.

    Returns:
        {"success": True, "base_url": ..., "results": [{url, raw_content}, ...]}

    NOTE: /crawl is invite-only on Tavily. On 402/403 the response is
    {"success": False, "error": "..."}; fall back to tavily_map + tavily_extract.
    """
    params = {
        "url": url,
        "max_depth": _coerce_int(max_depth, default=2, min_val=1, max_val=5),
        "limit": _coerce_int(limit, default=10, min_val=1, max_val=50),
    }
    if instructions:
        params["instructions"] = instructions
    return _tavily_call("tavily_crawl", {**params, **kwargs})


# ============================================================================
# 4. tavily_map
# ============================================================================
def tavily_map(url: str, max_depth: Any = 2, limit: Any = 25,
               instructions: Optional[str] = None, **kwargs):
    """
    Discover the URL structure of a site without extracting page content.

    Args:
        url: Starting URL.
        max_depth: 1-5 (default 2).
        limit: 1-100 URLs to return (default 25).
        instructions: Optional natural-language guidance.
        **kwargs: Reserved.

    Returns:
        {"success": True, "base_url": ..., "results": [url, url, ...]}
    """
    params = {
        "url": url,
        "max_depth": _coerce_int(max_depth, default=2, min_val=1, max_val=5),
        "limit": _coerce_int(limit, default=25, min_val=1, max_val=100),
    }
    if instructions:
        params["instructions"] = instructions
    return _tavily_call("tavily_map", {**params, **kwargs})


# ============================================================================
# 5. tavily_research
# ============================================================================
def tavily_research(input: str, model: str = "mini",
                    citation_format: str = "apa", **kwargs):
    """
    Submit an asynchronous deep research task to Tavily.

    Args:
        input: The research question/topic. Specific and detailed yields better synthesis.
        model: 'mini' (default, fast) or 'pro' (slower, more thorough).
        citation_format: 'apa' (default), 'mla', 'chicago', 'vancouver', 'harvard', 'ieee'.
        **kwargs: Reserved.

    Returns:
        {"success": True, "request_id": "..."}  - poll via tavily_get_research.
    """
    params = {
        "input": input,
        "model": model if model in ("mini", "pro", "auto") else "mini",
        "citation_format": citation_format
            if citation_format in ("apa", "mla", "chicago", "vancouver", "harvard", "ieee")
            else "apa",
    }
    return _tavily_call("tavily_research", {**params, **kwargs})


# ============================================================================
# 6. tavily_get_research
# ============================================================================
def tavily_get_research(request_id: str, **kwargs):
    """
    Poll for the result of a research task started by tavily_research.

    Args:
        request_id: The request_id returned from tavily_research.
        **kwargs: Reserved.

    Returns:
        {"success": True, "status": "pending"|"completed", "content"?: str, "sources"?: [...]}
    """
    if not request_id:
        return {"success": False, "error": "request_id is required"}
    return _tavily_call("tavily_get_research", {"request_id": request_id, **kwargs})


if __name__ == "__main__":
    print("Tavily tools loaded (6 tools: search, extract, crawl, map, research, get_research)")
