from __future__ import annotations

from decimal import Decimal
from typing import NotRequired, TypedDict

from django.contrib.auth.models import User


class OrderCreateData(TypedDict):
    """TypedDict for order creation input data."""

    user: User
    user_email: str
    delivery_address: str
    phone: str
    cart_price: Decimal
    applied_promo_name: str | None
    applied_promo_status: bool
    discount_sum: Decimal
    total_price: Decimal
    items: list[OrderItemData]


class OrderItemData(TypedDict):
    """TypedDict for order item data."""

    product_id: int
    product_name: str
    quantity: int
    price: float


class OrderData(OrderCreateData):
    """TypedDict for full order data including DB-generated fields."""

    user: NotRequired[User]
    order_id: int
    time_created: str


class PromoContext(TypedDict):
    """TypedDict for promo context to order data."""

    applied_promo_name: str | None
    applied_promo_status: bool
