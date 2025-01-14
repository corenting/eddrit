import json
import random
from base64 import standard_b64encode
from typing import Any
from uuid import uuid4

import httpx
import valkey
from loguru import logger

from eddrit.config import VALKEY_URL
from eddrit.exceptions import RateLimitedError

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
    "Version 2024.25.3/Build 1703490",
    "Version 2024.25.2/Build 1700401",
    "Version 2024.25.0/Build 1693595",
    "Version 2024.24.1/Build 1682520",
    "Version 2024.24.0/Build 1675730",
    "Version 2024.23.1/Build 1665606",
    "Version 2024.23.0/Build 1660290",
    "Version 2024.22.1/Build 1652272",
    "Version 2024.22.0/Build 1645257",
    "Version 2024.21.0/Build 1631686",
    "Version 2024.20.2/Build 1624969",
    "Version 2024.20.1/Build 1615586",
    "Version 2024.20.0/Build 1612800",
    "Version 2024.19.0/Build 1593346",
    "Version 2024.18.1/Build 1585304",
    "Version 2024.18.0/Build 1577901",
    "Version 2024.17.0/Build 1568106",
    "Version 2024.16.0/Build 1551366",
    "Version 2024.15.0/Build 1536823",
    "Version 2024.14.0/Build 1520556",
    "Version 2024.13.0/Build 1505187",
    "Version 2024.12.0/Build 1494694",
    "Version 2024.11.0/Build 1480707",
    "Version 2024.10.1/Build 1478645",
    "Version 2024.10.0/Build 1470045",
    "Version 2024.08.0/Build 1439531",
    "Version 2024.07.0/Build 1429651",
    "Version 2024.06.0/Build 1418489",
    "Version 2024.05.0/Build 1403584",
    "Version 2024.04.0/Build 1391236",
    "Version 2024.03.0/Build 1379408",
    "Version 2024.02.0/Build 1368985",
    "Version 2023.50.1/Build 1345844",
    "Version 2023.50.0/Build 1332338",
    "Version 2023.49.1/Build 1322281",
    "Version 2023.49.0/Build 1321715",
    "Version 2023.48.0/Build 1319123",
    "Version 2023.47.0/Build 1303604",
    "Version 2023.45.0/Build 1281371",
    "Version 2023.44.0/Build 1268622",
    "Version 2023.43.0/Build 1257426",
    "Version 2023.42.0/Build 1245088",
]

_valkey_connection_pool = valkey.ConnectionPool.from_url(url=VALKEY_URL)
_valkey_login_lock_key = "oauth_login_lock"
_valkey_check_headers_lock_key = "oauth_check_headers_lock"
_valkey_headers_key = "oauth_headers"


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
        if rate_limit_remaining_value < 15:
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
    logger.debug("Performing OAuth login")
    valkey_client = valkey.Valkey(connection_pool=_valkey_connection_pool)

    with valkey_client.lock(_valkey_login_lock_key, timeout=20, blocking_timeout=5):
        # Generate identity: unique ID + random user-agent
        unique_uuid = str(uuid4())
        android_app_version = random.choice(OFFICIAL_ANDROID_APP_VERSIONS)  # noqa: S311
        android_version = random.choice(range(9, 15))  # noqa: S311
        common_headers = {
            "Client-Vendor-Id": unique_uuid,
            "X-Reddit-Device-Id": unique_uuid,
            "User-Agent": f"Reddit/{android_app_version}/Android {android_version}",
        }
        logger.debug(
            f"Generated headers for official Android app login: {common_headers}"
        )

        # Login
        client = httpx.Client()  # not async but not supported by cachier
        id_to_encode = f"{OFFICIAL_ANDROID_OAUTH_ID}:"
        res = client.post(
            url="https://accounts.reddit.com/api/access_token",
            headers={
                "Authorization": f"Basic {standard_b64encode(id_to_encode.encode()).decode()}",
                **common_headers,
            },
            json={"scopes": ["*", "email"]},
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
                ex=82800,  # 23 hours
            )
        else:
            logger.debug(
                f"Got {res.status_code} response for official Android app login: {res.json()}"
            )
            raise RuntimeError(
                "Cannot generate credentials for Reddit by spoofing the official Android app"
            )
