from typing import Any

from starlette.requests import Request

from eddrit import models


def get_templates_common_context(request: Request) -> dict[str, Any]:
    settings = models.Settings(
        nsfw_popular_all=request.cookies.get("nsfw_popular_all", "0") == "1",
        nsfw_thumbnails=request.cookies.get("nsfw_thumbnails", "0") == "1",
    )

    return {
        "request": request,
        "settings": settings,
    }


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
