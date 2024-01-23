from collections.abc import Iterable
from dataclasses import asdict
from json import JSONDecodeError

import httpx
from loguru import logger

from eddrit import models
from eddrit.exceptions import (
    RateLimitedError,
    SubredditIsBannedError,
    SubredditIsPrivateError,
    SubredditIsQuarantinedError,
    SubredditNotFoundError,
)
from eddrit.reddit import parser


async def get_frontpage_information() -> models.Subreddit:
    return models.Subreddit(
        title="Popular",
        show_thumbnails=True,
        public_description=None,
        name="popular",
        over18=False,
        icon_url=None,
    )


async def get_frontpage_posts(
    http_client: httpx.AsyncClient,
    pagination: models.Pagination,
) -> tuple[list[models.Post], models.Pagination]:
    ret = await _get_posts_for_url(
        http_client, "https://old.reddit.com/.json", pagination, is_popular_or_all=True
    )
    return ret  # type: ignore


async def search_posts(
    http_client: httpx.AsyncClient, input_text: str
) -> list[models.Post]:
    res = await http_client.get(f"https://old.reddit.com/search.json?q={input_text}")

    _raise_if_rate_limited(res)

    posts, _ = parser.parse_posts_and_comments(res.json(), False)
    # Ignore response type as there is no models.PostComment for search posts
    return posts  # type: ignore


async def search_subreddits(
    http_client: httpx.AsyncClient, input_text: str
) -> list[models.Subreddit]:
    res = await http_client.get(
        f"https://old.reddit.com/subreddits/search.json?q={input_text}"
    )
    _raise_if_rate_limited(res)

    results = res.json()["data"]["children"]
    return [
        parser.parse_subreddit_information(
            item["data"]["display_name"], item["data"]["over18"], item
        )
        for item in results
    ]


async def get_subreddit_or_user_information(
    http_client: httpx.AsyncClient, subreddit_or_user_name: str, is_user: bool
) -> models.Subreddit:
    """
    Get information about a subreddit (or an user if is_user set to True).
    """
    if is_user:
        return models.Subreddit(
            title="All",
            name="all",
            show_thumbnails=True,
            public_description=None,
            over18=False,
            icon_url=None,
        )
    if subreddit_or_user_name == "all":
        # TODO: check what details are really needed for user
        return models.Subreddit(
            title=subreddit_or_user_name,
            name=subreddit_or_user_name,
            show_thumbnails=True,
            public_description=None,
            over18=False,
            icon_url=None,
        )
    elif subreddit_or_user_name == "popular":
        return await get_frontpage_information()

    # If multi subreddit
    if "+" in subreddit_or_user_name:
        return await _get_multi_information(http_client, subreddit_or_user_name)

    return await _get_subreddit_information(http_client, subreddit_or_user_name)


async def get_subreddit_or_user_posts(
    http_client: httpx.AsyncClient,
    subreddit_or_username: str,
    pagination: models.Pagination,
    sorting_mode: models.SubredditSortingMode,
    sorting_period: models.SubredditSortingPeriod,
    is_user: bool,
) -> tuple[list[models.Post | models.PostComment], models.Pagination]:
    """
    Get posts for a subreddit (or an user if is_user is set).

    Will include post comments if it's an user.
    """
    # Always add sorting period as it is ignored
    # when not needed
    path_part = "user" if is_user else "r"
    url = (
        f"https://old.reddit.com/{path_part}/{subreddit_or_username}/.json?t={sorting_period.value}"
        if sorting_mode == models.SubredditSortingMode.POPULAR
        else f"https://old.reddit.com/r/{subreddit_or_username}/{sorting_mode.value}.json?t={sorting_period.value}"
    )
    return await _get_posts_for_url(http_client, url, pagination)


