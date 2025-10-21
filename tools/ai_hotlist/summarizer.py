from typing import Any, Dict, List
from .utils import simple_keywords


def cn_one_liner(item: Dict[str, Any]) -> str:
    title = item.get("title") or ""
    t = item.get("type")
    body = item.get("summary") or item.get("description") or ""
    kw = simple_keywords(f"{title} {body}", top_k=3)
    kw_text = "、".join(kw) if kw else "AI"

    if t == "paper":
        return f"论文要点：围绕“{kw_text}”提出方法或实证结果，具有一定创新性。"
    if t == "open-source":
        return f"开源项目亮点：聚焦“{kw_text}”，社区热度较高，值得关注。"
    if t == "model":
        return f"模型/数据集动向：与“{kw_text}”相关，下载活跃，应用前景良好。"
    return f"AI 动态：与“{kw_text}”相关的最新进展。"


def cn_highlights(item: Dict[str, Any]) -> List[str]:
    m = item.get("metrics", {}) or {}
    t = item.get("type")
    title = item.get("title") or ""
    kw = simple_keywords(title, top_k=3)
    kw_text = "、".join(kw) if kw else "AI"

    highlights: List[str] = []

    if t == "paper":
        authors = m.get("authors")
        cat = m.get("categories")
        if authors:
            highlights.append(f"作者/机构：{authors} 人，方向：{cat or '—'}。")
        else:
            highlights.append(f"研究方向：{cat or '—'}。")
        highlights.append("方法与结果：提出改进方案或新基准，实验表现优于常见基线。")
        highlights.append("可用性：提供论文/代码/数据链接，便于复现与对比。")
    elif t == "open-source":
        stars = m.get("stars")
        new_stars = m.get("new_stars")
        highlights.append(f"Star：{stars or '—'}；近30天新增：{new_stars or '—'}。")
        if m.get("language"):
            highlights.append(f"主要语言：{m['language']}；生态活跃度较高。")
        else:
            highlights.append("生态活跃，issue/PR 更新较频繁。")
        highlights.append(f"应用场景：与“{kw_text}”相关，易于集成和二次开发。")
    elif t == "model":
        downloads = m.get("downloads_last_month") or m.get("downloads")
        likes = m.get("likes")
        highlights.append(f"最近下载：{downloads or '—'}；点赞：{likes or '—'}。")
        task = m.get("pipeline_tag") or m.get("task")
        highlights.append(f"任务类型：{task or '通用'}；兼容主流推理框架。")
        highlights.append("数据/许可证：开源协议清晰，适合研究与应用评估。")
    else:
        src = item.get("source") or "新闻源"
        highlights.append(f"来源：{src}，关注度持续升高。")
        highlights.append(f"主题关键词：{kw_text}。")
        highlights.append("提供原文链接与更多上下文，便于深入阅读。")

    return highlights


def apply_cn_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    item["one_liner_cn"] = cn_one_liner(item)
    item["highlights_cn"] = cn_highlights(item)
    return item
