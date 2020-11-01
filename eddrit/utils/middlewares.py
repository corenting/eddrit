from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

from eddrit.config import PROXY_COUNT


class NoReferrerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers["Referrer-Policy"] = "no-referrer"
        return response


# Taken from https://github.com/encode/uvicorn/blob/b8a3ab98f7f4d01265f2f91d32e5f8386a8d1003/uvicorn/middleware/proxy_headers.py
# under BSD 3-Clause Licence (https://github.com/encode/uvicorn/blob/master/LICENSE.md)
class ProxyHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.num_proxies = PROXY_COUNT

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope["headers"])

            if b"x-forwarded-proto" in headers:
                # Determine if the incoming request was http or https based on
                # the X-Forwarded-Proto header.
                x_forwarded_proto = headers[b"x-forwarded-proto"].decode("ascii")
                scope["scheme"] = x_forwarded_proto.strip()

            if b"x-forwarded-for" in headers:
                # Determine the client address from the last trusted IP in the
                # X-Forwarded-For header. We've lost the connecting client's port
                # information by now, so only include the host.
                x_forwarded_for = headers[b"x-forwarded-for"].decode("ascii")
                host = x_forwarded_for.split(",")[-self.num_proxies].strip()
                port = 0
                scope["client"] = (host, port)

        await self.app(scope, receive, send)
