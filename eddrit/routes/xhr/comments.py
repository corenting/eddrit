from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from eddrit.reddit.fetch import get_comments
from eddrit.templates import templates


async def comments(request: Request) -> Response:
    """
    Return the comments tree as HTML starting at the given comment for the given post.
    """
    # Check parameters
    post_id = request.query_params.get("post_id")
    subreddit_name = request.query_params.get("subreddit")
    comment_id = request.query_params.get("comment_id")
    if not comment_id or not subreddit_name or not post_id:
        return PlainTextResponse(None, status_code=400)

    comments = await get_comments(subreddit_name, post_id, comment_id)

    return templates.TemplateResponse(
        "comments_xhr.html",
        {
            "subreddit_name": subreddit_name,
            "request": request,
            "comments": comments,
            "post_id": post_id,
        },
    )


routes = [
    Route("/xhr", endpoint=comments),
]
