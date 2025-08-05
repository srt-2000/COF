"""
Factory for creating cart instances.
"""

from __future__ import annotations

from django.contrib.sessions.backends.base import SessionBase

from cart.cart import Cart
from cart.product_service import CartProductService
from cart.storage import SessionCartStorage


class CartFactory:
    """
    Factory class for creating cart instances.
    """

    @staticmethod
    def create_from_session(session: SessionBase) -> Cart:
        """
        Create a cart instance.

        Args:
            session (SessionBase): The SessionBase object.

        Returns:
            Cart: A new cart instance.
            :param session:
        """
        storage: SessionCartStorage = SessionCartStorage(session)
        product_service: CartProductService = CartProductService()
        return Cart(storage, product_service)
