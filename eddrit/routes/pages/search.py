from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from eddrit.reddit.fetch import search_posts, search_subreddits
from eddrit.templates import templates


async def search(request: Request) -> Response:
    # TODO : generate search context for posts and comments

    input_text = request.query_params.get("q", "")
    subreddit_search_results = await search_subreddits(input_text)
    posts_search_results = await search_posts(input_text)

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "subreddits": subreddit_search_results[:3],
            "posts": posts_search_results,
        },
    )


routes = [
    Route("/search", endpoint=search, methods=["GET"]),
]
