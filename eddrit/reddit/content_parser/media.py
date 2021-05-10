import html
from enum import Enum
from typing import Any, Dict, Hashable, Optional
from urllib.parse import urljoin, urlparse

import lxml.html

from eddrit import models
from eddrit.utils.media import (
    is_from_external_preview_reddit_domain,
    is_from_preview_reddit_domain,
)


class VideoFormat(Enum):
    MP4 = "mp4"
    DASH = "dash"


def post_has_video_content(api_post_data: Dict[Hashable, Any]) -> bool:
    if api_post_data.get("secure_media"):
        return True

    if "preview" in api_post_data:

        if api_post_data["preview"].get("reddit_video_preview"):
            return True

        variants = api_post_data["preview"]["images"][0].get("variants")

        if variants and variants.get("mp4"):
            return True

    return False


def get_post_image_content(api_post_data: Dict[Hashable, Any]) -> models.PostContent:
    try:
        content = html.unescape(api_post_data["preview"]["images"][0]["source"]["url"])
        return models.PostContent(
            content=content,
            type=models.PostContentType.IMAGE,
            width=api_post_data["preview"]["images"][0]["source"]["width"],
            height=api_post_data["preview"]["images"][0]["source"]["height"],
        )
    except Exception:
        return models.PostContent(
            content=api_post_data["url"],
            type=models.PostContentType.LINK,
            width=None,
            height=None,
        )


def get_embed_content(embed_data: Dict[Hashable, Any]) -> models.PostContent:
    content = html.unescape(embed_data["html"])
    content_type = None
    is_gif = False
    is_embed = True

    # Cleanup embed html
    content_parsed = lxml.html.fromstring(content)
    for elt in content_parsed.iter("iframe"):
        elt.attrib["style"] = "max-width: 100%; max-height: 100%;"
    content = lxml.html.tostring(content_parsed).decode("utf-8")

    return models.PostContent(
        content=content,
        type=models.PostContentType.VIDEO,
        width=embed_data["width"],
        height=embed_data["height"] + 25,
        is_gif=is_gif,
        is_embed=is_embed,
        content_type=content_type,
    )


def get_secure_media_reddit_video(
    api_post_data: Dict[Hashable, Any]
) -> models.PostContent:
    reddit_video = api_post_data["secure_media"]["reddit_video"]
    return models.PostContent(
        content=html.unescape(reddit_video["dash_url"]),
        type=models.PostContentType.VIDEO,
        width=reddit_video["width"],
        height=reddit_video["height"],
        is_gif=reddit_video["is_gif"],
        is_embed=False,
        content_type=VideoFormat.DASH.value,
    )


def get_mp4_preview_video(api_post_data: Dict[Hashable, Any]) -> models.PostContent:
    mp4_video = api_post_data["preview"]["images"][0]["variants"]["mp4"]["source"]
    return models.PostContent(
        content=html.unescape(mp4_video["url"]),
        type=models.PostContentType.VIDEO,
        width=mp4_video["width"],
        height=mp4_video["height"],
        is_gif="gif" in api_post_data["preview"]["images"][0]["variants"],
        is_embed=False,
        content_type=VideoFormat.MP4.value,
    )


def get_reddit_video_preview(
    api_post_data: Dict[Hashable, Any], format: Optional[VideoFormat] = None
) -> models.PostContent:
    reddit_video = api_post_data["preview"]["reddit_video_preview"]
    content = reddit_video["dash_url" if not format else "fallback_url"]
    return models.PostContent(
        content=content,
        type=models.PostContentType.VIDEO,
        width=reddit_video["width"],
        height=reddit_video["height"],
        is_gif=reddit_video["is_gif"],
        is_embed=False,
        content_type=format.value if format else "dash",
    )


def get_post_video_content(api_post_data: Dict[Hashable, Any]) -> models.PostContent:
    try:
        if api_post_data.get("secure_media"):
            if api_post_data["secure_media"].get("oembed"):
                ret = get_embed_content(api_post_data["secure_media"]["oembed"])
            elif api_post_data["secure_media"].get("reddit_video"):
                ret = get_secure_media_reddit_video(api_post_data)
        elif (
            "variants" in api_post_data["preview"]["images"][0]
            and "mp4" in api_post_data["preview"]["images"][0]["variants"]
        ):
            ret = get_mp4_preview_video(api_post_data)
        elif "reddit_video_preview" in api_post_data["preview"]:
            ret = get_reddit_video_preview(api_post_data)
        else:
            raise Exception("Cannot find video for post")

        # Swap external-preview.redd.it with video preview, as the former is blocked by CORS
        if ret.content and is_from_external_preview_reddit_domain(ret.content):
            return get_reddit_video_preview(api_post_data, VideoFormat.MP4)

        # Special case for preview.redd.it (blocked by CORS, swap with i.redd.it)
        if ret.content and is_from_preview_reddit_domain(ret.content):
            ret.content = urljoin(ret.content, urlparse(ret.content).path).replace(
                "preview.redd.it", "i.redd.it"
            )
            ret.type = models.PostContentType.IMAGE

        return ret

    except Exception:
        return models.PostContent(
            content=api_post_data["url"],
            type=models.PostContentType.LINK,
            width=None,
            height=None,
        )
