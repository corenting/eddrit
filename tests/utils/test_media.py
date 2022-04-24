import pytest

from eddrit.utils import media


@pytest.mark.parametrize(
    "domain,expected",
    [
        ("imgur.com", True),
        ("github.com", False),
    ],
)
def test_is_image_or_video_host(domain: str, expected: bool) -> None:
    assert media.is_image_or_video_host(domain) == expected


@pytest.mark.parametrize(
    "domain,expected",
    [
        ("external-preview.redd.it", True),
        ("preview.redd.it", False),
        ("i.redd.it", False),
        ("reddit.com", False),
        ("github.com", False),
    ],
)
def test_is_from_external_preview_reddit_domain(domain: str, expected: bool) -> None:
    assert media.is_from_external_preview_reddit_domain(domain) == expected
