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


class UserNotFoundError(RedditContentUnavailableError):
    detail = "User not found"


class SubredditNotFoundError(RedditContentUnavailableError):
    detail = "Subreddit not found"


class SubredditCannotBeViewedError(RedditContentUnavailableError):
    def __init__(self, status_code: int, reason: str) -> None:
        super().__init__(status_code)
        self.detail = f"Subreddit is {reason}"


class WikiPageNotFoundError(RedditContentUnavailableError):
    detail = "Wiki page not found"


class RateLimitedError(RedditContentUnavailableError):
    """
    Raised when rate-limit is reached
    """

    detail = "eddrit made too much requests to Reddit and was rate-limited.Try again later or try another instance"

    def __init__(self) -> None:
        super().__init__(status_code=429)
