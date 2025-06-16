from __future__ import annotations

from decimal import Decimal
from typing import Protocol, TypedDict

from django.contrib.auth.models import User

from order.models import Order


class OrderItemData(TypedDict):
    """Typed dictionary for order item data"""

    product_id: int
    product_name: str
    quantity: int
    price: Decimal


class OrderData(TypedDict):
    """Typed dictionary for order data"""

    order_id: int
    user_email: str
    delivery_address: str
    phone: str
    total_price: Decimal
    time_created: str
    items: list[OrderItemData]


class IOrderService(Protocol):
    """Interface for order service operations"""

    def create_order(
        self, user: User, items: list[OrderItemData], total_price: Decimal, delivery_address: str, phone: str
    ) -> OrderData:
        """Create a new order

        Args:
            user: The user creating the order
            items: List of items in the order
            total_price: Total price of the order
            delivery_address: Delivery address
            phone: Customer phone number

        Returns:
            OrderData containing the created order information
        """
        pass


class IOrderNotification(Protocol):
    """Interface for order notifications"""

    def send_order_notification(self, order: Order) -> None:
        """Send notification about new order

        Args:
            order: The order to send notification about
        """
        pass


class IOrderRepository(Protocol):
    """Interface for order data storage"""

    def save_order(self, order_data: OrderData) -> OrderData:
        """Save order to storage

        Args:
            order_data: Order data to save

        Returns:
            OrderData containing the saved order information
        """
        pass
