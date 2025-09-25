from __future__ import annotations

from catalog.domains import MenuItem

main_menu: list[MenuItem] = [
    {"title": "Home", "url_name": "home"},
    {"title": "About us", "url_name": "about"},
    {"title": "Contact us", "url_name": "contact"},
    {"title": "Promo", "url_name": "promo_list"},
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
