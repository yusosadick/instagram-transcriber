import re

from backend.core.errors import UnsupportedURLError

INSTAGRAM_URL_PATTERN = re.compile(
    r"^https?://(www\.|m\.)?instagram\.com/(reel|reels|p|tv)/[A-Za-z0-9_-]+/?(\?.*)?$"
)


def is_instagram_url(source: str) -> bool:
    return bool(INSTAGRAM_URL_PATTERN.match(source.strip()))


def validate_instagram_url(url: str) -> None:
    if not is_instagram_url(url):
        raise UnsupportedURLError(
            "Not a valid Instagram Reel/Post URL. Expected something like "
            "https://www.instagram.com/reel/<shortcode>/"
        )
