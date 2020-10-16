import pytest

from eddrit.utils.cookies import get_cookie_value_from_bool


@pytest.mark.parametrize("bool_value,expected", [(True, "1"), (False, "0"),])
def test_get_cookie_value_from_bool(bool_value: bool, expected: str) -> None:
    assert get_cookie_value_from_bool(bool_value) == expected
