import pytest
from starlette.requests import Request

from eddrit.utils.request import get_checkbox_from_form, should_redirect_to_age_check


@pytest.mark.parametrize(
    "post_is_over18,over18_cookie,expected",
    [(True, "0", True), (True, "1", False), (False, "1", False), (False, "0", False),],
)
def test_should_redirect_to_age_check(
    post_is_over18: bool, over18_cookie: str, expected: bool
) -> None:
    request = Request(scope={"type": "http", "headers": {},})
    request.cookies["over18"] = over18_cookie

    assert should_redirect_to_age_check(request, post_is_over18) == expected


@pytest.mark.parametrize(
    "value,expected", [("on", True), ("off", False), ("fake", False),]
)
def test_get_checkbox_from_form(value: str, expected: bool) -> None:
    form_data = {"test": value}
    assert get_checkbox_from_form(form_data, "test") == expected
