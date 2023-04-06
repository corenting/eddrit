import html
from typing import Any, Dict, Hashable
from urllib.parse import urlparse


from eddrit import models
from eddrit.utils.media import (
    post_is_from_domain,
)
from loguru import logger

from eddrit.reddit.content_parser import video_parsers


def _post_is_an_imgur_gif(api_post_data: Dict[Hashable, Any]) -> bool:
    """Check if a post is an imgur gif by checking domain and url file extension."""
    return (
        post_is_from_domain(api_post_data["domain"], "imgur.com")
        and ".gif" in api_post_data["url"]
    )


def post_has_video_content(api_post_data: Dict[Hashable, Any]) -> bool:
    """Check if a post is a video."""

    # Special case for imgur.com images as links
    if _post_is_an_imgur_gif(api_post_data):
        return True

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


def get_post_gallery_content(
    api_post_data: Dict[Hashable, Any]
) -> models.LinkPostContent | models.GalleryPostContent:
    """
    Get the gallery content of a post.
    Fallback to link post if errors encountered in pictures.
    """
    try:
        # Get pictures
        pictures = [
            _get_gallery_picture(item)
            for item in api_post_data["media_metadata"].values()
        ]

        return models.GalleryPostContent(pictures=pictures)
    except Exception:
        return models.LinkPostContent()


def _get_gallery_picture(picture_api_data: dict[str, Any]) -> models.PostPicture:
    # Get width and height
    width = picture_api_data["s"]["y"]
    height = picture_api_data["s"]["x"]

    # Get direct URL by switching domain and removing query parameters
    old_url = urlparse(picture_api_data["s"]["u"])
    new_url = f"{old_url.scheme}://i.redd.it{old_url.path}"

    return models.PostPicture(width=width, height=height, url=new_url)


def get_post_video_content(
    api_post_data: Dict[Hashable, Any]
) -> models.VideoPostContent | models.PicturePostContent | models.LinkPostContent:
    """
    Get the video content of a post.
    Fallback to image or link post if errors encountered in videos.
    """
    try:
        # Check all parsers
        parsers = [
            video_parsers.get_embed_content,
            video_parsers.get_external_video,
            video_parsers.get_secure_media_reddit_video,
            video_parsers.get_reddit_video_preview,
        ]

        # Special case for imgur gif/gifv, it's easier to get the mp4 directly from the URL
        if _post_is_an_imgur_gif(api_post_data):
            parsers.append(video_parsers.get_imgur_gif)

        # Special case for gfycats, some old links are not embed
        if post_is_from_domain(api_post_data["domain"], "gfycat.com"):
            parsers.append(video_parsers.get_gfycat_embed)

        parsed_results = []
        for parser in parsers:
            try:
                parsed_item = parser(api_post_data)
                parsed_results.append(parsed_item)
            except Exception:
                continue

        # Sort: best resolution + non-embed first
        parsed_results.sort(
            key=lambda x: (x.width + x.height, not x.is_embed), reverse=True
        )

        # Pick best content
        logger.debug(
            f"Media parsed for {api_post_data['permalink']} : {str(parsed_results)}"
        )
        return parsed_results[0]

    except Exception:
        logger.exception(
            f"Post \"{api_post_data['title']}\": could not parse video content, falling back to link"
        )
        return models.LinkPostContent()
