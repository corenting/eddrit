class SubredditUnavailable(Exception):
    """
    Raised when a subreddit is not available.
    """

    message = "Subreddit is not available"


class SubredditNotFound(SubredditUnavailable):
    message = "Subreddit not found"


class SubredditIsPrivate(SubredditUnavailable):
    message = "Subreddit is private"


class SubredditIsQuarantined(SubredditUnavailable):
    message = "Subreddit is quarantined"


class SubredditIsBanned(SubredditUnavailable):
    message = "Subreddit is banned"


class RateLimited(Exception):
    """
    Raised when rate-limit is reached
    """

    message = "eddrit made too much requests to Reddit and was rate-limited.Try again later or try another instance"