async def get_post(
    http_client: httpx.AsyncClient, subreddit: str, post_id: str
) -> models.PostWithComments:
    url = f"https://old.reddit.com/r/{subreddit}/comments/{post_id}/.json"
    params = {"limit": 100}
    res = await http_client.get(url, params=params)

    _raise_if_rate_limited(res)

    post = parser.parse_post(
        res.json()[0]["data"]["children"][0]["data"], is_popular_or_all=False
    )

    return models.PostWithComments(
        **asdict(post), comments=parser.parse_comments_tree(res.json()[1]["data"])
    )


async def get_comments(
    http_client: httpx.AsyncClient, subreddit: str, post_id: str, comment_id: str
) -> Iterable[models.PostComment | models.PostCommentShowMore]:
    url = f"https://old.reddit.com/r/{subreddit}/comments/{post_id}/comments/{comment_id}/.json"
    params = {"limit": 100}
    res = await http_client.get(url, params=params)

    _raise_if_rate_limited(res)

    return parser.parse_comments_tree(res.json()[1]["data"])


async def _get_posts_for_url(
    http_client: httpx.AsyncClient,
    url: str,
    pagination: models.Pagination,
    is_popular_or_all: bool = False,
) -> tuple[list[models.Post | models.PostComment], models.Pagination]:
    params: dict[str, str | int] = {}
    if pagination.before_post_id:
        params = {"before": pagination.before_post_id, "count": 25}
    elif pagination.after_post_id:
        params = {"after": pagination.after_post_id, "count": 25}

    res = await http_client.get(url, params=params)
    _raise_if_rate_limited(res)

    try:
        json_res = res.json()
    except JSONDecodeError:
        logger.exception(
            "Cannot parse JSON from response with status code {api_status_code} and content {api_content}",
            api_status_code=res.status_code,
            api_content=res.text,
        )
        raise
    else:
        return parser.parse_posts_and_comments(json_res, is_popular_or_all)


async def _get_subreddit_information(
    http_client: httpx.AsyncClient, name: str
) -> models.Subreddit:
    res = await http_client.get(f"https://old.reddit.com/r/{name}/about/.json")

    _raise_if_rate_limited(res)

    # If subreddit not found, the API redirects us to search endpoint
    if res.status_code == 302 and "search" in res.headers["location"]:
        raise SubredditNotFoundError()

    _raise_if_subreddit_is_not_available(res)

    json = res.json()
    return parser.parse_subreddit_information(name, json["data"]["over18"], json)


async def _get_multi_information(
    http_client: httpx.AsyncClient, name: str
) -> models.Subreddit:
    # Check if there is a redirect to know if it's an NSFW multi
    res = await http_client.head(f"https://old.reddit.com/r/{name}")

    _raise_if_rate_limited(res)

    if len(res.history) > 0 and res.history[0].status_code != 200:
        raise SubredditNotFoundError()

    over18 = res.status_code == 302 and "over18" in res.headers["location"]
    return parser.parse_subreddit_information(name, over18)


def _raise_if_rate_limited(api_res: httpx.Response) -> None:
    """Raise an exception if Reddit returns a 429 (rate-limit reached)."""
    if api_res.status_code == 429:
        raise RateLimitedError()


def _raise_if_subreddit_is_not_available(api_res: httpx.Response) -> None:
    """Raise an exception if the subreddit is not available (banned, private etc.)"""

    try:
        json = api_res.json()
    except JSONDecodeError:
        logger.exception(
            "Cannot parse JSON from response with status code {api_status_code} and content {api_content}",
            api_status_code=api_res.status_code,
            api_content=api_res.text,
        )
        return None

    # Check for banned subreddits
    if api_res.status_code == 404 and json.get("reason") == "banned":
        raise SubredditIsBannedError()

    # Check for quarantined subreddits
    if api_res.status_code == 403 and json.get("reason") == "quarantined":
        raise SubredditIsQuarantinedError()

    # Check for private subreddits
    if api_res.status_code == 403 and json.get("reason") == "private":
        raise SubredditIsPrivateError()

    # Check for subreddit not found
    if len(api_res.history) > 0 and api_res.history[0].status_code != 200:
        raise SubredditNotFoundError()

    # If error, consider we didn't find the subreddit
    if json.get("error") == 404:
        raise SubredditNotFoundError()
