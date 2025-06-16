from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Order(models.Model):
    """
    Order model:
    - Links to user
    - Delivery address and phone
    - Total amount and creation date
    - Payment status
    """

    objects = models.Manager()
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    delivery_address = models.TextField(verbose_name="Delivery Address")
    phone = models.CharField(max_length=20, verbose_name="Phone")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Total Amount"
    )
    time_created = models.DateTimeField(auto_now_add=True, verbose_name="Creation Date")
    is_paid = models.BooleanField(default=False, verbose_name="Paid")

    class Meta:
        ordering = ["-time_created"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self) -> str:
        return f"Order #{self.id} from {self.user.email}"

    def get_total_items(self) -> int:
        """
        Returns total number of items in the order

        Returns:
            int: Total quantity of all items
        """
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """
    Order item model:
    - Links to order
    - Product data (saved at order time)
    - Quantity and price
    """

    objects = models.Manager()
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE, verbose_name="Order")
    product_id = models.PositiveIntegerField(verbose_name="Product ID")
    product_name = models.CharField(max_length=255, verbose_name="Product Name")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Quantity")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))], verbose_name="Price"
    )

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product_name} ({self.price} ₽)"
