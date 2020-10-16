from eddrit.config import DEBUG


def cookie_is_secure() -> bool:
    return not DEBUG


def get_cookie_value_from_bool(bool_value: bool) -> str:
    return "1" if bool_value else "0"
