import httpx
from httpx_curl_cffi import AsyncCurlTransport, CurlTransport

IMPERSONATE = "chrome131_android"


def get_httpx_transport() -> httpx.BaseTransport:
    """Get an HTTPX transport with fingerprint impersonation."""
    return CurlTransport(impersonate=IMPERSONATE, default_headers=True)


def get_httpx_async_transport() -> httpx.AsyncBaseTransport:
    """Get an HTTPX transport with fingerprint impersonation."""
    return AsyncCurlTransport(impersonate=IMPERSONATE, default_headers=True)
