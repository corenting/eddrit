import datetime
import html
import re
from collections.abc import Hashable, Iterable
from typing import Any

import timeago

from eddrit import models
from eddrit.reddit.content_parser.flair import get_post_flair, get_user_flair
from eddrit.reddit.content_parser.media import (
    get_post_gallery_content,
    get_post_image_content,
    get_post_video_content,
    post_has_video_content,
)
from eddrit.utils.math import pretty_big_num
from eddrit.utils.urls import get_domain_and_suffix_from_url

# Constant used in templates to be replaced by the static path
STATIC_RES_PATH_REPLACEMENT = "$STATIC_RES_PATH"

# Domains that may be used in post of type link but that are majorly used for image hosting and should be parsed as such
MEDIA_HOSTING_DOMAINS = ["imgur.com"]

# Media domains to display as links (embed that cannot be displayed, scripts needed etc.)
MEDIA_DOMAINS_TO_DISPLAY_AS_LINK = ["tiktok.com", "twitter.com"]

WIKI_LINKS_REGEX = re.compile(r'href="https:\/\/old\.reddit\.com\/r\/(.*)\/wiki\/(.*)"')


def clean_content(initial_content: str) -> str:
    """
    Clean text content:
    - Unescape HTML content so that it can renderer on eddrit.
    - Replace reddit links to eddrit links for supported links
    """
    content = (
        html.unescape(initial_content)
        .replace("<!-- SC_ON -->", "")
        .replace("<!-- SC_OFF -->", "")
    )

    # Replace all match of regex in content
    content = WIKI_LINKS_REGEX.sub(r'href="/r/\1/wiki/\2"', content)

    return content


def get_post_content(api_post_data: dict[Hashable, Any]) -> models.PostContentBase:
    # Text posts
    if api_post_data["is_self"] and api_post_data.get("selftext_html"):
        content = clean_content(api_post_data.get("selftext_html", ""))

        return models.TextPostContent(text=content)

    # Check if it's a crosspost.
    # If it's a case, use crosspost data as the normal
    # data will be a link
    if (
        "crosspost_parent_list" in api_post_data
        and len(api_post_data["crosspost_parent_list"]) > 0
    ):
        api_post_data = api_post_data["crosspost_parent_list"][0]

    # Gallery posts
    if "gallery_data" in api_post_data:
        return get_post_gallery_content(api_post_data)

    # Media posts
    hint = api_post_data.get("post_hint")
    has_video_content = post_has_video_content(api_post_data)
    post_domain = get_domain_and_suffix_from_url(api_post_data["domain"])
    if (
        hint in ["image", "hosted:video", "rich:video"]
        or post_domain in MEDIA_HOSTING_DOMAINS
        or has_video_content
    ) and post_domain not in MEDIA_DOMAINS_TO_DISPLAY_AS_LINK:
        # First try video: if link returned, try image
        content = get_post_video_content(api_post_data)
        if type(content) is models.LinkPostContent:
            return get_post_image_content(api_post_data)
        return content

    # Default case: link posts
    return models.LinkPostContent()


def get_post_thumbnail(data: dict[Hashable, Any]) -> tuple[str, bool]:
    """Return a tuple with the post thumbnail URL and a boolean indicating if the thumbnail is an icon or not."""
    thumbnail_url = data.get("thumbnail")

    # Icons
    if thumbnail_url == "self":
        thumbnail_url = f"{STATIC_RES_PATH_REPLACEMENT}images/icons/card-list.svg"
    elif thumbnail_url == "default":
        thumbnail_url = f"{STATIC_RES_PATH_REPLACEMENT}images/icons/link.svg"
    elif thumbnail_url == "nsfw":
        thumbnail_url = f"{STATIC_RES_PATH_REPLACEMENT}images/icons/slash-circle.svg"
    elif thumbnail_url == "spoiler":
        thumbnail_url = (
            f"{STATIC_RES_PATH_REPLACEMENT}images/icons/exclamation-circle.svg"
        )
    elif thumbnail_url == "image":
        thumbnail_url = f"{STATIC_RES_PATH_REPLACEMENT}images/icons/image.svg"
    # Else get from media
    elif (
        (not thumbnail_url or thumbnail_url == "image")
        and data.get("media")
        and "oembed" in data["media"]
        and data["media"]["oembed"].get("thumbnail_url")
    ):
        thumbnail_url = data["media"]["oembed"]["thumbnail_url"]
    elif thumbnail_url is None or len(thumbnail_url) == 0:
        thumbnail_url = f"{STATIC_RES_PATH_REPLACEMENT}images/icons/globe.svg"

    return html.unescape(thumbnail_url), STATIC_RES_PATH_REPLACEMENT in thumbnail_url


def get_post_url(data: dict[Hashable, Any]) -> str:
    return data["permalink"] if data["is_self"] else data["url"]


def parse_posts_and_comments(
    api_response: dict[Hashable, Any], is_popular_or_all: bool
) -> tuple[list[models.Post | models.PostComment], models.Pagination]:
    """ "
    Parse posts from API response.

    Will also return comments if parsing an user page.
    """
    res: list[models.Post | models.PostComment] = []
    for item in api_response["data"]["children"]:
        data = item["data"]

        if item["kind"] == "t3":
            res.append(parse_post(data, is_popular_or_all))
        else:
            res.append(_parse_comment(item))

    return (
        res,
        models.Pagination(
            before_post_id=api_response["data"]["before"],
            after_post_id=api_response["data"]["after"],
        ),
    )


