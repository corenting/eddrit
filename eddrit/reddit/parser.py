import datetime
import html
from typing import Any, Dict, Hashable, Iterable, List, Optional, Tuple, Union

import timeago

from eddrit import models
from eddrit.reddit.content_parser.flair import get_post_flair, get_user_flair
from eddrit.reddit.content_parser.media import (
    get_post_image_content,
    get_post_video_content,
    post_has_video_content,
)
from eddrit.utils.math import pretty_big_num
from eddrit.utils.media import is_image_or_video_host


def get_post_content(api_post_data: Dict[Hashable, Any]) -> models.PostContentBase:
    # Text posts
    if api_post_data["is_self"] and api_post_data.get("selftext_html"):
        content = (
            html.unescape(api_post_data.get("selftext_html", ""))
            .replace("<!-- SC_ON -->", "")
            .replace("<!-- SC_OFF -->", "")
        )

        return models.TextPostContent(text=content)

    # Media posts
    hint = api_post_data.get("post_hint")
    has_video_content = post_has_video_content(api_post_data)
    if (
        hint == "image"
        or hint == "hosted:video"
        or hint == "rich:video"
        or (hint == "link" and is_image_or_video_host(api_post_data["domain"]))
        or has_video_content
    ):

        # Check if image has video (then consider video) else consider image
        if has_video_content:
            return get_post_video_content(api_post_data)

        return get_post_image_content(api_post_data)

    # Default case: link posts
    return models.LinkPostContent()


def get_thumbnail_url(data: Dict[Hashable, Any]) -> str:
    thumbnail_url = data.get("thumbnail")
    static_replacement = "$STATIC_RES_PATH"

    if thumbnail_url == "self":
        thumbnail_url = f"{static_replacement}images/icons/card-list.svg"
    elif thumbnail_url == "default":
        thumbnail_url = f"{static_replacement}images/icons/link.svg"
    elif thumbnail_url == "nsfw":
        thumbnail_url = f"{static_replacement}images/icons/slash-circle.svg"
    elif thumbnail_url == "spoiler":
        thumbnail_url = f"{static_replacement}images/icons/exclamation-circle.svg"
    elif thumbnail_url == "image":
        thumbnail_url = f"{static_replacement}images/icons/image.svg"
    elif (
        (not thumbnail_url or thumbnail_url == "image")
        and data.get("media", None)
        and "oembed" in data["media"]
        and data["media"]["oembed"].get("thumbnail_url")
    ):
        thumbnail_url = data["media"]["oembed"]["thumbnail_url"]
    elif thumbnail_url is None or len(thumbnail_url) == 0:
        thumbnail_url = f"{static_replacement}images/icons/globe.svg"

    return thumbnail_url


def get_post_url(data: Dict[Hashable, Any]) -> str:
    if data["is_self"]:
        return data["permalink"]
    return data["url"]


def parse_posts(
    api_response: Dict[Hashable, Any], is_popular: bool
) -> Tuple[List[models.Post], models.Pagination]:
    res = []
    for item in api_response["data"]["children"]:
        data = item["data"]

        res.append(parse_post(data, is_popular))

    return (
        res,
        models.Pagination(
            before_post_id=api_response["data"]["before"],
            after_post_id=api_response["data"]["after"],
        ),
    )


def parse_post(post_data: Dict[Hashable, Any], is_popular: bool) -> models.Post:
    utc_now = datetime.datetime.utcnow()

    post_image_content = get_post_image_content(post_data)

    # Get post thumbnail
    thumbnail_url = get_thumbnail_url(post_data)
    thumbnail_url_hq = thumbnail_url
    if type(post_image_content) == models.PicturePostContent:
        thumbnail_url_hq = post_image_content.picture.url

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
            datetime.datetime.utcfromtimestamp(post_data["created_utc"]),
            utc_now,
        ),
        thumbnail_url=thumbnail_url,
        thumbnail_url_hq=thumbnail_url_hq,
        flair=get_post_flair(post_data),
        content=get_post_content(post_data),
        url=get_post_url(post_data),
        is_sticky=post_data["stickied"] and not is_popular,
        comments_count=post_data["num_comments"],
        comments_url_path=post_data["permalink"],
        spoiler=post_data["spoiler"],
        over18=post_data["over_18"],
    )


def parse_subreddit_informations(
    name: str, over18: bool, api_response: Optional[Dict[Hashable, Any]] = None
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
    elif api_response:
        title = html.unescape(api_response["data"]["title"])
        show_thumbnails = api_response["data"]["show_media"]
        public_description = api_response["data"]["public_description"]
    else:
        raise ValueError("You need a api_response if it's not a multi")

    return models.Subreddit(
        title=title,
        show_thumbnails=show_thumbnails,
        public_description=public_description,
        name=name,
        over18=over18,
    )


def parse_comments(
    comments_data: Dict[Hashable, Any]
) -> Iterable[Union[models.PostComment, models.PostCommentShowMore]]:
    root_comments = comments_data["children"]
    ret: List[Union[models.PostComment, models.PostCommentShowMore]] = []
    utc_now = datetime.datetime.utcnow()

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
            data = comment["data"]
            replies = data["replies"]
            childrens = (
                []
                if replies is None or isinstance(replies, str)
                else parse_comments(data["replies"]["data"])
            )
            ret.append(
                models.PostComment(
                    id=data["id"],
                    parent_id=comment["data"]["parent_id"]
                    .replace("t1_", "")
                    .replace("t3_", ""),
                    is_sticky=data["stickied"],
                    author=models.User(
                        name=data["author"],
                        flair=get_user_flair(data),
                    ),
                    is_submitter=data["is_submitter"],
                    is_admin=data.get("distinguished", "") == "admin",
                    is_moderator=data.get("distinguished", "") == "moderator",
                    content=html.unescape(data["body_html"]),
                    human_date=timeago.format(
                        datetime.datetime.utcfromtimestamp(data["created_utc"]), utc_now
                    ),
                    human_score=pretty_big_num(data["score"]),
                    children=childrens,
                )
            )
    return ret
