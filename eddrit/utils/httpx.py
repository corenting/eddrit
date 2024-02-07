import httpx

from eddrit.exceptions import RateLimitedError


async def raise_if_rate_limited(api_res: httpx.Response) -> None:
    """Raise a specific exception if Reddit returns a 429 (rate-limit reached)."""
    if api_res.status_code == 429:
        raise RateLimitedError()
