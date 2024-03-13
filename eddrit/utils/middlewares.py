import http.cookies
from contextvars import ContextVar
from email.utils import format_datetime

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from eddrit.routes.common.cookies import get_default_cookie_settings

_current_host_ctx_var: ContextVar[str] = ContextVar("CURRENT_HOST_CTX_VAR", default="")


class CookiesRefreshMiddleware:
    """Middleware to refresh a specified set of cookies in all responses."""

    def __init__(self, app: ASGIApp, cookies_to_refresh: list[str]) -> None:
        self.app = app
        self.cookies_to_refresh = cookies_to_refresh

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def send_with_refreshed_cookies(message: Message) -> None:
            if message["type"] == "http.response.start":
                initial_request = Request(scope)
                headers = MutableHeaders(scope=message)
                cookie_default_settings = get_default_cookie_settings()

                for cookie_name, cookie_value in initial_request.cookies.items():
                    if cookie_name not in self.cookies_to_refresh:
                        continue

                    # Same code as Response.set_cookie from starlette
                    updated_cookie = http.cookies.SimpleCookie()
                    updated_cookie[cookie_name] = cookie_value
                    updated_cookie[cookie_name]["expires"] = format_datetime(
                        cookie_default_settings.expiration_date, usegmt=True
                    )
                    updated_cookie[cookie_name]["path"] = "/"
                    updated_cookie[cookie_name]["secure"] = (
                        cookie_default_settings.secure
                    )
                    updated_cookie[cookie_name]["httponly"] = (
                        cookie_default_settings.http_only
                    )
                    updated_cookie[cookie_name]["samesite"] = "lax"
                    headers.append(
                        key="set-cookie", value=updated_cookie.output(header="").strip()
                    )

            await send(message)

        await self.app(scope, receive, send_with_refreshed_cookies)


class NoReferrerMiddleware:
    """Middleware adding a no-referrer Referrer-Policy on all responses"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def send_with_extra_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["Referrer-Policy"] = "no-referrer"

            await send(message)

        await self.app(scope, receive, send_with_extra_headers)


class CurrentHostMiddleware:
    """Middleware to set a contextvar holding the value of the current host"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        host = Request(scope).url.hostname or "example.com"

        token = _current_host_ctx_var.set(host)
        await self.app(scope, receive, send)
        _current_host_ctx_var.reset(token)


def get_current_host() -> str:
    """Get the current host."""
    return _current_host_ctx_var.get()
