"""
Interfaces and typed data structures for order services, repositories, and notifications.
"""

from __future__ import annotations

from typing import Protocol

from cart.interfaces import ICart
from django.contrib.auth.models import User
from order.domains import OrderCreateData, OrderData


class IOrderService(Protocol):
    """
    Interface for order service operations.
    """

    def create_order(
        self,
        user: User,
        cart: ICart,
        form_data: dict[str, str],
        applied_promo_id: int | None,
    ) -> OrderData:
        """
        Create a new order.
        Args:
            user (User): The user creating the order.
            cart (ICart): Shopping cart with items.
            form_data (dict[str, str]): Form data with delivery information.
            applied_promo_id (int | None): ID of applied promo code.

        Returns:
            OrderData: The created order data including DB-generated fields.

        """
        pass


class IOrderNotification(Protocol):
    """
    Interface for order notifications.
    """

    def send_order_notification(self, order_id: int) -> None:
        """
        Send notification about new order.
        Args:
            order_id (int): The order_id to find order object in db and send notification about.
        """
        pass


class IOrderRepository(Protocol):
    """
    Interface for order data storage.
    """

    def save_order(self, order_data: OrderCreateData) -> OrderData:
        """
        Save order to storage.
        Args:
            order_data (OrderCreateData): Order data to save.
        Returns:
            OrderData: The saved order data including DB-generated fields.
        """
        pass
