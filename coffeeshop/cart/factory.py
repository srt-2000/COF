"""
Factory for creating cart instances.

This module provides a factory class for creating cart instances from HTTP requests.
"""
from __future__ import annotations

from django.http import HttpRequest

from cart.cart import Cart
from cart.product_service import CartProductService
from cart.storage import SessionCartStorage


class CartFactory:
    """
    Factory class for creating cart instances.
    """

    @staticmethod
    def create_from_request(request: HttpRequest) -> Cart:
        """
        Create a cart instance from an HTTP request.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Cart: A new cart instance.
        """
        storage = SessionCartStorage(request.session)
        product_service = CartProductService()
        return Cart(storage, product_service)
