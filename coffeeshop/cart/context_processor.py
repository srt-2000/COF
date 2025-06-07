"""
Context processor for the shopping cart.

This module provides a context processor that adds the cart to the template context.
"""
from __future__ import annotations

from typing import TypedDict

from django.http import HttpRequest

from cart.factory import CartFactory


class CartContext(TypedDict):
    cart: object  # Можно заменить на Cart, если нет циклических импортов


def cart(request: HttpRequest) -> CartContext:
    """
    Add the cart to the template context.

    Args:
        request: The HTTP request object.

    Returns:
        CartContext: A dictionary containing the cart.
    """
    cart_instance = CartFactory.create_from_request(request)
    return {"cart": cart_instance}
