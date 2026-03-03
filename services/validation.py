from urllib.parse import urlparse

from services.platforms import is_supported_url


def validate_video_url(url: str) -> tuple[bool, str]:
    if not url:
        return False, 'Please provide a URL.'

    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'}:
        return False, 'URL must start with http:// or https://.'

    if not parsed.netloc:
        return False, 'Invalid URL.'

    if not is_supported_url(url):
        return (
            False,
            'Unsupported source. This demo only supports public links from configured platforms.',
        )

    return True, ''
