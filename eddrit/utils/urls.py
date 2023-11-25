import tldextract


def get_domain_and_suffix_from_url(url: str) -> str:
    """Get domain name and suffix from url"""
    extracted_domain = tldextract.extract(url)
    return f"{extracted_domain.domain}.{extracted_domain.suffix}"
