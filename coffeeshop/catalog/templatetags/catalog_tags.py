from __future__ import annotations

from typing import Any

from ..models import ProductCategory
from ..utils import main_menu
from django import template

register = template.Library()


@register.simple_tag()
def get_main_menu() -> list[dict[str, Any]]:
    """
    Returns the main menu structure for the website navigation.

    Returns:
        List[dict[str, Any]]: List of menu items with their properties
    """
    return main_menu


@register.inclusion_tag("list_categories.html")
def show_categories() -> dict[str, list[ProductCategory]]:
    """
    Renders a template with all available categories.

    Returns:
        Dict[str, List[Category]]: Dictionary containing list of all categories
    """
    cats = ProductCategory.objects.all()
    return {"cats": cats}
