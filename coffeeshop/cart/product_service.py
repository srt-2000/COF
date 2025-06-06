"""
Service for product operations in the cart.

This module provides a service class for retrieving products and preparing cart items.
"""

from __future__ import annotations

from decimal import Decimal

from cart.interfaces import CartItemServiceTypedDict, ICartProductService
from catalog.models import Product


class CartProductService(ICartProductService):
    """
    Service class for product operations in the cart.
    """

    def __init__(self) -> None:
        pass

    def get_products(self, product_ids: list[int]) -> dict[int, Product]:
        """
        Retrieve products by their IDs.

        Args:
            product_ids (list[int]): List of product IDs.

        Returns:
            dict[int, Product]: A dictionary mapping product IDs to Product objects.
        """
        return {p.id: p for p in Product.objects.filter(id__in=product_ids)}

    def calculate_item_total(self, price: Decimal, quantity: int) -> Decimal:
        """
        Calculate the total price for a cart item.

        Args:
            price (Decimal): The price per unit.
            quantity (int): The quantity of the item.

        Returns:
            Decimal: The total price.
        """
        return price * quantity

    def prepare_item(self, product: Product, quantity: int) -> CartItemServiceTypedDict:
        """
        Prepare a cart item from a product and quantity.

        Args:
            product (Product): The product object.
            quantity (int): The quantity of the product.

        Returns:
            CartItemServiceTypedDict: A dictionary representing the cart item.
        """
        return {
            "product": product,
            "quantity": quantity,
            "price": product.price,
            "total_price": product.price * quantity,
        }
