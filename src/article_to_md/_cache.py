import os
from datetime import timedelta
from pathlib import Path

import requests_cache

EASYLIST_URL = (
    "https://raw.githubusercontent.com/easylist/easylist/refs/heads/master/easylist/easylist_general_hide.txt"
)


def get_cache_dir():
    """Get platform-appropriate cache directory."""

    if os.name == "nt":
        cache_base = os.getenv("LOCALAPPDATA", Path("~").expanduser())
    else:
        cache_base = os.getenv("XDG_CACHE_HOME", Path("~/.cache").expanduser())

    cache_dir = Path(cache_base) / "article-to-md"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_easylist_filters():
    """Retrieve Easylist filters utilizing cache"""
    cache_dir = get_cache_dir()
    cache_path = cache_dir / "easylist_cache"

    session = requests_cache.CachedSession(
        cache_name=str(cache_path), expire_after=timedelta(days=6), backend="sqlite", stale_if_error=True
    )

    try:
        response = session.get(EASYLIST_URL, timeout=10)
        response.raise_for_status()
        return response.text.splitlines()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch EasyList: {e}")
