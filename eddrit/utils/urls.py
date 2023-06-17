import tldextract


def get_domain_and_suffix_from_url(url: str) -> str:
    """Get domain name and suffix from url"""
    _, domain, suffix = tldextract.extract(url)
    return f"{domain}.{suffix}"
