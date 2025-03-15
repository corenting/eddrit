from starlette.requests import Request


def get_instance_scheme_and_netloc(request: Request) -> str:
    """
    Get eddrit's current instance scheme and netloc as a string.
    """
    return f"{request.url.scheme}://{request.url.netloc}"
