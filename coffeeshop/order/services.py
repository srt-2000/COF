"""
Order service layer: business logic, repository, and notification implementations.
"""

from __future__ import annotations

from typing import cast

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string

from cart.interfaces import ICart
from order.domains import OrderCreateData, OrderData, OrderItemData
from order.interfaces import IOrderNotification, IOrderRepository, IOrderService
from order.models import Order, OrderItem
from promo.utils import get_applied_promo_context


class OrderService(IOrderService):
    """
    Service for order operations: coordinates order creation process, independent of specific storage and notification implementations.
    """

    def __init__(self, repository: IOrderRepository, notifier: IOrderNotification) -> None:
        """
        Initialize the order service with repository and notifier.
        Args:
            repository (IOrderRepository): The repository for order storage.
            notifier (IOrderNotification): The notification service.
        """
        self.repository: IOrderRepository = repository
        self.notifier: IOrderNotification = notifier

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
            user (User): User creating the order.
            cart (ICart): Shopping cart with items.
            form_data (dict[str, str]): Form data with delivery information.
            applied_promo_id (int | None): ID of applied promo code.
        Returns:
            OrderData: The created order data including DB-generated fields.
        """

        items: list[OrderItemData] = [
            cast(
                OrderItemData,
                {
                    "product_id": item["product"].id,
                    "product_name": item["product"].name,
                    "quantity": item["quantity"],
                    "price": item["price"],
                },
            )
            for item in cart
        ]

        promo_context = get_applied_promo_context(cart, applied_promo_id)

        order_data: OrderCreateData = {
            "user": user,
            "user_email": user.email,
            "delivery_address": form_data["delivery_address"],
            "phone": form_data["phone"],
            "cart_price": cart.get_cart_total(),
            "applied_promo_name": promo_context["applied_promo_name"],
            "applied_promo_status": promo_context["applied_promo_status"],
            "discount_sum": cart.get_discount_sum(applied_promo_id),
            "total_price": cart.get_total_price(applied_promo_id),
            "items": items,

        }

        return self.repository.save_order(order_data)


class DatabaseOrderRepository(IOrderRepository):
    """
    Repository for database operations: encapsulates order storage logic, works with Django models.
    """

    def save_order(self, order_data: OrderCreateData) -> OrderData:
        """
        Save order to database.
        Args:
            order_data (OrderCreateData): Order data to save.
        Returns:
            OrderData: The saved order data including DB-generated fields.
        """
        with transaction.atomic():
            order: Order = Order.objects.create(
                user=order_data["user"],
                delivery_address=order_data["delivery_address"],
                phone=order_data["phone"],
                cart_price=order_data["cart_price"],
                applied_promo_name=order_data["applied_promo_name"],
                applied_promo_status=order_data["applied_promo_status"],
                discount_sum=order_data["discount_sum"],
                total_price=order_data["total_price"],

            )

            order_items: list[dict[str, object]] = [
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
                "cart_price": order.cart_price,
                "applied_promo_name": order.applied_promo_name,
                "applied_promo_status": order.applied_promo_status,
                "discount_sum": order.discount_sum,
                "total_price": order.total_price,
                "time_created": order.time_created,
                "items": order_items,

            }


class EmailOrderNotification(IOrderNotification):
    """
    Email notification service: sends email to administrator about new order, uses templates for email generation.
    """

    def send_order_notification(self,
                                order_id: int,
                                ) -> None:
        """
        Send email notification about new order.
        Args:
            order (Order): Order to send notification about.
            :param order_id:
        """
        order = Order.objects.get(id=order_id)
        subject: str = f"New Order #{order.id}"
        message: str = render_to_string("order_notification.txt", {"order": order})
        html_message: str = render_to_string("order_notification.html", {"order": order})
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=html_message,
        )
