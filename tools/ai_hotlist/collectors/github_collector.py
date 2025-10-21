from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import os
import requests
from ..utils import within_days, parse_date

GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/vnd.github+json"})
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def search_repos(self, q: str, sort: str = "stars", order: str = "desc", per_page: int = 50) -> List[Dict[str, Any]]:
        url = f"{GITHUB_API}/search/repositories"
        params = {"q": q, "sort": sort, "order": order, "per_page": per_page}
        r = self.session.get(url, params=params, timeout=30)
        if r.status_code != 200:
            return []
        data = r.json()
        return data.get("items", [])


def collect_github(days: int, token: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    client = GitHubClient(token)
    since_date = (datetime.utcnow() - timedelta(days=days)).date().isoformat()
    q_created = f"created:>={since_date}"
    repos = client.search_repos(q_created, sort="stars", order="desc", per_page=min(100, limit))
    items: List[Dict[str, Any]] = []
    for r in repos:
        title = r.get("full_name")
        url = r.get("html_url")
        desc = r.get("description")
        created_at = parse_date(r.get("created_at"))
        if not within_days(created_at, days):
            continue
        item = {
            "type": "open-source",
            "title": title,
            "url": url,
            "summary": desc,
            "date": created_at,
            "source": "GitHub",
            "metrics": {
                "stars": r.get("stargazers_count"),
                "forks": r.get("forks_count"),
                "language": r.get("language"),
            },
        }
        items.append(item)
    return items


def collect_github_trending() -> List[Dict[str, Any]]:
    # Scrape trending monthly page
    import requests
    from bs4 import BeautifulSoup

    url = "https://github.com/trending?since=monthly"
    items: List[Dict[str, Any]] = []
    try:
        r = requests.get(url, timeout=30, headers={"Accept": "text/html,application/xhtml+xml"})
        if r.status_code != 200:
            return items
        soup = BeautifulSoup(r.text, "html.parser")
        li = soup.select("article.Box-row")
        rank = 0
        for row in li:
            rank += 1
            h2 = row.select_one("h2 a")
            if not h2:
                continue
            full_name = h2.get_text(strip=True).replace("\n", "").replace(" ", "")
            href = h2.get("href")
            url = f"https://github.com{href}"
            lang_el = row.select_one("span[itemprop='programmingLanguage']")
            lang = lang_el.get_text(strip=True) if lang_el else None
            # Stars text (today or period)
            star_spans = row.select("a Link--muted"); new_stars = None
            # More robust parse of "stars added" line
            added_el = row.find(text=lambda t: t and "stars" in t and "since" in t)
            if added_el:
                try:
                    new_stars = int("".join([ch for ch in added_el if ch.isdigit()]))
                except Exception:
                    new_stars = None
            items.append(
                {
                    "type": "open-source",
                    "title": full_name,
                    "url": url,
                    "summary": None,
                    "date": None,
                    "source": "GitHub Trending",
                    "metrics": {
                        "trending_rank": rank,
                        "new_stars": new_stars,
                        "language": lang,
                    },
                }
            )
    except Exception:
        return items
    return items
