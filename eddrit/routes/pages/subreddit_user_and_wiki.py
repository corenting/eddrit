from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route

from eddrit import models
from eddrit.reddit.fetch import (
    get_post,
    get_subreddit_information,
    get_subreddit_or_user_posts,
    get_user_information,
    get_wiki_page,
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
    """
    Endpoint for a post page.
    """
    subreddit_infos = await get_subreddit_information(
        request.state.http_client, request.path_params["name"]
    )
    post_id = request.path_params["post_id"]
    post = await get_post(
        request.state.http_client, request.path_params["name"], post_id
    )

    if _should_redirect_to_age_check(request, post.over18):
        return _redirect_to_age_check(request)

    return templates.TemplateResponse(
        "post.html",
        {
            "about_information": subreddit_infos,
            "post": post,
            "title_link": request.url_for("subreddit", path=post.subreddit),
            **get_templates_common_context(request),
            **get_canonical_url_context(request),
        },
    )


async def wiki_page(request: Request) -> Response:
    """
    Endpoint for a wiki page.
    """
    subreddit_name = request.path_params["name"]
    wiki_page_name = request.path_params["page_name"]

    wiki_page_item = await get_wiki_page(
        request.state.http_client, subreddit_name, wiki_page_name
    )

    return templates.TemplateResponse(
        "wiki_page.html",
        {
            "wiki_page": wiki_page_item,
            **get_templates_common_context(request),
            **get_canonical_url_context(request),
        },
    )


async def subreddit_or_user(request: Request) -> Response:
    """
    Endpoint for a subreddit or an user page.
    """
    is_user = request.url.path.startswith("/user")

    # Get sorting mode
    sorting_mode = (
        models.SubredditSortingMode(request.path_params.get("sorting_mode", "popular"))
        if not is_user
        else models.UserSortingMode(request.query_params.get("sort", "new"))
    )

    # Get sorting period
    sorting_period = models.SubredditSortingPeriod(
        request.query_params.get("t", "month" if not is_user else "all")
    )

    # Get information
    if is_user:
        information = await get_user_information(
            request.state.http_client, request.path_params["name"]
        )
    else:
        information = await get_subreddit_information(
            request.state.http_client, request.path_params["name"]
        )

    if _should_redirect_to_age_check(request, information.over18):
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
    return templates.TemplateResponse(
        "posts_list.html",
        {
            **get_posts_pages_common_context(
                response_pagination,
                posts,
                information,
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
    Route("/{name:str}/wiki/{page_name:str}", endpoint=wiki_page),
]
