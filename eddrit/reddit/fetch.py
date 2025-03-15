from collections.abc import Iterable
from dataclasses import asdict
from json import JSONDecodeError

import httpx
from loguru import logger

from eddrit import models
from eddrit.constants import REDDIT_BASE_API_URL
from eddrit.exceptions import (
    ContentCannotBeViewedError,
    RateLimitedError,
    SubredditNotFoundError,
    UserNotFoundError,
    WikiPageNotFoundError,
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
        wiki_enabled=False,
    )


async def search_posts(
    http_client: httpx.AsyncClient, input_text: str
) -> list[models.Post]:
    res = await http_client.get(f"{REDDIT_BASE_API_URL}/search.json?q={input_text}")
    posts, _ = parser.parse_posts_and_comments(res.json())

    # Ignore response type as there is no models.PostComment for search posts
    return posts  # type: ignore


async def search_subreddits(
    http_client: httpx.AsyncClient, input_text: str
) -> list[models.Subreddit]:
    res = await http_client.get(
        f"{REDDIT_BASE_API_URL}/subreddits/search.json?q={input_text}"
    )
    results = res.json()["data"]["children"]
    return [
        parser.parse_subreddit_information(
            item["data"]["display_name"], item["data"]["over18"], item
        )
        for item in results
    ]


async def get_subreddit_information(
    http_client: httpx.AsyncClient, subreddit_name: str
) -> models.Subreddit:
    """
    Get information about a subreddit
    """
    if subreddit_name == "all":
        return models.Subreddit(
            title=subreddit_name,
            name=subreddit_name,
            show_thumbnails=True,
            public_description=None,
            over18=False,
            icon_url=None,
            wiki_enabled=False,
        )
    elif subreddit_name == "popular":
        return await get_frontpage_information()

    # If multi subreddit
    if "+" in subreddit_name:
        return await _get_multi_information(http_client, subreddit_name)

    return await _get_subreddit_information(http_client, subreddit_name)


def _get_pagination_query_parameters(
    pagination: models.Pagination,
) -> dict:
    params = {}
    if pagination.before_post_id:
        params["before"] = pagination.before_post_id
    elif pagination.after_post_id:
        params["after"] = pagination.after_post_id
        params["count"] = 25

    return params


def _get_url_and_query_parameters_for_subreddit_or_user(
    subreddit_or_username: str,
    sorting_mode: models.SubredditSortingMode | models.UserSortingMode,
    pagination: models.Pagination,
    sorting_period: models.SubredditSortingPeriod,
    is_user: bool,
) -> tuple[str, dict]:
    """Get URL and query parameters to use for subreddit or user posts query."""
    path_part = "user" if is_user else "r"

    query_params = {}
    if is_user:
        url = f"{REDDIT_BASE_API_URL}/{path_part}/{subreddit_or_username}/.json"
        query_params["t"] = sorting_period.value
        if sorting_mode != models.UserSortingMode.NEW:
            query_params["sort"] = sorting_mode.value

    else:
        if sorting_mode == models.SubredditSortingMode.HOT:
            url = f"{REDDIT_BASE_API_URL}/{path_part}/{subreddit_or_username}/.json"
            query_params["t"] = sorting_period.value
        else:
            url = f"{REDDIT_BASE_API_URL}/{path_part}/{subreddit_or_username}/{sorting_mode.value}.json"
            query_params["t"] = sorting_period.value

    # If it's the popular subreddit (aka the homepage), use global geo filter
    # in case the /r/popular URL is used instead of the / one.
    if subreddit_or_username == "popular":
        query_params["geo_filter"] = "GLOBAL"

    query_params |= _get_pagination_query_parameters(pagination)

    return (url, query_params)


async def get_subreddit_or_user_posts(
    http_client: httpx.AsyncClient,
    subreddit_or_username: str,
    pagination: models.Pagination,
    sorting_mode: models.SubredditSortingMode | models.UserSortingMode,
    sorting_period: models.SubredditSortingPeriod,
    is_user: bool,
) -> tuple[list[models.Post | models.PostComment], models.Pagination]:
    """
    Get posts for a subreddit (or an user if is_user is set).

    Will include post comments if it's an user.
    """
    url, query_params = _get_url_and_query_parameters_for_subreddit_or_user(
        subreddit_or_username, sorting_mode, pagination, sorting_period, is_user
    )

    return await _get_posts_for_url(http_client, url, query_params=query_params)


async def get_subreddit_or_user_rss_feed(
    http_client: httpx.AsyncClient,
    subreddit_or_username: str,
    pagination: models.Pagination,
    sorting_mode: models.SubredditSortingMode | models.UserSortingMode,
    sorting_period: models.SubredditSortingPeriod,
    is_user: bool,
    eddrit_instance_scheme_and_netloc: str,
) -> str:
    """
    Get the RSS feed for a subreddit or an user page.

    Returns the RSS feed as text.
    """
    url, query_params = _get_url_and_query_parameters_for_subreddit_or_user(
        subreddit_or_username, sorting_mode, pagination, sorting_period, is_user
    )

    return await _get_rss_feed_from_reddit(
        http_client, url, query_params, eddrit_instance_scheme_and_netloc
    )


async def _get_rss_feed_from_reddit(
    http_client: httpx.AsyncClient,
    url: str,
    query_params: dict,
    eddrit_instance_scheme_and_netloc: str,
) -> str:
    """
    Get RSS feed from reddit, replace links to point to current instance and return it.
    """
    url = url.removesuffix(".json")
    url += ".rss"

    res = await http_client.get(url, params=query_params)
    _raise_if_content_is_not_available(res, is_json=False)

    rss_feed_content = res.text
    rss_feed_content = rss_feed_content.replace(
        "https://www.reddit.com", eddrit_instance_scheme_and_netloc
    )
    return rss_feed_content


