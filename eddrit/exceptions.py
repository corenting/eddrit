class SubredditUnavailableError(Exception):
    """
    Raised when a subreddit is not available.
    """

    message = "Subreddit is not available"


class UserUnavailableError(Exception):
    """
    Raised when an user is not available.
    """

    message = "User is not available"


class UserNotFoundError(SubredditUnavailableError):
    message = "User not found"


class SubredditNotFoundError(SubredditUnavailableError):
    message = "Subreddit not found"


class SubredditCannotBeViewedError(SubredditUnavailableError):
    def __init__(self, reason: str) -> None:
        self.message = f"Subreddit is {reason}"


class RateLimitedError(Exception):
    """
    Raised when rate-limit is reached
    """

    message = "eddrit made too much requests to Reddit and was rate-limited.Try again later or try another instance"
