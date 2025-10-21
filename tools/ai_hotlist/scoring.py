from typing import Any, Dict
from .utils import safe_float


def score_item(item: Dict[str, Any]) -> float:
    t = item.get("type")
    m = item.get("metrics", {}) or {}
    base = 0.0

    if t == "news":
        # Base on source weight and presence on multiple feeds
        source_weight = safe_float(m.get("source_weight", 0))
        share_count = safe_float(m.get("share_count", 0))
        base = 10 + source_weight + 0.5 * share_count
    elif t == "paper":
        # Base on PWC trending, authors count
        authors = safe_float(m.get("authors", 1))
        pwc_trending = safe_float(m.get("pwc_trending_rank", 0))
        base = 25 + min(10, authors / 2.0) + (10 if pwc_trending > 0 else 0) + max(0, 5 - pwc_trending)
    elif t == "open-source":
        # GitHub stars and trending rank
        stars = safe_float(m.get("stars", 0))
        new_stars = safe_float(m.get("new_stars", 0))
        trending_rank = safe_float(m.get("trending_rank", 0))
        base = 20 + (stars ** 0.5) + (new_stars ** 0.5) + max(0, 10 - trending_rank)
    elif t == "model":
        # HF downloads
        downloads = safe_float(m.get("downloads_last_month", m.get("downloads", 0)))
        likes = safe_float(m.get("likes", 0))
        base = 20 + (downloads ** 0.5) + (likes ** 0.3)
    else:
        base = 10

    # Recency boost
    if item.get("date"):
        base += 2

    return round(base, 2)
