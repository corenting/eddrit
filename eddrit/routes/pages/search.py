from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from eddrit import exceptions
from eddrit.reddit.fetch import search_posts, search_subreddits
from eddrit.routes.common.context import (
    get_canonical_url_context,
    get_templates_common_context,
)
from eddrit.templates import templates


async def search(request: Request) -> Response:
    input_text = request.query_params.get("q", "")

    try:
        subreddit_search_results = await search_subreddits(
            request.state.http_client, input_text
        )
        posts_search_results = await search_posts(request.state.http_client, input_text)
    except exceptions.RateLimitedError as e:
        raise HTTPException(status_code=429, detail=e.message)

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "subreddits": subreddit_search_results[:3],
            "posts": posts_search_results,
            **get_templates_common_context(request),
            **get_canonical_url_context(request),
        },
    )


routes = [
    Route("/search", endpoint=search, methods=["GET"]),
]
