import pytest

from eddrit.utils import math


@pytest.mark.parametrize(
    "num,expected",
    [
        (-3, "-"),
        (14, ""),
    ],
)
def test_sign_for_negative(num: int, expected: str) -> None:
    assert math.sign_for_negative(num) == expected


@pytest.mark.parametrize(
    "num,expected",
    [
        (-3, "-3"),
        (14, "14"),
        (343, "343"),
        (140004, "140k"),
        (1030003, "1030k"),
    ],
)
def test_pretty_big_num(num: int, expected: str) -> None:
    assert math.pretty_big_num(num) == expected
