from typing import Any, Dict, List
from datetime import datetime

import arxiv

from ..utils import within_days, parse_date


ARXIV_CATEGORIES = ["cs.CL", "cs.LG", "cs.CV", "cs.AI"]


def collect_arxiv(days: int, max_results: int = 200) -> List[Dict[str, Any]]:
    query = " OR ".join([f"cat:{c}" for c in ARXIV_CATEGORIES])
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    items: List[Dict[str, Any]] = []
    for result in search.results():
        published = result.published or result.updated
        if not within_days(published, days):
            continue
        url = result.entry_id
        title = result.title.strip().replace("\n", " ")
        summary = (result.summary or "").strip().replace("\n", " ")
        authors = len(result.authors or [])
        cats = ",".join(result.categories or [])
        item = {
            "type": "paper",
            "title": title,
            "url": url,
            "summary": summary,
            "date": published,
            "source": "arXiv",
            "metrics": {
                "authors": authors,
                "categories": cats,
            },
            "links": {
                "pdf": getattr(result, "pdf_url", None),
            },
        }
        items.append(item)
    return items
