from dataclasses import asdict
from typing import Dict, Iterable, List, Tuple, Union

import httpx

from eddrit import models
from eddrit.exceptions import (
    SubredditIsBanned,
    SubredditIsPrivate,
    SubredditIsQuarantined,
    SubredditNotFound,
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
    pagination: models.Pagination,
) -> Tuple[List[models.Post], models.Pagination]:
    return await _get_posts_for_url(
        "https://www.reddit.com/.json", pagination, is_popular_or_all=True
    )


async def search_posts(input_text: str) -> list[models.Post]:
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://old.reddit.com/search.json?q={input_text}")

    posts, _ = parser.parse_posts(res.json(), False)
    return posts


async def search_subreddits(input_text: str) -> list[models.Subreddit]:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"https://www.reddit.com/subreddits/search.json?q={input_text}"
        )

    results = res.json()["data"]["children"]
    return [
        parser.parse_subreddit_informations(
            item["data"]["display_name"], item["data"]["over18"], item
        )
        for item in results
    ]


async def get_subreddit_informations(subreddit: str) -> models.Subreddit:
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
        return await _get_multi_informations(subreddit)

    return await _get_subreddit_informations(subreddit)


async def get_subreddit_posts(
    subreddit: str,
    pagination: models.Pagination,
    sorting_mode: models.SubredditSortingMode,
    sorting_period: models.SubredditSortingPeriod,
) -> Tuple[List[models.Post], models.Pagination]:
    # Always add sorting period as it is ignored
    # when not needed
    url = (
        f"https://www.reddit.com/r/{subreddit}/.json?t={sorting_period.value}"
        if sorting_mode == models.SubredditSortingMode.POPULAR
        else f"https://www.reddit.com/r/{subreddit}/{sorting_mode.value}.json?t={sorting_period.value}"
    )
    return await _get_posts_for_url(url, pagination)


async def get_post(subreddit: str, post_id: str) -> models.PostWithComments:
    async with httpx.AsyncClient() as client:
        url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/.json"
        params = {"limit": 100}
        res = await client.get(url, params=params)

    post = parser.parse_post(
        res.json()[0]["data"]["children"][0]["data"], is_popular_or_all=False
    )

    return models.PostWithComments(
        **asdict(post), comments=parser.parse_comments(res.json()[1]["data"])
    )


async def get_comments(
    subreddit: str, post_id: str, comment_id: str
) -> Iterable[Union[models.PostComment, models.PostCommentShowMore]]:
    async with httpx.AsyncClient() as client:
        url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}/comments/{comment_id}/.json"
        params = {"limit": 100}
        res = await client.get(url, params=params)

    return parser.parse_comments(res.json()[1]["data"])


async def _get_posts_for_url(
    url: str, pagination: models.Pagination, is_popular_or_all: bool = False
) -> Tuple[List[models.Post], models.Pagination]:
    async with httpx.AsyncClient() as client:
        params: Dict[str, Union[str, int]] = {}
        if pagination.before_post_id:
            params = {"before": pagination.before_post_id, "count": 25}
        elif pagination.after_post_id:
            params = {"after": pagination.after_post_id, "count": 25}

        res = await client.get(url, params=params)

    return parser.parse_posts(res.json(), is_popular_or_all)


async def _get_subreddit_informations(name: str) -> models.Subreddit:
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://www.reddit.com/r/{name}/about/.json")

    # If subreddit not found, the API redirects us to search endpoint
    if res.status_code == 302 and "search" in res.headers["location"]:
        raise SubredditNotFound()

    _raise_if_subreddit_is_not_available(res)

    json = res.json()
    return parser.parse_subreddit_informations(name, json["data"]["over18"], json)


async def _get_multi_informations(name: str) -> models.Subreddit:
    # Check if there is a redirect to know if it's an NSFW multi
    async with httpx.AsyncClient() as client:
        res = await client.head(f"https://old.reddit.com/r/{name}")

    if len(res.history) > 0 and res.history[0].status_code != 200:
        raise SubredditNotFound()

    over18 = res.status_code == 302 and "over18" in res.headers["location"]
    return parser.parse_subreddit_informations(name, over18)


def _raise_if_subreddit_is_not_available(api_res: httpx.Response) -> None:
    """Raise an exception if the subreddit is not available (banned, private etc.)"""

    json = api_res.json()

    # Check for banned subreddits
    if api_res.status_code == 404 and json.get("reason") == "banned":
        raise SubredditIsBanned()

    # Check for quarantined subreddits
    if api_res.status_code == 403 and json.get("reason") == "quarantined":
        raise SubredditIsQuarantined()

    # Check for private subreddits
    if api_res.status_code == 403 and json.get("reason") == "private":
        raise SubredditIsPrivate()

    # Check for subreddit not found
    if len(api_res.history) > 0 and api_res.history[0].status_code != 200:
        raise SubredditNotFound()

    # If error, consider we didn't find the subreddit
    if json.get("error") == 404:
        raise SubredditNotFound()
