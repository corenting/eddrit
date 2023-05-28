import tldextract

from eddrit import const


def is_media_hosting_domain(image_domain: str) -> bool:
    """
    Check if the given domain is known to be an media hosting domain like imgur.
    """
    _, domain, suffix = tldextract.extract(image_domain)
    return f"{domain}.{suffix}" in const.MEDIA_HOSTING_DOMAINS


def post_is_from_domain(post_domain: str, domain_to_check: str) -> bool:
    """Check if a post is from a given domain"""
    _, domain, suffix = tldextract.extract(post_domain)
    return f"{domain}.{suffix}" == domain_to_check


def domain_has_special_embed_handling(domain: str) -> bool:
    """Check if the given domain is a domain that has a special code for embed handling."""
    _, domain, suffix = tldextract.extract(domain)
    return f"{domain}.{suffix}" in const.DOMAINS_WITH_SPECIAL_EMBED_HANDLING
