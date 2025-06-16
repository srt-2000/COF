from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string

from .interfaces import IOrderNotification, IOrderRepository, IOrderService, OrderData, OrderItemData
from .models import Order, OrderItem


class OrderService(IOrderService):
    """
    Service for order operations:
    - Coordinates order creation process
    - Independent of specific storage and notification implementations
    """

    def __init__(self, repository: IOrderRepository, notifier: IOrderNotification) -> None:
        self.repository = repository
        self.notifier = notifier

    def create_order(
        self, user: User, items: list[OrderItemData], total_price: Decimal, delivery_address: str, phone: str
    ) -> OrderData:
        """
        Create a new order

        Args:
            user: User creating the order
            items: List of items in the order
            total_price: Total price of the order
            delivery_address: Delivery address
            phone: Customer phone number

        Returns:
            OrderData containing the created order information
        """
        order_data: OrderData = {
            "user": user,
            "user_email": user.email,
            "delivery_address": delivery_address,
            "phone": phone,
            "total_price": total_price,
            "items": items,
        }

        saved_order = self.repository.save_order(order_data)
        order = Order.objects.get(id=saved_order["order_id"])
        self.notifier.send_order_notification(order)

        return saved_order


class DatabaseOrderRepository(IOrderRepository):
    """
    Repository for database operations:
    - Encapsulates order storage logic
    - Works with Django models
    """

    def save_order(self, order_data: OrderData) -> OrderData:
        """
        Save order to database

        Args:
            order_data: Order data to save

        Returns:
            OrderData containing the saved order information
        """
        with transaction.atomic():
            order = Order.objects.create(
                user=order_data["user"],
                delivery_address=order_data["delivery_address"],
                phone=order_data["phone"],
                total_price=order_data["total_price"],
            )

            order_items = [
                {
                    "product_name": OrderItem.objects.create(
                        order=order,
                        product_id=item["product_id"],
                        product_name=item["product_name"],
                        quantity=item["quantity"],
                        price=item["price"],
                    ).product_name,
                    "quantity": item["quantity"],
                    "price": item["price"],
                }
                for item in order_data["items"]
            ]

            return {
                "order_id": order.id,
                "user_email": order.user.email,
                "delivery_address": order.delivery_address,
                "phone": order.phone,
                "total_price": order.total_price,
                "time_created": order.time_created,
                "items": order_items,
            }


class EmailOrderNotification(IOrderNotification):
    """
    Email notification service:
    - Sends email to administrator about new order
    - Uses templates for email generation
    """

    def send_order_notification(self, order: Order) -> None:
        """
        Send email notification about new order

        Args:
            order: Order to send notification about
        """
        subject = f"New Order #{order.id}"
        message = render_to_string("order_notification.txt", {"order": order})
        html_message = render_to_string("order_notification.html", {"order": order})

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=html_message,
        )
