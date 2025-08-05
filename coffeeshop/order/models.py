"""
Models for orders and order items in the shop.
"""

from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Order(models.Model):
    """
    Model representing a customer order.
    Links to user, delivery address, phone, total amount, creation date, payment status, and applied promo.
    """

    objects = models.Manager()
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    delivery_address: str = models.TextField(verbose_name="Delivery Address")
    phone: str = models.CharField(max_length=20, verbose_name="Phone")
    cart_price: Decimal = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Cart Total", null=False
    )
    applied_promo_name: str = models.CharField(max_length=255, null=True, blank=True, verbose_name="Applied promo")
    applied_promo_status: bool = models.BooleanField(default=False, verbose_name="Applied promo status Y/N")
    discount_sum: Decimal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Discount SUM")
    total_price: Decimal = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Total Amount", null=False
    )
    time_created: str = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")
    is_paid: bool = models.BooleanField(default=False, verbose_name="Paid")

    class Meta:
        ordering = ["-time_created"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self) -> str:
        """
        String representation of the order.
        Returns:
            str: String with order id and user email.
        """
        return f"Order #{self.id} from {self.user.email}"

    def get_total_items(self) -> int:
        """
        Returns total number of items in the order.
        Returns:
            int: Total quantity of all items.
        """
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """
    Model representing an item in an order.
    Links to order, product data (saved at order time), quantity, and price.
    """

    objects = models.Manager()
    order: Order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE, verbose_name="Order")
    product_id: int = models.PositiveIntegerField(verbose_name="Product ID")
    product_name: str = models.CharField(max_length=255, verbose_name="Product Name")
    quantity: int = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Quantity")
    price: Decimal = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Price"
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self) -> str:
        """
        String representation of the order item.
        Returns:
            str: String with quantity, product name, and price.
        """
        return f"{self.quantity} x {self.product_name} ({self.price} ₽)"
