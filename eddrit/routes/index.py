from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from eddrit import models
from eddrit.reddit.fetch import get_frontpage_informations, get_frontpage_posts
from eddrit.templates import templates
from eddrit.utils import settings


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

    request_pagination = models.Pagination(
        before_post_id=request.query_params.get("before"),
        after_post_id=request.query_params.get("after"),
    )

    informations = await get_frontpage_informations()
    posts, response_pagination = await get_frontpage_posts(request_pagination)

    return templates.TemplateResponse(
        "posts_list.html",
        {
            "pagination": response_pagination,
            "posts": posts,
            "request": request,
            "settings": settings.get_settings_from_request(request),
            "subreddit": informations,
            "current_sorting_mode": sorting_mode,
        },
    )


routes = [
    Route("/{sorting_mode:str}", endpoint=index),
    Route("/", endpoint=index),
]
