from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from eddrit.config import DEBUG


@dataclass
class CookieSettings:
    secure: bool
    http_only: bool
    expiration_date: datetime


def get_default_cookie_settings() -> CookieSettings:
    """
    Get default cookie settings
    """
    return CookieSettings(
        secure=not DEBUG,
        http_only=True,
        expiration_date=datetime.now(tz=UTC) + timedelta(days=90),
    )


def get_bool_setting_value_from_cookie(
    name: str, cookies: dict[str, str], default: bool = False
) -> bool:
    """Get boolean value of a given setting according to the given cookies.

    If setting not present, use default value
    """
    if name in cookies:
        return cookies[name] == "1"
    else:
        return default
