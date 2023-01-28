import html
from typing import Any, Dict, Hashable

import lxml.html

from eddrit import models


def _cleanup_embed(content: str) -> str:
    """Cleanup embed content for embed posts"""
    content_parsed = lxml.html.fromstring(content)
    for elt in content_parsed.iter("iframe"):
        elt.attrib["class"] = "post-content-iframe"
        elt.attrib.pop("width", None)
        elt.attrib.pop("height", None)
        elt.attrib.pop("style", None)

    return lxml.html.tostring(content_parsed).decode("utf-8")


def get_gfycat_embed(api_post_data: Dict[Hashable, Any]) -> models.VideoPostContent:
    """Fetch gfycat embed directly"""

    # Get url
    src_url = api_post_data["url"].replace("gfycat.com/", "gfycat.com/ifr/")
    embed_code = f"<iframe src='{src_url}' frameborder='0' scrolling='no' allowfullscreen></iframe>"

    # Get width and height from reddit video preview which should be same size
    reddit_video_preview = get_reddit_video_preview(api_post_data)

    return models.VideoPostContent(
        url=_cleanup_embed(embed_code),
        width=reddit_video_preview.width,
        height=reddit_video_preview.height,
        is_gif=False,
        is_embed=True,
    )


def get_imgur_gif(api_post_data: Dict[Hashable, Any]) -> models.VideoPostContent:
    """Fetch gif from imgur."""

    # Get item as we still need it for width/height
    video_item = api_post_data["preview"]["images"][0]["source"]

    url = api_post_data["url"]
    url = url.replace(".gifv", ".mp4")
    url = url.replace(".gif", ".mp4")

    return models.VideoPostContent(
        url=url,
        width=video_item["width"],
        height=video_item["height"],
        is_gif=True,
        is_embed=False,
        video_format=models.PostVideoFormat.MP4,
    )


def get_embed_content(api_post_data: Dict[Hashable, Any]) -> models.VideoPostContent:
    embed_data = api_post_data["secure_media"]["oembed"]
    content = html.unescape(embed_data["html"])
    is_embed = True

    return models.VideoPostContent(
        url=_cleanup_embed(content),
        width=embed_data["width"],
        height=embed_data["height"],
        is_gif=False,
        is_embed=is_embed,
    )


def get_secure_media_reddit_video(
    api_post_data: Dict[Hashable, Any]
) -> models.VideoPostContent:
    """Get 'secure media' reddit video."""
    reddit_video = api_post_data["secure_media"]["reddit_video"]
    return models.VideoPostContent(
        url=html.unescape(reddit_video["dash_url"]),
        width=reddit_video["width"],
        height=reddit_video["height"],
        is_gif=reddit_video["is_gif"],
        is_embed=False,
        video_format=models.PostVideoFormat.DASH,
    )


def get_external_video(api_post_data: Dict[Hashable, Any]) -> models.VideoPostContent:
    """Get external video."""
    video = api_post_data["preview"]["images"][0]["variants"]["mp4"]["source"]

    return models.VideoPostContent(
        url=html.unescape(video["url"]),
        width=video["width"],
        height=video["height"],
        is_gif="gif" in api_post_data["preview"]["images"][0]["variants"],
        is_embed=False,
        video_format=models.PostVideoFormat.MP4,
    )


def get_reddit_video_preview(
    api_post_data: Dict[Hashable, Any]
) -> models.VideoPostContent:
    """Get reddit video."""
    reddit_video = api_post_data["preview"]["reddit_video_preview"]
    video_url = reddit_video["dash_url"]

    return models.VideoPostContent(
        url=video_url,
        width=reddit_video["width"],
        height=reddit_video["height"],
        is_gif=reddit_video["is_gif"],
        is_embed=False,
        video_format=models.PostVideoFormat.DASH,
    )
