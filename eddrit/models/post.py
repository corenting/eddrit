from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional, Union

from eddrit.models.flair import Flair


class PostContentType(Enum):
    LINK = "link"
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"


@dataclass
class PostContent:
    content: Optional[str]
    type: PostContentType
    width: Optional[int] = None
    height: Optional[int] = None
    is_gif: Optional[bool] = False
    is_embed: Optional[bool] = False
    content_type: Optional[str] = None


@dataclass
class PostComment:
    id: str
    parent_id: str
    is_sticky: bool
    author: str
    is_submitter: bool
    is_admin: bool
    content: str
    children: Iterable[Union[PostComment, PostCommentShowMore]]
    human_score: str
    human_date: str


@dataclass
class PostCommentShowMore:
    id: str
    parent_id: str
    show_more_count: int


@dataclass
class Post:
    id: str
    score: int
    human_score: str
    title: str
    author: str
    subreddit: str
    domain: str
    human_date: str
    thumbnail_url: str
    thumbnail_url_hq: str
    flair: Optional[Flair]
    content: PostContent
    url: str
    is_sticky: bool
    comments_count: int
    comments_url_path: str
    spoiler: bool
    over18: bool


@dataclass
class PostWithComments(Post):
    comments: Iterable[Union[PostComment, PostCommentShowMore]]
