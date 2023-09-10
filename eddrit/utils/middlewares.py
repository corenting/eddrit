from contextvars import ContextVar

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

_current_host_ctx_var: ContextVar[str] = ContextVar("CURRENT_HOST_CTX_VAR", default="")


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
