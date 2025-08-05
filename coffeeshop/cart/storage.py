"""
Session-based storage backend for the shopping cart.
"""

from __future__ import annotations

from cart.domains import CartData
from cart.interfaces import IStorage
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase


class SessionCartStorage(IStorage):
    """
    Session-based storage backend for the cart.
    """

    def __init__(self, session: SessionBase) -> None:
        """
        Initialize the storage with a session.
        Args:
            session (SessionBase): The Django session object.
        """
        self.session: SessionBase = session
        self._key: str = settings.CART_SESSION_ID

    def load(self) -> dict[str, CartData]:
        """
        Load cart data from the session.
        Returns:
            dict[str, CartData]: A dictionary mapping product IDs to cart data.
        """
        return self.session.get(self._key, {})

    def save(self, cart_data: dict[str, CartData]) -> None:
        """
        Save cart data to the session.
        Args:
            cart_data (dict[str, CartData]): The cart data to save.
        """
        self.session[self._key] = cart_data
        self.session.modified = True

    def clear(self) -> None:
        """
        Clear cart data from the session.
        """
        if self._key in self.session:
            del self.session[self._key]
            self.session.modified = True
