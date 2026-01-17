import json
import random
from base64 import standard_b64encode
from typing import Any
from uuid import uuid4

import httpx
import valkey
from loguru import logger

from eddrit.config import PROXY, VALKEY_URL
from eddrit.constants import REDDIT_BASE_API_URL_HOST
from eddrit.exceptions import RateLimitedError
from eddrit.utils.http import get_httpx_transport

OFFICIAL_ANDROID_OAUTH_ID = "ohXpoqrZYub1kg"
OFFICIAL_ANDROID_APP_VERSIONS = [
    "Version 2024.35.0/Build 1857451",
    "Version 2024.34.0/Build 1837909",
    "Version 2024.33.0/Build 1819908",
    "Version 2024.32.1/Build 1813258",
    "Version 2024.32.0/Build 1809095",
    "Version 2024.31.0/Build 1786202",
    "Version 2024.30.0/Build 1770787",
    "Version 2024.29.0/Build 1747562",
    "Version 2024.28.1/Build 1741165",
    "Version 2024.28.0/Build 1737665",
    "Version 2024.26.1/Build 1717435",
    "Version 2024.26.1/Build 1717435",
    "Version 2024.26.0/Build 1710470",
]

_valkey_key_version = (
    "3"  # to bump if the auth mechanism change to not reuse already cached values
)
_valkey_connection_pool = valkey.ConnectionPool.from_url(url=VALKEY_URL)
_valkey_login_lock_key = f"oauth_login_lock_v{_valkey_key_version}"
_valkey_check_headers_lock_key = f"oauth_check_headers_lock_v{_valkey_key_version}"
_valkey_headers_key = f"oauth_headers_v{_valkey_key_version}"


async def oauth_after_request(api_res: httpx.Response) -> None:
    """
    Event hook to:
    - Raise a specific exception if Reddit returns a 429 (rate-limit reached).
    - Refresh oauth credentials if needed
    """
    if api_res.status_code == 429:
        raise RateLimitedError()

    # Handle rate-limiting
    logger.debug(
        f"x-ratelimit-remaining: {api_res.headers.get('x-ratelimit-remaining')} x-ratelimit-reset: {api_res.headers.get('x-ratelimit-reset')} x-ratelimit-used: {api_res.headers.get('x-ratelimit-used')}"
    )
    rate_limit_remaining = api_res.headers.get("x-ratelimit-remaining")
    if rate_limit_remaining:
        rate_limit_remaining_value = float(rate_limit_remaining)
        if rate_limit_remaining_value < 50:
            logger.info("Rate-limit remaining is too low, renewing token")
            oauth_login()
    else:
        logger.debug("Didn't receive x-ratelimit-remaining header in response")


async def oauth_before_request(
    request: httpx.Request,
) -> None:
    """
    Event hook to add the official Android app headers to the request
    """
    # Add the Android official app headers
    request.headers.update(_get_login_headers_from_cache())

    # Add other headers
    request.headers.update(
        {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept-Encoding": "gzip" if request.method == "GET" else "identity",
            "Cookie": "",
            "Host": REDDIT_BASE_API_URL_HOST,
        }
    )

    # Shuffle the headers
    initial_headers_list = list(request.headers.items())
    random.shuffle(initial_headers_list)
    new_headers = dict(initial_headers_list)
    request.headers.clear()
    for header_name, header_value in new_headers.items():
        request.headers[header_name] = header_value

    # For multi subreddits, the user-agent doesn't work so tweak it
    if "+" in request.url.path:
        request.headers.encoding = "utf-8"
        request.headers["User-Agent"] = request.headers["User-Agent"].replace(
            "Android", "Andr\u200boid"
        )


def _get_login_headers_from_cache() -> dict[str, Any]:
    """
    Get the login headers from cache
    """
    valkey_client = valkey.Valkey(connection_pool=_valkey_connection_pool)
    # Check if we have login headers in cache, with lock if multiple workers
    # try to login at same time
    with valkey_client.lock(
        _valkey_check_headers_lock_key, timeout=20, blocking_timeout=5
    ):
        if not valkey_client.exists(_valkey_headers_key):
            oauth_login()

        headers_str: bytes = valkey_client.get(_valkey_headers_key)  # type: ignore
    decoded_headers = json.loads(headers_str.decode())
    return decoded_headers


def oauth_login() -> None:
    """
    Perform OAuth login to get headers matching the official Android app.
    """
    logger.info("Performing OAuth login")
    valkey_client = valkey.Valkey(connection_pool=_valkey_connection_pool)

    with valkey_client.lock(_valkey_login_lock_key, timeout=20, blocking_timeout=5):
        # Generate identity: unique ID + random user-agent
        unique_uuid = str(uuid4())
        android_app_version = random.choice(OFFICIAL_ANDROID_APP_VERSIONS)  # noqa: S311
        android_version = random.choice(range(9, 15))  # noqa: S311
        qos = f"{random.uniform(1.0, 100):.3f}"  # noqa: S311
        video_codecs = "available-codecs=video/avc, video/hevc"
        if random.choice([0, 1]) == 1:  # noqa: S311
            video_codecs += ", video/x-vnd.on2.vp9"

        common_headers = {
            "User-Agent": f"Reddit/{android_app_version}/Android {android_version}",
            "x-reddit-retry": "algo=no-retries",
            "x-reddit-compression": "1",
            "x-reddit-qos": qos,
            "x-reddit-media-codecs": video_codecs,
            "Client-Vendor-Id": unique_uuid,
            "X-Reddit-Device-Id": unique_uuid,
        }
        logger.debug(
            f"Generated headers for official Android app login: {common_headers}"
        )

        # Login
        client = httpx.Client(
            http2=True,
            proxy=PROXY,
            transport=get_httpx_transport(),
        )  # not async but not supported by cachier
        id_to_encode = f"{OFFICIAL_ANDROID_OAUTH_ID}:"
        res = client.post(
            url="https://www.reddit.com/auth/v2/oauth/access-token/loid",
            headers={
                "Authorization": f"Basic {standard_b64encode(id_to_encode.encode()).decode()}",
                **common_headers,
            },
            json={"scopes": ["*", "email", "pii"]},
        )

        if res.is_success:
            oauth_headers = {
                **common_headers,
                "Authorization": f"Bearer {res.json()['access_token']}",
                "x-reddit-loid": res.headers["x-reddit-loid"],
                "x-reddit-session": res.headers["x-reddit-session"],
            }
            valkey_client.set(
                _valkey_headers_key,
                json.dumps(oauth_headers),
                ex=res.json()["expires_in"]
                - 300,  # expires time minus 5 min for renewal margin
            )
        else:
            logger.info(
                f"Got {res.status_code} response for official Android app login: {res.json()}"
            )
            raise RuntimeError(
                "Cannot generate credentials for Reddit by spoofing the official Android app"
            )
