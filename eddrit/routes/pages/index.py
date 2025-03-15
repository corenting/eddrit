from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from eddrit import models
from eddrit.reddit.fetch import (
    get_frontpage_information,
    get_subreddit_or_user_posts,
    get_subreddit_or_user_rss_feed,
)
from eddrit.routes.common.context import (
    get_canonical_url_context,
    get_posts_pages_common_context,
    get_templates_common_context,
)
from eddrit.routes.common.request import get_instance_scheme_and_netloc
from eddrit.templates import templates


def _get_request_context_for_index(
    request: Request,
) -> tuple[
    models.SubredditSortingMode, models.SubredditSortingPeriod, models.Pagination
]:
    """
    Get common request context for the index page.
    """
    # Get sorting mode
    sorting_mode = models.SubredditSortingMode(
        request.path_params.get("sorting_mode", models.SubredditSortingMode.HOT)
    )

    # Get sorting period
    sorting_period = models.SubredditSortingPeriod(
        request.query_params.get("t", models.SubredditSortingPeriod.DAY)
    )

    request_pagination = models.Pagination(
        before_post_id=request.query_params.get("before"),
        after_post_id=request.query_params.get("after"),
    )

    return (sorting_mode, sorting_period, request_pagination)


async def index(request: Request) -> Response:
    sorting_mode, sorting_period, request_pagination = _get_request_context_for_index(
        request
    )
    information = await get_frontpage_information()
    posts, response_pagination = await get_subreddit_or_user_posts(
        request.state.http_client,
        "popular",
        request_pagination,
        sorting_mode,
        sorting_period,
        is_user=False,
    )

    rss_feed_url = request.url.replace(path=f"{request.url.path}.rss")

    return templates.TemplateResponse(
        "posts_list.html",
        {
            **get_posts_pages_common_context(
                response_pagination, posts, information, sorting_mode, sorting_period
            ),
            **get_templates_common_context(request),
            **get_canonical_url_context(request),
            "rss_feed_url": rss_feed_url,
        },
    )


async def index_rss(request: Request):
    sorting_mode, sorting_period, pagination = _get_request_context_for_index(request)

    rss_feed = await get_subreddit_or_user_rss_feed(
        request.state.http_client,
        "popular",
        pagination,
        sorting_mode,
        sorting_period,
        is_user=False,
        eddrit_instance_scheme_and_netloc=get_instance_scheme_and_netloc(request),
    )

    return Response(content=rss_feed, media_type="application/atom+xml")


routes = [
    # Index
    Route("/.rss", endpoint=index_rss),
    Route("/", endpoint=index),
    # Index with sorting mode
    Route("/{sorting_mode:str}/.rss", endpoint=index_rss),
    Route("/{sorting_mode:str}.rss", endpoint=index_rss),
    Route("/{sorting_mode:str}", endpoint=index),
]
