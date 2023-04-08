from typing import Any
from urllib.parse import urlparse
from eddrit import models
from starlette.requests import Request


def get_templates_common_context(request: Request) -> dict[str, Any]:
    settings = models.Settings(
        nsfw_popular_all=request.cookies.get("nsfw_popular_all", "0") == "1",
        nsfw_thumbnails=request.cookies.get("nsfw_thumbnails", "0") == "1",
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
