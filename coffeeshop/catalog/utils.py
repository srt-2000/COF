from __future__ import annotations

from typing import TypedDict


class MenuItem(TypedDict):
    title: str
    url_name: str


main_menu: list[MenuItem] = [
    {"title": "Home", "url_name": "home"},
    {"title": "About us", "url_name": "about"},
    {"title": "Contact us", "url_name": "contact"},
]
"""Main navigation menu of the site.
Contains dictionaries with titles and URL names for main pages.
"""


class DataMixin:
    """Mixin for adding pagination to views.
    
    Attributes:
        paginate_by (int): Number of items per page in pagination.
    """
    paginate_by: int = 2
