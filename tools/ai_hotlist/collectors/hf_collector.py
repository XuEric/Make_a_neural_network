from typing import Any, Dict, List, Optional
import requests
from ..utils import parse_date, within_days


HF_MODELS_API = "https://huggingface.co/api/models"
HF_DATASETS_API = "https://huggingface.co/api/datasets"


def _fetch(endpoint: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    try:
        r = requests.get(endpoint, params=params or {}, timeout=30)
        if r.status_code != 200:
            return []
        return r.json()
    except Exception:
        return []


def collect_hf_models(days: int, limit: int = 100) -> List[Dict[str, Any]]:
    params = {"sort": "lastModified", "direction": -1, "limit": limit}
    data = _fetch(HF_MODELS_API, params=params)
    items: List[Dict[str, Any]] = []
    for m in data:
        last_modified = parse_date(m.get("lastModified"))
        if not within_days(last_modified, days):
            continue
        url = f"https://huggingface.co/{m.get('modelId') or m.get('id') or m.get('name')}"
        item = {
            "type": "model",
            "title": m.get("modelId") or m.get("id") or m.get("name"),
            "url": url,
            "summary": None,
            "date": last_modified,
            "source": "Hugging Face",
            "metrics": {
                "downloads": m.get("downloads"),
                "likes": m.get("likes"),
                "pipeline_tag": m.get("pipeline_tag"),
                "downloads_last_month": m.get("downloads_last_month") or m.get("downloadsLastMonth"),
            },
        }
        items.append(item)
    return items


def collect_hf_datasets(days: int, limit: int = 100) -> List[Dict[str, Any]]:
    params = {"sort": "lastModified", "direction": -1, "limit": limit}
    data = _fetch(HF_DATASETS_API, params=params)
    items: List[Dict[str, Any]] = []
    for d in data:
        last_modified = parse_date(d.get("lastModified"))
        if not within_days(last_modified, days):
            continue
        url = f"https://huggingface.co/datasets/{d.get('id') or d.get('name')}"
        item = {
            "type": "model",
            "title": d.get("id") or d.get("name"),
            "url": url,
            "summary": None,
            "date": last_modified,
            "source": "Hugging Face Datasets",
            "metrics": {
                "downloads": d.get("downloads"),
                "likes": d.get("likes"),
                "task": (d.get("cardData") or {}).get("task_categories"),
                "downloads_last_month": d.get("downloads_last_month") or d.get("downloadsLastMonth"),
            },
        }
        items.append(item)
    return items
