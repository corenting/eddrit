class SubredditUnavailableError(Exception):
    """
    Raised when a subreddit is not available.
    """

    message = "Subreddit is not available"


class SubredditNotFoundError(SubredditUnavailableError):
    message = "Subreddit not found"


class SubredditIsPrivateError(SubredditUnavailableError):
    message = "Subreddit is private"


class SubredditIsQuarantinedError(SubredditUnavailableError):
    message = "Subreddit is quarantined"


class SubredditIsBannedError(SubredditUnavailableError):
    message = "Subreddit is banned"


class RateLimitedError(Exception):
    """
    Raised when rate-limit is reached
    """

    message = "eddrit made too much requests to Reddit and was rate-limited.Try again later or try another instance"
