"""
Service for product operations in the cart.
"""

from __future__ import annotations

from cart.domains import CartItemServiceData
from cart.interfaces import ICartProductService
from catalog.models import Product


class CartProductService(ICartProductService):
    """
    Service class for product operations in the cart.
    """

    def __init__(self) -> None:
        """Initialize the cart product service."""
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

    def calculate_item_total(self, price: float, quantity: int) -> float:
        """
        Calculate the total price for a cart item.
        Args:
            price (float): The price per unit.
            quantity (int): The quantity of the item.
        Returns:
            float: The total price.
        """
        return price * quantity

    def prepare_item(self, product: Product, quantity: int) -> CartItemServiceData:
        """
        Prepare a cart item from a product and quantity.
        Args:
            product (Product): The product object.
            quantity (int): The quantity of the product.
        Returns:
            CartItemServiceData: A dictionary representing the cart item.
        """
        return {
            "product": product,
            "quantity": quantity,
            "price": float(product.price),
            "total_price": float(product.price * quantity),
        }
