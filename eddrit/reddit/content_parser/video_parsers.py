import contextlib
import html
import re
from collections.abc import Callable, Hashable
from typing import Any

import lxml.html
import tldextract

from eddrit import models
from eddrit.utils.middlewares import get_current_host


def _domain_has_special_embed_handling(domain: str) -> bool:
    """Check if the given domain is a domain that has a special code for embed handling."""
    extracted_domain = tldextract.extract(domain)
    return (
        f"{extracted_domain.domain}.{extracted_domain.suffix}"
        in get_domains_with_special_embed_handling()
    )


def _cleanup_embed(content: str) -> str:
    """Cleanup embed content for embed posts"""
    content_parsed = lxml.html.fromstring(content)
    for elt in content_parsed.iter("iframe"):
        elt.attrib["class"] = "post-content-iframe"
        elt.attrib.pop("style", None)

    return lxml.html.tostring(content_parsed).decode("utf-8")  # type: ignore


def _try_get_poster_url(api_post_data: dict[Hashable, Any]) -> str | None:
    """
    Try to get a poster URL for embed and videos
    """
    poster_url = None
    with contextlib.suppress(Exception):
        poster_url = html.unescape(
            api_post_data["preview"]["images"][0]["source"]["url"]
        )
    return poster_url


def get_domains_with_special_embed_handling() -> dict[str, Callable]:
    """Return dict of domain associated with parsing function
    of domains that have a special handling for their embed
    and should not be parsed with the generic embed code"""
    return {"twitch.tv": get_twitch_embed}


def get_twitch_embed(api_post_data: dict[Hashable, Any]) -> models.EmbedPostContent:
    """Fetch twitch embed directly as the one in the API has
    a Content-Security-Policy preventing including it.
    """

    # There are different formats of clips URLs
    if "clips.twitch.tv" in api_post_data["url"]:
        embed_url = api_post_data["url"].replace(
            "clips.twitch.tv/", "clips.twitch.tv/embed?clip="
        )
    elif regex_clip_id := re.search(
        "https://www.twitch.tv/.*/clip/(.*)", api_post_data["url"]
    ):
        clip_id = regex_clip_id.groups(0)[0]
        embed_url = f"https://clips.twitch.tv/embed?clip={clip_id}"
    else:
        raise ValueError("Cannot parse Twitch embed")

    parent = get_current_host()
    embed_code = f'<iframe src="{embed_url}&parent={parent}" frameborder="0" allowfullscreen="true" scrolling="no" height="378" width="620"></iframe>'
    return models.EmbedPostContent(
        url=_cleanup_embed(embed_code),
        width=378,
        height=620,
        poster_url=_try_get_poster_url(api_post_data),
    )


def get_imgur_gif(api_post_data: dict[Hashable, Any]) -> models.PostVideo:
    """Fetch gif from imgur."""

    # Get item as we still need it for width/height
    video_item = api_post_data["preview"]["images"][0]["source"]

    url = api_post_data["url"]
    url = url.replace(".gifv", ".mp4")
    url = url.replace(".gif", ".mp4")

    return models.PostVideo(
        url=url,
        width=video_item["width"],
        height=video_item["height"],
        is_gif=True,
        video_format=models.PostVideoFormat.MP4,
        poster_url=_try_get_poster_url(api_post_data),
    )


def get_embed_content(api_post_data: dict[Hashable, Any]) -> models.EmbedPostContent:
    if _domain_has_special_embed_handling(api_post_data["url"]):
        raise ValueError("The post domain cannot be parsed with get_embed_content")

    embed_data = api_post_data["secure_media"]["oembed"]
    content = html.unescape(embed_data["html"])

    return models.EmbedPostContent(
        url=_cleanup_embed(content),
        width=embed_data["width"],
        height=embed_data["height"] or 0,
        poster_url=_try_get_poster_url(api_post_data),
    )


def get_secure_media_reddit_video(
    api_post_data: dict[Hashable, Any],
) -> models.PostVideo:
    """Get 'secure media' reddit video."""
    reddit_video = api_post_data["secure_media"]["reddit_video"]
    return models.PostVideo(
        url=html.unescape(reddit_video["dash_url"]),
        width=reddit_video["width"],
        height=reddit_video["height"],
        is_gif=reddit_video["is_gif"],
        video_format=models.PostVideoFormat.DASH,
        poster_url=_try_get_poster_url(api_post_data),
    )


def get_external_video(api_post_data: dict[Hashable, Any]) -> models.PostVideo:
    """Get external video."""
    video = api_post_data["preview"]["images"][0]["variants"]["mp4"]["source"]

    return models.PostVideo(
        url=html.unescape(video["url"]),
        width=video["width"],
        height=video["height"],
        is_gif="gif" in api_post_data["preview"]["images"][0]["variants"],
        video_format=models.PostVideoFormat.MP4,
        poster_url=_try_get_poster_url(api_post_data),
    )


def get_reddit_video_preview(api_post_data: dict[Hashable, Any]) -> models.PostVideo:
    """Get reddit video."""
    reddit_video = api_post_data["preview"]["reddit_video_preview"]
    video_url = reddit_video["dash_url"]

    return models.PostVideo(
        url=video_url,
        width=reddit_video["width"],
        height=reddit_video["height"],
        is_gif=reddit_video["is_gif"],
        video_format=models.PostVideoFormat.DASH,
        poster_url=_try_get_poster_url(api_post_data),
    )
