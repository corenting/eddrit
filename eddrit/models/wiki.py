from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WikiPage:
    page_name: str
    subreddit_name: str
    content_html: str
