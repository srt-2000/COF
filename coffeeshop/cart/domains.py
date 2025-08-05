"""
Type definitions for cart data structures.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TypedDict

from catalog.models import Product


class CartData(TypedDict):
    """TypedDict for cart item data stored in session."""

    quantity: int
    price: float | None


class CartItemServiceData(TypedDict):
    """TypedDict for cart item data used in services and iteration."""

    product: Product
    quantity: int
    price: float
    total_price: float


class CartContext(TypedDict):
    """TypedDict for cart context processor."""

    cart: object
    total_cart_price: Decimal
    discount_sum: Decimal
    total_price: Decimal
