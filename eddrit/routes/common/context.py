from typing import Any
from urllib.parse import urlparse

from starlette.requests import Request

from eddrit import models
from eddrit.models.settings import ThumbnailsMode


def _get_bool_setting_value_from_cookie(
    name: str, cookies: dict[str, str], default: bool = False
) -> bool:
    """Get boolean value of a given setting according to the given cookies.

    If setting not present, use default value
    """
    if name in cookies:
        return cookies[name] == "1"
    else:
        return default


def get_templates_common_context(
    request: Request, cookies: dict[str, str] | None = None
) -> dict[str, Any]:
    """
    Get common context from request (the request itself and the user settings).

    If cookies is provided, this dict will be used for the settings as the cookies source instead of the request cookies.
    This is useful if there were updated during this request.
    """
    cookies_source = cookies if cookies else request.cookies
    settings = models.Settings(
        thumbnails=ThumbnailsMode(
            cookies_source.get("thumbnails", "subreddit_preference")
        ),
        nsfw_popular_all=_get_bool_setting_value_from_cookie(
            "nsfw_popular_all", cookies_source
        ),
        nsfw_thumbnails=_get_bool_setting_value_from_cookie(
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


def get_subreddits_and_frontpage_common_context(
    pagination: models.Pagination,
    posts: list[models.Post],
    subreddit: models.Subreddit,
    sorting_mode: models.SubredditSortingMode,
    sorting_period: models.SubredditSortingPeriod,
) -> dict[str, Any]:
    return {
        "pagination": pagination,
        "posts": posts,
        "subreddit": subreddit,
        "current_sorting_mode": sorting_mode,
        "current_sorting_period": sorting_period,
        "has_sorting_period": sorting_mode
        in [models.SubredditSortingMode.CONTROVERSIAL, models.SubredditSortingMode.TOP],
    }
