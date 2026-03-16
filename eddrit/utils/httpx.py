from json import JSONDecodeError

import httpx
from httpx_curl_cffi import AsyncCurlTransport, CurlTransport
from loguru import logger

from eddrit.exceptions import (
    ContentCannotBeViewedError,
    RateLimitedError,
    SubredditNotFoundError,
    UserBlockedError,
    UserNotFoundError,
    UserSuspendedError,
    WikiPageNotFoundError,
)

IMPERSONATE = "chrome131_android"


def get_httpx_transport() -> httpx.BaseTransport:
    """Get an HTTPX transport with fingerprint impersonation."""
    return CurlTransport(impersonate=IMPERSONATE, default_headers=True)


def get_httpx_async_transport() -> httpx.AsyncBaseTransport:
    """Get an HTTPX transport with fingerprint impersonation."""
    return AsyncCurlTransport(impersonate=IMPERSONATE, default_headers=True)


async def raise_if_content_is_not_available(api_res: httpx.Response) -> None:
    """Response hook: raise if Reddit content is unavailable (banned, private etc.)."""
    await api_res.aread()

    request_path = str(api_res.request.url.path)
    is_user_path = "/user/" in request_path
    is_subreddit_path = "/r/" in request_path
    has_json = not request_path.endswith(".rss") and api_res.request.method != "HEAD"

    # Rate-limit: HTML 403 blocked page (applies to all requests)
    if api_res.status_code == 403 and "blocked by network security" in api_res.text:
        raise RateLimitedError()

    # Parse JSON body when applicable (not a list)
    json_dict_body: dict = {}
    if has_json:
        try:
            parsed = api_res.json()
        except JSONDecodeError:
            logger.exception(
                "Cannot parse JSON from response with status code {api_status_code}"
                " and content {api_content}",
                api_status_code=api_res.status_code,
                api_content=api_res.text,
            )
            raise
        if isinstance(parsed, dict):
            json_dict_body = parsed

    # User-specific checks
    if is_user_path and api_res.status_code == 404:
        raise UserNotFoundError(api_res.status_code)
    if is_user_path and json_dict_body.get("data", {}).get("is_suspended", False):
        raise UserSuspendedError(api_res.status_code)
    if is_user_path and json_dict_body.get("data", {}).get("is_blocked", False):
        raise UserBlockedError(api_res.status_code)

    # Wiki page not found
    if api_res.status_code == 404 and json_dict_body.get("reason") == "PAGE_NOT_FOUND":
        raise WikiPageNotFoundError(status_code=api_res.status_code)

    # Banned subreddit
    if api_res.status_code == 404 and json_dict_body.get("reason") == "banned":
        raise ContentCannotBeViewedError(api_res.status_code, "banned")

    # Quarantined/private/gated
    if api_res.status_code == 403 and (reason := json_dict_body.get("reason")):
        raise ContentCannotBeViewedError(api_res.status_code, reason)

    # Subreddit-specific not-found checks
    if (
        is_subreddit_path
        and api_res.status_code == 302
        and "search" in api_res.headers.get("location", "")
    ):
        raise SubredditNotFoundError(status_code=404)

    if (
        is_subreddit_path
        and len(api_res.history) > 0
        and api_res.history[0].status_code != 200
    ):
        raise SubredditNotFoundError(status_code=api_res.status_code)

    if is_subreddit_path and json_dict_body.get("error") == 404:
        raise SubredditNotFoundError(status_code=api_res.status_code)
