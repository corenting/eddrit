def is_homepage(subreddit_title: str) -> bool:
    titles = ["All", "Popular"]
    return subreddit_title in titles
