from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from eddrit import exceptions, models
from eddrit.reddit.fetch import (
    get_post,
    get_subreddit_informations,
    get_subreddit_posts,
)
from eddrit.templates import templates
from eddrit.utils import settings
from eddrit.utils.request import redirect_to_age_check, should_redirect_to_age_check


async def subreddit_post(request: Request) -> Response:
    try:
        subreddit_infos = await get_subreddit_informations(request.path_params["name"])
    except exceptions.SubredditUnavailable as e:
        raise HTTPException(status_code=403, detail=e.message)

    post_id = request.path_params["post_id"]
    post = await get_post(request.path_params["name"], post_id)

    if should_redirect_to_age_check(request, post.over18):
        return redirect_to_age_check(request)

    return templates.TemplateResponse(
        "post.html",
        {
            "request": request,
            "subreddit": subreddit_infos,
            "post": post,
            "settings": settings.get_settings_from_request(request),
        },
    )


async def subreddit(request: Request) -> Response:
    # Get sorting mode
    sorting_mode = models.SubredditSortingMode(
        request.path_params.get("sorting_mode", "popular")
    )

    try:
        subreddit_infos = await get_subreddit_informations(request.path_params["name"])
    except exceptions.SubredditUnavailable as e:
        raise HTTPException(status_code=403, detail=e.message)

    if should_redirect_to_age_check(request, subreddit_infos.over18):
        return redirect_to_age_check(request)

    request_pagination = models.Pagination(
        before_post_id=request.query_params.get("before"),
        after_post_id=request.query_params.get("after"),
    )

    posts, response_pagination = await get_subreddit_posts(
        request.path_params["name"], request_pagination, sorting_mode
    )

    return templates.TemplateResponse(
        "posts_list.html",
        {
            "pagination": response_pagination,
            "posts": posts,
            "request": request,
            "settings": settings.get_settings_from_request(request),
            "subreddit": subreddit_infos,
            "current_sorting_mode": sorting_mode,
        },
    )


routes = [
    Route("/{name:str}", endpoint=subreddit),
    Route("/{name:str}/{sorting_mode:str}", endpoint=subreddit),
    Route(
        "/{name:str}/comments/{post_id:str}/{post_title:str}", endpoint=subreddit_post
    ),
]