def parse_post(post_data: dict[Hashable, Any], is_popular_or_all: bool) -> models.Post:
    utc_now = datetime.datetime.now(tz=datetime.UTC)

    # Get post thumbnail
    thumbnail_url, thumbnail_is_icon = get_post_thumbnail(post_data)

    return models.Post(
        id=post_data["id"],
        score=post_data["score"],
        human_score=pretty_big_num(post_data["score"]),
        title=html.unescape(post_data["title"]),
        author=models.User(
            name=post_data["author"],
            flair=get_user_flair(post_data),
        ),
        subreddit=post_data["subreddit"],
        domain=post_data["domain"],
        human_date=timeago.format(
            datetime.datetime.fromtimestamp(post_data["created_utc"], tz=datetime.UTC),
            utc_now,
        ),
        thumbnail_url=thumbnail_url,
        thumbnail_is_icon=thumbnail_is_icon,
        flair=get_post_flair(post_data),
        content=get_post_content(post_data),
        url=get_post_url(post_data),
        is_sticky=post_data["stickied"] and not is_popular_or_all,
        comments_count=post_data["num_comments"],
        comments_url_path=post_data["permalink"],
        spoiler=post_data["spoiler"],
        over18=post_data["over_18"],
    )


def parse_subreddit_information(
    name: str, over18: bool, api_response: dict[Hashable, Any] | None = None
) -> models.Subreddit:
    # Check if multi
    splitted_name = name.split("+")
    if len(splitted_name) > 1:
        title = f"Posts from {', '.join(splitted_name)}"
        show_thumbnails = True
        public_description = "<p>Multi subreddits with :</p><ul>"
        for name in splitted_name:
            public_description += f'<li><a href="/r/{name}">r/{name}</a></li>'
        public_description += "</ul>"
        icon_url = None
    elif api_response:
        title = html.unescape(api_response["data"]["title"])
        show_thumbnails = api_response["data"]["show_media"]
        public_description = api_response["data"]["public_description"]
        icon_url = api_response["data"].get("icon_img")
    else:
        raise ValueError("You need a api_response if it's not a multi")

    return models.Subreddit(
        title=title,
        show_thumbnails=show_thumbnails,
        public_description=public_description,
        name=name,
        over18=over18,
        icon_url=icon_url,
        wiki_enabled=api_response["data"]["wiki_enabled"] if api_response else False,
    )


def parse_user_information(api_response: dict[Hashable, Any]) -> models.User:
    """
    Parse an user.
    """
    return models.User(
        name=api_response["data"]["name"],
        flair=None,
        over18=api_response["data"]["subreddit"]["over_18"],
        public_description=api_response["data"]["subreddit"]["public_description"],
    )


def _parse_comment(comment: dict[Hashable, Any]) -> models.PostComment:
    """
    Parse a single comment (not a show more link) to a models.PostComment
    """
    data = comment["data"]
    replies = data["replies"]
    utc_now = datetime.datetime.now(tz=datetime.UTC)
    childrens = (
        []
        if replies is None or isinstance(replies, str)
        else parse_comments_tree(data["replies"]["data"])
    )

    # For user page, get the link to the associated post
    # The link to the post is not relative in the API
    if link_url_absolute := data.get("link_url"):
        link_url: str | None = link_url_absolute.replace("https://old.reddit.com", "")
    else:
        link_url = None

    return models.PostComment(
        id=data["id"],
        parent_id=comment["data"]["parent_id"].replace("t1_", "").replace("t3_", ""),
        is_sticky=data["stickied"],
        author=models.User(
            name=data["author"],
            flair=get_user_flair(data),
        ),
        is_submitter=data["is_submitter"],
        is_admin=data.get("distinguished", "") == "admin",
        is_moderator=data.get("distinguished", "") == "moderator",
        content=clean_content(data["body_html"]),
        human_date=timeago.format(
            datetime.datetime.fromtimestamp(data["created_utc"], tz=datetime.UTC),
            utc_now,
        ),
        human_score=pretty_big_num(data["score"]),
        over18=data.get("over_18"),
        link_url=link_url,
        link_title=data.get("link_title"),
        comments_count=data.get("num_comments"),
        subreddit=data["subreddit"],
        children=childrens,
    )


def parse_comments_tree(
    comments_data: dict[Hashable, Any],
) -> Iterable[models.PostComment | models.PostCommentShowMore]:
    root_comments = comments_data["children"]
    ret: list[models.PostComment | models.PostCommentShowMore] = []

    for comment in root_comments:
        if comment["kind"] == "more":
            ret.append(
                models.PostCommentShowMore(
                    id=comment["data"]["id"],
                    parent_id=comment["data"]["parent_id"]
                    .replace("t1_", "")
                    .replace("t3_", ""),
                    show_more_count=comment["data"]["count"],
                )
            )
        else:
            ret.append(_parse_comment(comment))
    return ret
