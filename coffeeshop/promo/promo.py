"""
Promo logic implementations for different promo types.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from cart.interfaces import ICart
from django.utils import timezone
from promo.interfaces import IPromo
from promo.models import Promo


class BasePromo(IPromo):
    """
    Base class for promo logic. Implements common validation logic for all promo types.
    """

    def __init__(self, promo: Promo) -> None:
        """
        Initialize promo logic with a specific Promo instance.
        Args:
            promo (Promo): The promo model instance to use for logic.
        """
        self.promo: Promo = promo

    def is_valid_period(self) -> bool:
        """
        Check if the promo is active and within the valid period.
        Returns:
            bool: True if promo is active and within period, False otherwise.
        """
        now = timezone.now()
        return self.promo.is_active and self.promo.date_start < now < self.promo.date_end

    def is_valid_id(self, session_promo_id: int) -> bool:
        """
        Check if the session promo id matches the promo id.
        Args:
            session_promo_id (int): Promo id from session.
        Returns:
            bool: True if ids match, False otherwise.
        """
        return session_promo_id == self.promo.id

    def valid_promo(self, session_promo_id: int) -> bool:
        """
        Check if the promo is valid for the session.
        Args:
            session_promo_id (int): Promo id from session.
        Returns:
            bool: True if promo is valid, False otherwise.
        """
        return self.is_valid_period() and self.is_valid_id(session_promo_id)

    def valid_cart(self, cart: ICart) -> bool:
        pass

    def apply_promo(self, current_total: Decimal, session_promo_id: int, cart: ICart) -> Decimal:
        pass


class TotalCartPromo(BasePromo):
    """
    Promo logic for total cart discount.
    """

    def valid_cart(self, cart: ICart) -> bool:
        """
        Check if the cart is valid for the total cart promo.
        Args:
            cart (ICart): Cart object implementing get_cart_total().
        Returns:
            bool: True if cart total is above minimum, False otherwise.
        """
        return cart.get_cart_total() >= self.promo.min_cart_total

    def apply_promo(self, current_total: Decimal, session_promo_id: int, cart: ICart) -> Decimal:
        """
        Apply the total cart promo if valid.
        Args:
            current_total (Decimal): Current cart total.
            session_promo_id (int): Promo id from session.
            cart (ICart): Cart object implementing get_cart_total().
        Returns:
            Decimal: New total after applying promo, or original total if not valid.
        """
        if self.valid_promo(session_promo_id) and self.valid_cart(cart):
            total = current_total * Decimal(1 - (self.promo.discount / 100))
            return Decimal(total).quantize(Decimal("1.00"), ROUND_HALF_UP)
        return current_total


class FreeProductPromo(BasePromo):
    """
    Promo logic for free product promo.
    """

    def valid_cart(self, cart: ICart) -> bool:
        """
        Check if the cart is valid for the free product promo.
        Args:
            cart (ICart): Cart object implementing get_cart_total() and iterable of items.
        Returns:
            bool: True if cart meets promo requirements, False otherwise.
        """
        promo_product_ids: set[int] = {p.id for p in self.promo.promo_products.all()}
        cart_product_ids: set[int] = {item["product"].id for item in cart}
        cart_promo_product_qnt: int = len(cart_product_ids.intersection(promo_product_ids))
        return (
            self.promo.min_cart_total <= cart.get_cart_total()
            and self.promo.required_products_quantity <= cart_promo_product_qnt
        )

    def apply_promo(self, current_total: Decimal, session_promo_id: int, cart: ICart) -> Decimal:
        """
        Apply the free product promo if valid.
        Args:
            current_total (Decimal): Current cart total.
            session_promo_id (int): Promo id from session.
            cart (ICart): Cart object implementing get_cart_total() and iterable of items.
        Returns:
            Decimal: New total after applying promo, or original total if not valid.
        """
        if self.valid_promo(session_promo_id) and self.valid_cart(cart):
            min_promo_product_price: Decimal = Decimal("Infinity")
            promo_product_ids: set[int] = {p.id for p in self.promo.promo_products.all()}
            for item in cart:
                if item["product"].id in promo_product_ids:
                    min_promo_product_price = min(min_promo_product_price, Decimal(str(item["price"])))
            total: Decimal = current_total - Decimal(min_promo_product_price)
            return Decimal(total).quantize(Decimal("1.00"), ROUND_HALF_UP)
        return current_total
