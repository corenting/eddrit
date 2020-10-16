from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from eddrit import models
from eddrit.reddit.fetch import get_frontpage_informations, get_frontpage_posts
from eddrit.templates import templates
from eddrit.utils import settings


async def index(request: Request) -> Response:

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
        },
    )


routes = [
    Route("/", endpoint=index),
]
