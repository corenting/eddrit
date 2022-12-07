import html
from typing import Any, Dict, Hashable, Optional

import lxml.html

from eddrit import models
from eddrit.utils.media import is_from_external_preview_reddit_domain


def post_has_video_content(api_post_data: Dict[Hashable, Any]) -> bool:
    """Check if a post is a video."""
    if api_post_data.get("secure_media"):
        return True

    if "preview" in api_post_data:

        if api_post_data["preview"].get("reddit_video_preview"):
            return True

        variants = api_post_data["preview"]["images"][0].get("variants")

        if variants and variants.get("mp4"):
            return True

    return False


def get_post_image_content(
    api_post_data: Dict[Hashable, Any]
) -> models.LinkPostContent | models.PicturePostContent:
    """
    Get the image content of a post.
    Fallback to link post if errors encountered in pictures.
    """
    try:
        picture_url = html.unescape(
            api_post_data["preview"]["images"][0]["source"]["url"]
        )
        return models.PicturePostContent(
            picture=models.PostPicture(
                url=picture_url,
                width=api_post_data["preview"]["images"][0]["source"]["width"],
                height=api_post_data["preview"]["images"][0]["source"]["height"],
            )
        )
    except Exception:
        return models.LinkPostContent()


def get_post_video_content(
    api_post_data: Dict[Hashable, Any]
) -> models.VideoPostContent | models.PicturePostContent | models.LinkPostContent:
    """
    Get the video content of a post.
    Fallback to image or link post if errors encountered in pictures.
    """
    try:
        if api_post_data.get("secure_media"):
            if api_post_data["secure_media"].get("oembed"):
                ret = _get_embed_content(api_post_data["secure_media"]["oembed"])
            else:
                ret = _get_secure_media_reddit_video(api_post_data)
        elif (
            "variants" in api_post_data["preview"]["images"][0]
            and "mp4" in api_post_data["preview"]["images"][0]["variants"]
        ):
            ret = _get_mp4_preview_video(api_post_data)
        elif "reddit_video_preview" in api_post_data["preview"]:
            ret = _get_reddit_video_preview(api_post_data)
        else:
            raise Exception("Cannot find video for post")

        # Swap external-preview.redd.it with video preview, as the former is blocked by CORS
        if is_from_external_preview_reddit_domain(ret.url):
            return _get_reddit_video_preview(api_post_data, models.PostVideoFormat.MP4)

        return ret

    except Exception:
        return models.LinkPostContent()


def _get_embed_content(embed_data: Dict[Hashable, Any]) -> models.VideoPostContent:
    content = html.unescape(embed_data["html"])
    is_gif = False
    is_embed = True

    # Cleanup embed html
    content_parsed = lxml.html.fromstring(content)
    for elt in content_parsed.iter("iframe"):
        elt.attrib["class"] = "post-content-iframe"
        del elt.attrib["width"]
        del elt.attrib["height"]
        del elt.attrib["style"]
    content = lxml.html.tostring(content_parsed).decode("utf-8")

    return models.VideoPostContent(
        url=content,
        width=embed_data["width"],
        height=embed_data["height"] + 25,
        is_gif=is_gif,
        is_embed=is_embed,
    )


def _get_secure_media_reddit_video(
    api_post_data: Dict[Hashable, Any]
) -> models.VideoPostContent:
    reddit_video = api_post_data["secure_media"]["reddit_video"]
    return models.VideoPostContent(
        url=html.unescape(reddit_video["dash_url"]),
        width=reddit_video["width"],
        height=reddit_video["height"],
        is_gif=reddit_video["is_gif"],
        is_embed=False,
        video_format=models.PostVideoFormat.DASH,
    )


def _get_mp4_preview_video(
    api_post_data: Dict[Hashable, Any]
) -> models.VideoPostContent:
    mp4_video = api_post_data["preview"]["images"][0]["variants"]["mp4"]["source"]
    return models.VideoPostContent(
        url=html.unescape(mp4_video["url"]),
        width=mp4_video["width"],
        height=mp4_video["height"],
        is_gif="gif" in api_post_data["preview"]["images"][0]["variants"],
        is_embed=False,
        video_format=models.PostVideoFormat.MP4,
    )


def _get_reddit_video_preview(
    api_post_data: Dict[Hashable, Any], format: Optional[models.PostVideoFormat] = None
) -> models.VideoPostContent:
    reddit_video = api_post_data["preview"]["reddit_video_preview"]
    video_url = reddit_video["fallback_url" if format else "dash_url"]
    return models.VideoPostContent(
        url=video_url,
        width=reddit_video["width"],
        height=reddit_video["height"],
        is_gif=reddit_video["is_gif"],
        is_embed=False,
        video_format=format or models.PostVideoFormat.DASH,
    )
