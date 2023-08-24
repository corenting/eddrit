from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from eddrit import exceptions, models
from eddrit.reddit.fetch import get_frontpage_informations, get_frontpage_posts
from eddrit.routes.common.context import (
    get_canonical_url_context,
    get_subreddits_and_frontpage_common_context,
    get_templates_common_context,
)
from eddrit.templates import templates


async def index(request: Request) -> Response:
    # Get sorting mode
    try:
        sorting_mode = models.SubredditSortingMode(
            request.path_params.get("sorting_mode", "popular")
        )
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid sorting mode for index page"
        )

    # Get sorting period
    try:
        sorting_period = models.SubredditSortingPeriod(
            request.query_params.get("t", "day")
        )
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid sorting period for index page"
        )

    request_pagination = models.Pagination(
        before_post_id=request.query_params.get("before"),
        after_post_id=request.query_params.get("after"),
    )

    informations = await get_frontpage_informations()
    try:
        posts, response_pagination = await get_frontpage_posts(
            request.state.http_client, request_pagination
        )
    except exceptions.RateLimited as e:
        raise HTTPException(status_code=429, detail=e.message)

    return templates.TemplateResponse(
        "posts_list.html",
        {
            **get_subreddits_and_frontpage_common_context(
                response_pagination, posts, informations, sorting_mode, sorting_period
            ),
            **get_templates_common_context(request),
            **get_canonical_url_context(request),
        },
    )


routes = [
    Route("/{sorting_mode:str}", endpoint=index),
    Route("/", endpoint=index),
]
