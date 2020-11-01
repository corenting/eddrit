import pytest
from starlette.requests import Request

from eddrit.utils import settings
from eddrit.utils.settings import get_settings_from_request


def test_get_settings_from_request_true() -> None:
    request = Request(
        scope={
            "type": "http",
            "headers": {},
        }
    )
    request.cookies["nsfw_popular_all"] = "1"
    request.cookies["nsfw_thumbnails"] = "1"

    res = get_settings_from_request(request)

    assert res.nsfw_popular_all is True
    assert res.nsfw_thumbnails is True


def test_get_settings_from_request_false() -> None:
    request = Request(
        scope={
            "type": "http",
            "headers": {},
        }
    )
    request.cookies["nsfw_popular_all"] = "0"
    request.cookies["nsfw_thumbnails"] = "0"

    res = get_settings_from_request(request)

    assert res.nsfw_popular_all is False
    assert res.nsfw_thumbnails is False


def test_get_settings_from_request_garbage() -> None:
    request = Request(
        scope={
            "type": "http",
            "headers": {},
        }
    )
    request.cookies["nsfw_popular_all"] = "garbage"
    request.cookies["nsfw_thumbnails"] = "garbage"

    res = get_settings_from_request(request)

    assert res.nsfw_popular_all is False
    assert res.nsfw_thumbnails is False
