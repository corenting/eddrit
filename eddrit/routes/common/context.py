from collections.abc import Iterable
from typing import Any
from urllib.parse import urlparse

from starlette.requests import Request

from eddrit import models
from eddrit.models.settings import LayoutMode, ThumbnailsMode
from eddrit.routes.common.cookies import get_bool_setting_value_from_cookie


def get_templates_common_context(
    request: Request, cookies: dict[str, str] | None = None
) -> dict[str, Any]:
    """
    Get common context from request (the request itself and the user settings).

    If cookies are provided, they will be used instead of the one of the request.
    This is only used when updating settings, as we just computed new values that are
    not in the original request.
    """
    cookies_source = cookies if cookies else request.cookies
    settings = models.Settings(
        layout=LayoutMode(cookies_source.get("layout", LayoutMode.WIDE.value)),
        thumbnails=ThumbnailsMode(
            cookies_source.get("thumbnails", ThumbnailsMode.SUBREDDIT_PREFERENCE.value)
        ),
        nsfw_popular_all=get_bool_setting_value_from_cookie(
            "nsfw_popular_all", cookies_source
        ),
        nsfw_thumbnails=get_bool_setting_value_from_cookie(
            "nsfw_thumbnails", cookies_source
        ),
    )

    return {
        "request": request,
        "settings": settings,
    }


def get_canonical_url_context(request: Request) -> dict[str, str]:
    """Get reddit canonical URL for a given eddrit request"""
    parsed_eddrit_url = urlparse(str(request.url))

    reddit_url = f"https://old.reddit.com{parsed_eddrit_url.path}"
    if parsed_eddrit_url.query:
        reddit_url += f"?{parsed_eddrit_url.query}"
    return {"canonical_url": reddit_url}


def get_posts_pages_common_context(
    pagination: models.Pagination,
    posts: Iterable[models.Post | models.PostComment],
    about_information: models.Subreddit | models.User,
    sorting_mode: models.SubredditSortingMode | models.UserSortingMode,
    sorting_period: models.SubredditSortingPeriod,
) -> dict[str, Any]:
    """
    Get common context for pages containing posts (subreddits, homepage, user pages).

    Posts also include post comments for user pages.
    """
    return {
        "pagination": pagination,
        "posts": posts,
        "about_information": about_information,
        "current_sorting_mode": sorting_mode,
        "current_sorting_period": sorting_period,
        "has_sorting_period": sorting_mode
        in [
            models.SubredditSortingMode.CONTROVERSIAL,
            models.SubredditSortingMode.TOP,
            models.UserSortingMode.CONTROVERSIAL,
            models.UserSortingMode.TOP,
        ],
    }
