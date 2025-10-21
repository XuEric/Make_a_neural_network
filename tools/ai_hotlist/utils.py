import os
import re
import json
import math
import time
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytz
from dateutil import parser as dateparser


CHINESE_PUNCT = "，。；：？！“”‘’（）《》、——…"
PUNCT = set(string.punctuation + CHINESE_PUNCT)


def ensure_dirs(*paths: str) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)


def now_utc() -> datetime:
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def days_ago(days: int) -> datetime:
    return now_utc() - timedelta(days=days)


def parse_date(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=pytz.utc)
    try:
        dt = dateparser.parse(str(value))
        if not dt:
            return None
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=pytz.utc)
        return dt
    except Exception:
        return None


def within_days(dt: Optional[datetime], days: int) -> bool:
    if not dt:
        return False
    return dt >= days_ago(days)


def normalize_text(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    for ch in PUNCT:
        text = text.replace(ch, " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def simple_keywords(text: str, top_k: int = 5) -> List[str]:
    text = (text or "").lower()
    # Split by non-word, keep ascii words/numbers; Chinese not handled perfectly
    tokens = re.split(r"[^\w]+", text)
    stop = set(
        [
            "the",
            "and",
            "with",
            "this",
            "that",
            "for",
            "into",
            "from",
            "are",
            "was",
            "were",
            "have",
            "has",
            "had",
            "using",
            "use",
            "of",
            "in",
            "on",
            "to",
            "a",
            "an",
            "by",
            "we",
            "our",
            "is",
            "it",
            "as",
            "at",
            "be",
            "can",
            "via",
            "based",
            "model",
            "models",
            "paper",
            "method",
            "methods",
        ]
    )
    counts: Dict[str, int] = {}
    for t in tokens:
        if not t or len(t) <= 1:
            continue
        if t in stop:
            continue
        if any(ch.isdigit() for ch in t) and not any(ch.isalpha() for ch in t):
            continue
        counts[t] = counts.get(t, 0) + 1
    return [w for w, _ in sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:top_k]]


def dump_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def read_env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(name, default)


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def throttled_sleep(seconds: float) -> None:
    try:
        time.sleep(seconds)
    except Exception:
        pass


def pick_top(items: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    return items[:limit] if limit and limit > 0 else items


def merge_metrics(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if k not in out:
            out[k] = v
            continue
        av = out[k]
        try:
            if isinstance(av, (int, float)) and isinstance(v, (int, float)):
                out[k] = max(av, v)
            else:
                out[k] = av if av else v
        except Exception:
            out[k] = av or v
    return out


def normalize_url(url: str) -> str:
    if not url:
        return url
    url = url.strip()
    url = url.replace("http://", "https://")
    if url.endswith("/"):
        url = url[:-1]
    return url


def format_date(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    return dt.astimezone(pytz.timezone("UTC")).strftime("%Y-%m-%d")