def _get_url_for_post(subreddit: str, post_id: str, is_user: bool):
    """
    Get the URL to query to fetch a post
    """
    path_part = "user" if is_user else "r"
    return f"{REDDIT_BASE_API_URL}/{path_part}/{subreddit}/comments/{post_id}/.json"


async def get_post(
    http_client: httpx.AsyncClient,
    subreddit_or_username: str,
    post_id: str,
    is_user: bool,
) -> models.PostWithComments:
    """
    Get a post in a subreddit or an user page
    """
    url = _get_url_for_post(subreddit_or_username, post_id, is_user)
    res = await http_client.get(url)

    post = parser.parse_post(res.json()[0]["data"]["children"][0]["data"])

    return models.PostWithComments(
        **asdict(post), comments=parser.parse_comments_tree(res.json()[1]["data"])
    )


async def get_post_rss(
    http_client: httpx.AsyncClient,
    subreddit_or_username: str,
    post_id: str,
    eddrit_instance_scheme_and_netloc: str,
    is_user: bool,
) -> str:
    url = _get_url_for_post(subreddit_or_username, post_id, is_user)
    url = url.removesuffix(".json")
    url += ".rss"
    return await _get_rss_feed_from_reddit(
        http_client, url, {}, eddrit_instance_scheme_and_netloc
    )


async def get_wiki_page(
    http_client: httpx.AsyncClient, subreddit: str, page_name: str
) -> models.WikiPage:
    url = f"{REDDIT_BASE_API_URL}/r/{subreddit}/wiki/{page_name}.json"
    res = await http_client.get(url)

    _raise_if_content_is_not_available(res)

    json_content = res.json()
    content = parser.clean_content(json_content["data"]["content_html"])

    return models.WikiPage(
        content_html=content, page_name=page_name, subreddit_name=subreddit
    )


async def get_comments(
    http_client: httpx.AsyncClient, subreddit: str, post_id: str, comment_id: str
) -> Iterable[models.PostComment | models.PostCommentShowMore]:
    url = f"{REDDIT_BASE_API_URL}/r/{subreddit}/comments/{post_id}/comments/{comment_id}/.json"
    res = await http_client.get(url)

    return parser.parse_comments_tree(res.json()[1]["data"])


async def _get_posts_for_url(
    http_client: httpx.AsyncClient,
    url: str,
    query_params: dict | None = None,
) -> tuple[list[models.Post | models.PostComment], models.Pagination]:
    res = await http_client.get(url, params=query_params)
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
        return parser.parse_posts_and_comments(json_res)


async def get_user_information(
    http_client: httpx.AsyncClient, name: str
) -> models.User:
    res = await http_client.get(f"{REDDIT_BASE_API_URL}/user/{name}/about/.json")

    # If user not found, the API redirects us to search endpoint
    if res.status_code == 404:
        raise UserNotFoundError(res.status_code)

    json = res.json()
    return parser.parse_user_information(json)


async def _get_subreddit_information(
    http_client: httpx.AsyncClient, name: str
) -> models.Subreddit:
    res = await http_client.get(
        f"{REDDIT_BASE_API_URL}/r/{name}/about/.json?raw_json=1"
    )

    # If subreddit not found, the API redirects us to search endpoint
    if res.status_code == 302 and "search" in res.headers["location"]:
        raise SubredditNotFoundError(status_code=404)

    _raise_if_content_is_not_available(res)

    json = res.json()
    return parser.parse_subreddit_information(name, json["data"]["over18"], json)


async def _get_multi_information(
    http_client: httpx.AsyncClient, name: str
) -> models.Subreddit:
    # Check if there is a redirect to know if it's an NSFW multi
    res = await http_client.head(f"{REDDIT_BASE_API_URL}/r/{name}")

    if len(res.history) > 0 and res.history[0].status_code != 200:
        raise SubredditNotFoundError(status_code=404)

    over18 = res.status_code == 302 and "over18" in res.headers["location"]
    return parser.parse_subreddit_information(name, over18)


def _raise_if_content_is_not_available(
    api_res: httpx.Response, is_json: bool = True
) -> None:
    """Raise an exception if the subreddit is not available (banned, private etc.)"""

    # Check for HTML 403 blocked page
    if api_res.status_code == 403 and "blocked by network security" in api_res.text:
        raise RateLimitedError()

    json = {}
    if is_json:
        try:
            json = api_res.json()
        except JSONDecodeError:
            logger.exception(
                "Cannot parse JSON from response with status code {api_status_code} and content {api_content}",
                api_status_code=api_res.status_code,
                api_content=api_res.text,
            )
            return None

    # Check for not found wiki pages
    if (
        api_res.status_code == 404
        and is_json
        and json.get("reason") == "PAGE_NOT_FOUND"
    ):
        raise WikiPageNotFoundError(status_code=api_res.status_code)

    # Check for banned subreddits
    if api_res.status_code == 404 and is_json and json.get("reason") == "banned":
        raise ContentCannotBeViewedError(api_res.status_code, "banned")

    # Check for subreddits that cannot be viewed (quarantine, privated, gated)
    if api_res.status_code == 403 and is_json and (reason := json.get("reason")):
        raise ContentCannotBeViewedError(api_res.status_code, reason)

    # Check for subreddit not found
    if len(api_res.history) > 0 and api_res.history[0].status_code != 200:
        raise SubredditNotFoundError(status_code=api_res.status_code)

    # If error, consider we didn't find the subreddit
    if is_json and json.get("error") == 404:
        raise SubredditNotFoundError(status_code=api_res.status_code)
