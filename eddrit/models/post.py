from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from eddrit.models.user import Flair, User


class PostContentType(StrEnum):
    GALLERY = "gallery"
    PICTURE = "picture"
    LINK = "link"
    TEXT = "text"
    VIDEO = "video"
    EMBED = "embed"


class PostVideoFormat(StrEnum):
    MP4 = "video/mp4"
    DASH = "application/dash+xml"


@dataclass
class PostVideo:
    """Class representing a post video."""

    url: str
    is_gif: bool
    width: int
    height: int
    video_format: PostVideoFormat | None = None
    poster_url: str | None = None


@dataclass
class PostPicture:
    """Class representing a post picture."""

    width: int
    height: int
    url: str


@dataclass(kw_only=True)
class PostContent:
    """Base class representing a post content."""

    # The default type is text, as it doesn't
    # need any other fields,
    # and other post types can still include texts
    type: PostContentType = PostContentType.TEXT

    text: str | None = None


@dataclass(kw_only=True)
class PicturePostContent(PostContent):
    """Class representing a picture post content."""

    type: PostContentType = PostContentType.PICTURE

    picture: PostPicture


@dataclass(kw_only=True)
class LinkPostContent(PostContent):
    """Class representing a link post content.

    The link is not in the class as it the same as the post link."""

    type: PostContentType = PostContentType.LINK


@dataclass(kw_only=True)
class VideoPostContent(PostContent):
    """Class representing a video post content with different sources."""

    type: PostContentType = PostContentType.VIDEO
    videos: list[PostVideo]


@dataclass(kw_only=True)
class EmbedPostContent(PostContent):
    """Class representing a embed post content."""

    type: PostContentType = PostContentType.EMBED
    width: int
    height: int
    url: str
    poster_url: str | None = None


@dataclass(kw_only=True)
class GalleryPostContent(PostContent):
    """Class representing a gallery post content."""

    type: PostContentType = PostContentType.GALLERY

    contents: Iterable[PostPicture | PostVideo]
    captions: Iterable[str]


@dataclass
class PostComment:
    id: str
    author: User
    children: Iterable[PostComment | PostCommentShowMore]
    content: str
    human_date: str
    human_score: str
    is_admin: bool
    is_moderator: bool
    is_sticky: bool
    is_submitter: bool
    parent_id: str
    subreddit: str

    # only for comments on user pages
    comments_count: str
    link_title: str
    link_url: str | None
    current_comment_url: str | None
    over18: bool


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
    flair: Flair | None
    content: PostContent
    url: str
    is_sticky: bool
    comments_count: int
    comments_url_path: str
    spoiler: bool
    over18: bool


@dataclass
class PostWithComments(Post):
    comments: Iterable[PostComment | PostCommentShowMore]
