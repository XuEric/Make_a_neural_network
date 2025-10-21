#!/usr/bin/env python3
import argparse
import os
from typing import Any, Dict, List, Tuple
from datetime import datetime

from .config import DEFAULT_CONFIG, HotlistConfig
from .utils import ensure_dirs, normalize_text, merge_metrics, dump_json, format_date
from .collectors.news import collect_news
from .collectors.arxiv_collector import collect_arxiv
from .collectors.pwc import collect_pwc_trending
from .collectors.github_collector import collect_github, collect_github_trending
from .collectors.hf_collector import collect_hf_models, collect_hf_datasets
from .summarizer import apply_cn_summary
from .scoring import score_item


def filter_by_keywords(items: List[Dict[str, Any]], allow: List[str], deny: List[str]) -> List[Dict[str, Any]]:
    if not allow and not deny:
        return items
    out = []
    for it in items:
        text = f"{it.get('title') or ''} {it.get('summary') or ''}"
        t = normalize_text(text)
        passed = True
        if allow:
            passed = any(a.lower() in t for a in allow)
        if passed and deny:
            if any(d.lower() in t for d in deny):
                passed = False
        if passed:
            out.append(it)
    return out


def deduplicate(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_keys = {}
    out: List[Dict[str, Any]] = []
    for it in items:
        key = normalize_text(it.get("title") or it.get("url") or "")
        if not key:
            out.append(it)
            continue
        if key not in seen_keys:
            seen_keys[key] = it
            out.append(it)
        else:
            prev = seen_keys[key]
            prev["metrics"] = merge_metrics(prev.get("metrics", {}), it.get("metrics", {}))
            # Prefer earliest date if missing
            if not prev.get("date") and it.get("date"):
                prev["date"] = it["date"]
    return out


def categorize(items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    news, papers, oss = [], [], []
    for it in items:
        if it.get("type") == "news":
            news.append(it)
        elif it.get("type") == "paper":
            papers.append(it)
        elif it.get("type") in ("open-source", "model"):
            oss.append(it)
    return news, papers, oss


def build_markdown(date_str: str, news: List[Dict[str, Any]], papers: List[Dict[str, Any]], oss: List[Dict[str, Any]]) -> str:
    def section(title: str, items: List[Dict[str, Any]]) -> str:
        lines = [f"## {title}"]
        for it in items:
            metrics = it.get("metrics", {})
            metrics_str = ", ".join([f"{k}: {v}" for k, v in metrics.items() if v is not None])
            lines.append(f"- [{it.get('title')}]({it.get('url')}) | 分数: {it.get('score')} | 热度: {metrics_str}")
            lines.append(f"  - {it.get('one_liner_cn')}")
            for h in it.get("highlights_cn", [])[:3]:
                lines.append(f"  - {h}")
        return "\n".join(lines)

    md = [
        f"# AI 30天最热精选清单（{date_str}）",
        "",
        "说明：基于公开信号自动抓取与汇总，包含新闻、论文与开源/模型，按综合热度排序。",
        "",
        section("新闻", news),
        "",
        section("论文", papers),
        "",
        section("开源/模型", oss),
        "",
        "注：信号来源包括 GitHub/Hugging Face 下载与 Star、Papers with Code 趋势、新闻源权重等。",
    ]
    return "\n".join(md)


def run(config: HotlistConfig) -> Dict[str, Any]:
    ensure_dirs(config.output_dir_data, config.output_dir_reports)

    items: List[Dict[str, Any]] = []

    # Collect
    try:
        items += collect_news(config.rss_feeds, config.days)
    except Exception:
        pass
    try:
        items += collect_arxiv(config.days)
    except Exception:
        pass
    try:
        items += collect_pwc_trending()
    except Exception:
        pass
    try:
        items += collect_github(config.days, token=os.environ.get(config.github_token_env))
    except Exception:
        pass
    try:
        items += collect_github_trending()
    except Exception:
        pass
    try:
        items += collect_hf_models(config.days)
    except Exception:
        pass
    try:
        items += collect_hf_datasets(config.days)
    except Exception:
        pass

    # Filter
    items = filter_by_keywords(items, config.allowlist, config.denylist)

    # Dedup
    items = deduplicate(items)

    # Score, summarize
    for it in items:
        it["score"] = score_item(it)
        it = apply_cn_summary(it)

    # Sort by score
    items = sorted(items, key=lambda x: x.get("score", 0), reverse=True)

    # Categorize and cap
    news, papers, oss = categorize(items)
    news = news[: config.max_items_per_section]
    papers = papers[: config.max_items_per_section]
    oss = oss[: config.max_items_per_section]

    # Export
    date_str = datetime.utcnow().strftime("%Y%m%d")
    raw_path = os.path.join(config.output_dir_data, f"ai_hotlist_raw_{date_str}.json")
    agg_path = os.path.join(config.output_dir_data, f"ai_hotlist_{date_str}.json")
    report_path = os.path.join(config.output_dir_reports, f"ai-hotlist-{date_str}.md")

    dump_json(raw_path, items)
    # Final aggregated structure
    agg = {
        "date": date_str,
        "news": news,
        "papers": papers,
        "open_source_and_models": oss,
    }
    dump_json(agg_path, agg)

    # Markdown report
    md = build_markdown(date_str, news, papers, oss)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    return {
        "raw": raw_path,
        "aggregated": agg_path,
        "report": report_path,
        "counts": {
            "total": len(items),
            "news": len(news),
            "papers": len(papers),
            "oss_models": len(oss),
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI 30天最热精选清单 - 抓取与中文摘要器")
    parser.add_argument("--days", type=int, default=DEFAULT_CONFIG.days, help="抓取时间窗口（天）")
    parser.add_argument("--allow", type=str, default=None, help="关键词白名单，逗号分隔")
    parser.add_argument("--deny", type=str, default=None, help="关键词黑名单，逗号分隔")
    parser.add_argument("--max-per-section", type=int, default=DEFAULT_CONFIG.max_items_per_section)
    parser.add_argument("--output-data", type=str, default=None, help="数据输出目录")
    parser.add_argument("--output-reports", type=str, default=None, help="报告输出目录")

    args = parser.parse_args()

    cfg = HotlistConfig(
        days=args.days,
        allowlist=[x.strip() for x in args.allow.split(",")] if args.allow else [],
        denylist=[x.strip() for x in args.deny.split(",")] if args.deny else [],
        max_items_per_section=args.max_per_section,
        output_dir_data=os.path.abspath(args.output_data) if args.output_data else DEFAULT_CONFIG.output_dir_data,
        output_dir_reports=os.path.abspath(args.output_reports) if args.output_reports else DEFAULT_CONFIG.output_dir_reports,
        rss_feeds=DEFAULT_CONFIG.rss_feeds,
        github_token_env=DEFAULT_CONFIG.github_token_env,
        hf_models_endpoint=DEFAULT_CONFIG.hf_models_endpoint,
        hf_datasets_endpoint=DEFAULT_CONFIG.hf_datasets_endpoint,
        pwc_trending_url=DEFAULT_CONFIG.pwc_trending_url,
    )

    result = run(cfg)
    print("生成完成：")
    for k, v in result.items():
        print(k, v)
