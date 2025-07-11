class RedditContentUnavailableError(Exception):
    """
    Raised when reddit content is not available.
    """

    detail = "Content is not available"

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


class UserUnavailableError(Exception):
    """
    Raised when an user is not available.
    """

    detail = "User is not available"


class UserSuspendedError(RedditContentUnavailableError):
    detail = "User suspended"


class UserBlockedError(RedditContentUnavailableError):
    detail = "User blocked"


class UserNotFoundError(RedditContentUnavailableError):
    detail = "User not found"


class SubredditNotFoundError(RedditContentUnavailableError):
    detail = "Subreddit not found"


class ContentCannotBeViewedError(RedditContentUnavailableError):
    def __init__(self, status_code: int, reason: str) -> None:
        super().__init__(status_code)
        self.detail = f"Content cannot be viewed ({reason})"


class WikiPageNotFoundError(RedditContentUnavailableError):
    detail = "Wiki page not found"


class RateLimitedError(RedditContentUnavailableError):
    """
    Raised when rate-limit is reached
    """

    detail = "eddrit made too much requests to Reddit and was rate-limited. Try again later or on another instance"

    def __init__(self) -> None:
        super().__init__(status_code=429)
