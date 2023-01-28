import tldextract

from eddrit import const


def is_image_or_video_host(image_domain: str) -> bool:
    _, domain, suffix = tldextract.extract(image_domain)
    return f"{domain}.{suffix}" in const.IMAGE_HOSTING_DOMAINS


def is_from_external_preview_reddit_domain(url: str) -> bool:
    subdomain, domain, suffix = tldextract.extract(url)
    return f"{domain}.{suffix}" == "redd.it" and "external-preview" in subdomain


def post_is_from_domain(post_domain: str, domain_to_check: str) -> bool:
    """Check if a post is from a given domain"""
    _, domain, suffix = tldextract.extract(post_domain)
    return f"{domain}.{suffix}" == domain_to_check
