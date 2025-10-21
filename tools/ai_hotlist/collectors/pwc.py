from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup
from ..utils import parse_date


PWC_TRENDING_URL = "https://paperswithcode.com/trending"


def collect_pwc_trending() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    try:
        resp = requests.get(PWC_TRENDING_URL, timeout=20)
        if resp.status_code != 200:
            return items
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.paper-card")
        rank = 0
        for card in cards:
            rank += 1
            title_el = card.select_one("h1 a")
            if not title_el:
                title_el = card.select_one("h2 a")
            title = title_el.get_text(strip=True) if title_el else None
            url = "https://paperswithcode.com" + title_el.get("href", "") if title_el else None
            abstract_el = card.select_one("p.item-strip-abstract")
            abstract = abstract_el.get_text(strip=True) if abstract_el else ""
            date_el = card.select_one("span[itemprop='datePublished']")
            date = parse_date(date_el.get_text(strip=True)) if date_el else None
            if not title or not url:
                continue
            items.append(
                {
                    "type": "paper",
                    "title": title,
                    "url": url,
                    "summary": abstract,
                    "date": date,
                    "source": "Papers with Code",
                    "metrics": {
                        "pwc_trending_rank": rank,
                    },
                }
            )
    except Exception:
        return items
    return items
