"""
Factory for creating order service instances with dependencies.
"""

from __future__ import annotations

from typing import Protocol

from order.services import DatabaseOrderRepository, EmailOrderNotification, OrderService


class OrderFactory(Protocol):
    """
    Factory for creating order service instances.
    Provides centralized service creation and simplifies implementation replacement.
    """

    @staticmethod
    def create_order_service() -> OrderService:
        """
        Create an OrderService instance with configured dependencies.
        Returns:
            OrderService: An instance of OrderService with repository and notifier.
        """
        return OrderService(repository=DatabaseOrderRepository(), notifier=EmailOrderNotification())
