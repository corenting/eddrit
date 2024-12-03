class RedditContentUnavailableError(Exception):
    """
    Raised when reddit content is not available.
    """

    message = "Content is not available"


class UserUnavailableError(Exception):
    """
    Raised when an user is not available.
    """

    message = "User is not available"


class UserNotFoundError(RedditContentUnavailableError):
    message = "User not found"


class SubredditNotFoundError(RedditContentUnavailableError):
    message = "Subreddit not found"


class SubredditCannotBeViewedError(RedditContentUnavailableError):
    def __init__(self, reason: str) -> None:
        self.message = f"Subreddit is {reason}"


class WikiPageNotFoundError(RedditContentUnavailableError):
    message = "Wiki page not found"


class RateLimitedError(Exception):
    """
    Raised when rate-limit is reached
    """

    message = "eddrit made too much requests to Reddit and was rate-limited.Try again later or try another instance"
