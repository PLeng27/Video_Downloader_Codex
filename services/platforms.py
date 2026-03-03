from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Platform:
    name: str
    domains: tuple[str, ...]


SUPPORTED_PLATFORMS: tuple[Platform, ...] = (
    Platform('YouTube (public videos)', ('youtube.com', 'www.youtube.com', 'youtu.be')),
    Platform('Vimeo (public videos)', ('vimeo.com', 'www.vimeo.com')),
    Platform('Internet Archive', ('archive.org', 'www.archive.org')),
    Platform('Pexels', ('pexels.com', 'www.pexels.com')),
)


def get_supported_domains() -> set[str]:
    domains: set[str] = set()
    for platform in SUPPORTED_PLATFORMS:
        domains.update(platform.domains)
    return domains


def is_supported_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or '').lower()
    if not host:
        return False
    return host in get_supported_domains()
