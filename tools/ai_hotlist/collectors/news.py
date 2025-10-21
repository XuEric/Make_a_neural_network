from typing import Any, Dict, List
from datetime import datetime

import feedparser

from ..utils import parse_date, within_days, normalize_url


NEWS_SOURCE_WEIGHTS = {
    "量子位": 3,
    "机器之心": 3,
    "AI 前线": 2,
    "36Kr": 2,
    "钛媒体": 2,
    "OpenAI": 3,
    "Google AI Blog": 3,
}


def guess_source(entry: Any, feed_url: str) -> str:
    src = (
        getattr(entry, "source", None)
        or getattr(entry, "author", None)
        or getattr(entry, "authors", None)
        or getattr(entry, "publisher", None)
    )
    if isinstance(src, list) and src:
        src = src[0]
    if isinstance(src, dict):
        src = src.get("title") or src.get("name")
    if not src:
        if "qbitai" in feed_url:
            src = "量子位"
        elif "openai.com" in feed_url:
            src = "OpenAI"
        elif "ai.googleblog" in feed_url:
            src = "Google AI Blog"
        else:
            src = "RSS"
    return str(src)


def collect_news(feeds: List[str], days: int) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for url in feeds:
        try:
            parsed = feedparser.parse(url)
        except Exception:
            continue
        entries = getattr(parsed, "entries", []) or []
        for e in entries:
            link = normalize_url(getattr(e, "link", ""))
            title = getattr(e, "title", "")
            summary = getattr(e, "summary", getattr(e, "description", ""))
            published = None
            for k in ["published", "updated", "created"]:
                if hasattr(e, k):
                    published = parse_date(getattr(e, k))
                    if published:
                        break
            if not within_days(published, days):
                continue
            source = guess_source(e, url)
            weight = NEWS_SOURCE_WEIGHTS.get(source, 1)
            item = {
                "type": "news",
                "title": title,
                "url": link,
                "summary": summary,
                "date": published,
                "source": source,
                "metrics": {
                    "source_weight": weight,
                },
            }
            items.append(item)
    return items
