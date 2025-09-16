"""
Models for promo codes and promo types.
"""

from __future__ import annotations

from enum import IntEnum

from catalog.models import Product
from django.db import models


class PromoTypeEnum(IntEnum):
    """
    Enum for promo types.
    """

    TOTAL_CART = 1
    FREE_PRODUCT = 2


class Promo(models.Model):
    """
    Model representing a promo code.
    """

    name: str = models.CharField(max_length=250, null=False)
    promo_type = models.IntegerField(
        choices=[(choice.value, choice.name) for choice in PromoTypeEnum],
        null=False,
    )
    description: str = models.TextField()
    is_active: bool = models.BooleanField(default=False)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    promo_products = models.ManyToManyField(Product, related_name="free_product_promos")
    min_cart_total = models.DecimalField(max_digits=16, decimal_places=2, default=0.01)
    required_products_quantity: int = models.PositiveIntegerField(default=0)
    free_promo_products: int = models.PositiveIntegerField(default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)

    class Meta:
        ordering = ["is_active", "-date_start"]
        verbose_name = "Cart Promo"
        verbose_name_plural = "Cart Promos"

    def __str__(self) -> str:
        return self.name
