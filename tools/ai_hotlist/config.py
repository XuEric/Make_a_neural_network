import os
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class HotlistConfig:
    days: int = 30
    allowlist: List[str] = field(default_factory=list)
    denylist: List[str] = field(default_factory=list)
    max_items_per_section: int = 100
    output_dir_data: str = os.path.abspath(os.path.join(os.getcwd(), "data"))
    output_dir_reports: str = os.path.abspath(os.path.join(os.getcwd(), "reports"))

    # Sources
    rss_feeds: List[str] = field(
        default_factory=lambda: [
            # Chinese AI media - availability may vary
            "https://www.qbitai.com/feed",  # 量子位（WordPress）
            # Add more if available; parsing is resilient to failures
            "https://ai.googleblog.com/feeds/posts/default",  # Google AI Blog
            "https://openai.com/blog/rss.xml",  # OpenAI Blog
            "https://rsshub.app/zhihu/collection/26444956",  # RSSHub mirror of AI topics (if accessible)
        ]
    )

    # GitHub API token (optional)
    github_token_env: str = "GITHUB_TOKEN"

    # Hugging Face endpoints
    hf_models_endpoint: str = "https://huggingface.co/api/models"
    hf_datasets_endpoint: str = "https://huggingface.co/api/datasets"

    # Papers With Code
    pwc_trending_url: str = "https://paperswithcode.com/trending"


DEFAULT_CONFIG = HotlistConfig()
