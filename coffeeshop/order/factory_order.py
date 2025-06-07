from __future__ import annotations

from typing import Protocol

from order.services import DatabaseOrderRepository, EmailOrderNotification, OrderService


class OrderFactory(Protocol):
    """
    Order factory:
    - Centralized service creation
    - Simplifies implementation replacement
    """

    @staticmethod
    def create_order_service() -> OrderService:
        """
        Create order service with dependencies

        Returns:
            OrderService instance with configured dependencies
        """
        return OrderService(repository=DatabaseOrderRepository(), notifier=EmailOrderNotification())
