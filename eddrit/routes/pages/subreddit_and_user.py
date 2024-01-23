from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route

from eddrit import exceptions, models
from eddrit.reddit.fetch import (
    get_post,
    get_subreddit_or_user_information,
    get_subreddit_or_user_posts,
)
from eddrit.routes.common.context import (
    get_canonical_url_context,
    get_posts_pages_common_context,
    get_templates_common_context,
)
from eddrit.templates import templates


def _redirect_to_age_check(request: Request) -> RedirectResponse:
    return RedirectResponse(url=f"/over18?dest={request.url!s}")


def _should_redirect_to_age_check(request: Request, over18: bool) -> bool:
    return over18 and request.cookies.get("over18", "0") != "1"


async def subreddit_post(request: Request) -> Response:
    try:
        subreddit_infos = await get_subreddit_or_user_information(
            request.state.http_client, request.path_params["name"], is_user=False
        )
        post_id = request.path_params["post_id"]
        post = await get_post(
            request.state.http_client, request.path_params["name"], post_id
        )
    except exceptions.SubredditUnavailableError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except exceptions.RateLimitedError as e:
        raise HTTPException(status_code=429, detail=e.message)

    if _should_redirect_to_age_check(request, post.over18):
        return _redirect_to_age_check(request)

    return templates.TemplateResponse(
        "post.html",
        {
            "subreddit": subreddit_infos,
            "post": post,
            "title_link": request.url_for("subreddit", path=post.subreddit),
            **get_templates_common_context(request),
            **get_canonical_url_context(request),
        },
    )


async def subreddit_or_user(request: Request) -> Response:
    """
    Endpoint for a subreddit or an user page.
    """

    # Get sorting mode
    sorting_mode = models.SubredditSortingMode(
        request.path_params.get("sorting_mode", "popular")
    )

    # Get sorting period
    sorting_period = models.SubredditSortingPeriod(request.query_params.get("t", "day"))

    is_user = request.url.path.startswith("/user")
    try:
        subreddit_infos = await get_subreddit_or_user_information(
            request.state.http_client, request.path_params["name"], is_user
        )
        if _should_redirect_to_age_check(request, subreddit_infos.over18):
            return _redirect_to_age_check(request)

        request_pagination = models.Pagination(
            before_post_id=request.query_params.get("before"),
            after_post_id=request.query_params.get("after"),
        )

        posts, response_pagination = await get_subreddit_or_user_posts(
            request.state.http_client,
            request.path_params["name"],
            request_pagination,
            sorting_mode,
            sorting_period,
            is_user,
        )
    except exceptions.SubredditUnavailableError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except exceptions.RateLimitedError as e:
        raise HTTPException(status_code=429, detail=e.message)

    return templates.TemplateResponse(
        "posts_list.html",
        {
            **get_posts_pages_common_context(
                response_pagination,
                posts,
                subreddit_infos,
                sorting_mode,
                sorting_period,
            ),
            **get_templates_common_context(request),
            **get_canonical_url_context(request),
        },
    )


routes = [
    Route("/{name:str}", endpoint=subreddit_or_user),
    Route("/{name:str}/{sorting_mode:str}", endpoint=subreddit_or_user),
    Route(
        "/{name:str}/comments/{post_id:str}/{post_title:str}", endpoint=subreddit_post
    ),
    # register with trailing slash too: the permalinks given by reddit for these URLs have a trailing slash
    # so we want to avoid an extra redirect
    Route(
        "/{name:str}/comments/{post_id:str}/{post_title:str}/", endpoint=subreddit_post
    ),
]
