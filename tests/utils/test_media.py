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
    assert media.is_media_hosting_domain(domain) == expected
