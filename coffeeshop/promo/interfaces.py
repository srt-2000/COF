"""
Interfaces for promo logic and validation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from cart.interfaces import ICart


class IPromo(ABC):
    """
    Interface for promo logic and application.
    """

    @abstractmethod
    def valid_promo(self, session_promo_id: int) -> bool:
        """
        Check if the promo is valid for the given session promo id.
        """
        pass

    @abstractmethod
    def valid_cart(self, cart: ICart) -> bool:
        """
        Check if the cart is valid for the promo.
        """
        pass

    @abstractmethod
    def apply_promo(self, current_total: Decimal, session_promo_id: int, cart: ICart) -> Decimal:
        """
        Apply the promo to the current total if valid.
        """
        pass
