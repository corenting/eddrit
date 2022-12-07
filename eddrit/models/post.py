from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional, Union

from eddrit.models.user import Flair, User


class PostContentType(Enum):
    GALLERY = "gallery"
    PICTURE = "picture"
    LINK = "link"
    TEXT = "text"
    VIDEO = "video"


class PostVideoFormat(Enum):
    MP4 = "video/mp4"
    DASH = "application/dash+xml"


@dataclass
class PostPicture:
    """Class representing a post picture."""

    width: int
    height: int
    url: str


@dataclass(kw_only=True)
class PostContentBase:
    """Base class representing a post content."""

    type: PostContentType


@dataclass(kw_only=True)
class PicturePostContent(PostContentBase):
    """Class representing a picture post content."""

    type: PostContentType = PostContentType.PICTURE

    picture: PostPicture


@dataclass(kw_only=True)
class LinkPostContent(PostContentBase):
    """Class representing a link post content.

    The link is not in the class as it the same as the post link."""

    type: PostContentType = PostContentType.LINK


@dataclass(kw_only=True)
class TextPostContent(PostContentBase):
    """Class representing a text post content."""

    type: PostContentType = PostContentType.TEXT

    text: str


@dataclass(kw_only=True)
class VideoPostContent(PostContentBase):
    """Class representing a video post content."""

    type: PostContentType = PostContentType.VIDEO

    url: str
    is_gif: bool
    is_embed: bool
    width: int
    height: int
    video_format: Optional[PostVideoFormat] = None


@dataclass(kw_only=True)
class GalleryPostContent(PostContentBase):
    """Class representing a gallery post content."""

    type: PostContentType = PostContentType.GALLERY

    pictures: Iterable[PostPicture]


@dataclass
class PostComment:
    id: str
    author: User
    children: Iterable[Union[PostComment, PostCommentShowMore]]
    content: str
    human_date: str
    human_score: str
    is_admin: bool
    is_moderator: bool
    is_sticky: bool
    is_submitter: bool
    parent_id: str


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
    author: User
    subreddit: str
    domain: str
    human_date: str
    thumbnail_url: str
    thumbnail_is_icon: bool
    flair: Optional[Flair]
    content: PostContentBase
    url: str
    is_sticky: bool
    comments_count: int
    comments_url_path: str
    spoiler: bool
    over18: bool


@dataclass
class PostWithComments(Post):
    comments: Iterable[Union[PostComment, PostCommentShowMore]]
