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


async def get_frontpage_informations() -> models.Subreddit:
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
    return await _get_posts_for_url(
        http_client, "https://www.reddit.com/.json", pagination, is_popular_or_all=True
    )


async def search_posts(
    http_client: httpx.AsyncClient, input_text: str
) -> list[models.Post]:
    res = await http_client.get(f"https://old.reddit.com/search.json?q={input_text}")

    _raise_if_rate_limited(res)

    posts, _ = parser.parse_posts(res.json(), False)
    return posts


async def search_subreddits(
    http_client: httpx.AsyncClient, input_text: str
) -> list[models.Subreddit]:
    res = await http_client.get(
        f"https://www.reddit.com/subreddits/search.json?q={input_text}"
    )
    _raise_if_rate_limited(res)

    results = res.json()["data"]["children"]
    return [
        parser.parse_subreddit_informations(
            item["data"]["display_name"], item["data"]["over18"], item
        )
        for item in results
    ]


async def get_subreddit_informations(
    http_client: httpx.AsyncClient, subreddit: str
) -> models.Subreddit:
    if subreddit == "all":
        return models.Subreddit(
            title="All",
            name="all",
            show_thumbnails=True,
            public_description=None,
            over18=False,
            icon_url=None,
        )
    elif subreddit == "popular":
        return await get_frontpage_informations()

    # If multi subreddit
    if "+" in subreddit:
        return await _get_multi_informations(http_client, subreddit)

    return await _get_subreddit_informations(http_client, subreddit)


async def get_subreddit_posts(
    http_client: httpx.AsyncClient,
    subreddit: str,
    pagination: models.Pagination,
    sorting_mode: models.SubredditSortingMode,
    sorting_period: models.SubredditSortingPeriod,
) -> tuple[list[models.Post], models.Pagination]:
    # Always add sorting period as it is ignored
    # when not needed
    url = (
        f"https://www.reddit.com/r/{subreddit}/.json?t={sorting_period.value}"
        if sorting_mode == models.SubredditSortingMode.POPULAR
        else f"https://www.reddit.com/r/{subreddit}/{sorting_mode.value}.json?t={sorting_period.value}"
    )
    return await _get_posts_for_url(http_client, url, pagination)


async def get_post(
    http_client: httpx.AsyncClient, subreddit: str, post_id: str
) -> models.PostWithComments:
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/.json"
    params = {"limit": 100}
    res = await http_client.get(url, params=params)

    _raise_if_rate_limited(res)

    post = parser.parse_post(
        res.json()[0]["data"]["children"][0]["data"], is_popular_or_all=False
    )

    return models.PostWithComments(
        **asdict(post), comments=parser.parse_comments(res.json()[1]["data"])
    )


async def get_comments(
    http_client: httpx.AsyncClient, subreddit: str, post_id: str, comment_id: str
) -> Iterable[models.PostComment | models.PostCommentShowMore]:
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/comments/{comment_id}/.json"
    params = {"limit": 100}
    res = await http_client.get(url, params=params)

    _raise_if_rate_limited(res)

    return parser.parse_comments(res.json()[1]["data"])


async def _get_posts_for_url(
    http_client: httpx.AsyncClient,
    url: str,
    pagination: models.Pagination,
    is_popular_or_all: bool = False,
) -> tuple[list[models.Post], models.Pagination]:
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
        return parser.parse_posts(json_res, is_popular_or_all)


async def _get_subreddit_informations(
    http_client: httpx.AsyncClient, name: str
) -> models.Subreddit:
    res = await http_client.get(f"https://www.reddit.com/r/{name}/about/.json")

    _raise_if_rate_limited(res)

    # If subreddit not found, the API redirects us to search endpoint
    if res.status_code == 302 and "search" in res.headers["location"]:
        raise SubredditNotFoundError()

    _raise_if_subreddit_is_not_available(res)

    json = res.json()
    return parser.parse_subreddit_informations(name, json["data"]["over18"], json)


async def _get_multi_informations(
    http_client: httpx.AsyncClient, name: str
) -> models.Subreddit:
    # Check if there is a redirect to know if it's an NSFW multi
    res = await http_client.head(f"https://old.reddit.com/r/{name}")

    _raise_if_rate_limited(res)

    if len(res.history) > 0 and res.history[0].status_code != 200:
        raise SubredditNotFoundError()

    over18 = res.status_code == 302 and "over18" in res.headers["location"]
    return parser.parse_subreddit_informations(name, over18)


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
