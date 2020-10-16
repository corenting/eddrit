from dataclasses import dataclass
from typing import Optional


@dataclass
class Subreddit:
    title: str
    name: str
    show_thumbnails: bool
    public_description: Optional[str]
    over18: bool
