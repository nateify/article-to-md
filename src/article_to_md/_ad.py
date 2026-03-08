from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


def remove_by_cosmetic_filters(soup: BeautifulSoup, filters: list[str]):
    """
    Remove elements from BeautifulSoup object based on Adblock Plus generic cosmetic filters.

    Args:
        soup: BeautifulSoup object to modify
        filters: List of filter strings

    Returns:
        Modified BeautifulSoup object
    """
    for filter_line in filters:
        filter_line = filter_line.strip()
        if not filter_line.startswith("##"):
            continue

        selector = filter_line[2:]

        try:
            elements = soup.select(selector)
            for element in elements:
                element.decompose()
        except NotImplementedError:
            continue

    return soup
