import html
from collections.abc import Callable, Hashable
from typing import Any
from urllib.parse import urlparse

from loguru import logger

from eddrit import models
from eddrit.reddit.content_parser import video_parsers
from eddrit.utils.urls import get_domain_and_suffix_from_url


def _post_is_an_imgur_gif(api_post_data: dict[Hashable, Any]) -> bool:
    """Check if a post is an imgur gif by checking domain and url file extension."""
    return (
        get_domain_and_suffix_from_url(api_post_data["domain"]) == "imgur.com"
        and ".gif" in api_post_data["url"]
    )


def post_has_video_content(api_post_data: dict[Hashable, Any]) -> bool:
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
    api_post_data: dict[Hashable, Any],
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
    api_post_data: dict[Hashable, Any],
) -> models.LinkPostContent | models.GalleryPostContent:
    """
    Get the gallery content of a post.
    Fallback to link post if errors encountered in pictures.
    """
    try:
        # Get image urls in order
        gallery_data = api_post_data["gallery_data"].get("items")
        sorted_image_ids = [item["media_id"] for item in gallery_data]

        media_metadata = api_post_data["media_metadata"]
        sorted_image_metadata = [media_metadata[id] for id in sorted_image_ids]

        pictures = [_get_gallery_picture(item) for item in sorted_image_metadata]

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
    api_post_data: dict[Hashable, Any],
) -> models.VideoPostContent | models.LinkPostContent | models.EmbedPostContent:
    """
    Get the video content of a post.
    Fallback to image or link post if errors encountered in videos.
    """
    try:
        # Check all parsers
        parsers: list[Callable[[dict], models.PostVideo | models.EmbedPostContent]] = [
            video_parsers.get_embed_content,
            video_parsers.get_external_video,
            video_parsers.get_secure_media_reddit_video,
            video_parsers.get_reddit_video_preview,
        ]

        post_domain = get_domain_and_suffix_from_url(api_post_data["domain"])

        # Special case for some embeds
        domains_with_special_embed_handling = (
            video_parsers.get_domains_with_special_embed_handling()
        )
        if post_domain in domains_with_special_embed_handling:
            parsers.append(domains_with_special_embed_handling[post_domain])

        parsed_results: list[models.PostVideo | models.EmbedPostContent] = []
        for parser in parsers:
            try:
                parsed_item = parser(api_post_data)
                parsed_results.append(parsed_item)
            except Exception:
                logger.debug(f"Cannot parse content with {parser.__name__}")
                continue
            else:
                logger.debug(f"Parsed {parsed_item} with {parser.__name__}")

        # Sort: best resolution + non-embed first
        parsed_results.sort(
            key=lambda x: (x.width * x.height, type(x) != models.EmbedPostContent),
            reverse=True,
        )
        logger.debug(
            f"Media parsed for {api_post_data['permalink']} : {parsed_results}"
        )

        # If we cannot parse anything, put a link
        if not parsed_results:
            logger.debug(
                f"Couldn't find media for {api_post_data['permalink']}, fallbacking to link"
            )
            return models.LinkPostContent()

        # If one content is an embed but the other are GIF (so no sound),
        # display the embed as it may have sound
        if (
            embed_content := next(
                (x for x in parsed_results if type(x) == models.EmbedPostContent), None
            )
        ) and any(getattr(x, "is_gif", False) for x in parsed_results):
            return embed_content

        # If the best content is an embed, just return it as the frontend
        # doesn't handle mix of embed and non embed sources
        best_content = parsed_results[0]
        if type(best_content) == models.EmbedPostContent:
            return best_content

        # Else return the list of non-embed sources
        videos = [
            item for item in parsed_results if type(item) != models.EmbedPostContent
        ]
        return models.VideoPostContent(
            videos=videos  # type: ignore
        )

    except Exception:
        logger.exception(
            f"Post \"{api_post_data['title']}\": could not parse video content, falling back to link"
        )
        return models.LinkPostContent()
