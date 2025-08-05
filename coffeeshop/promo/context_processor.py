"""
Context processor for promo status. Provides applied promo name and status to templates.
"""

from __future__ import annotations

from django.http import HttpRequest

from cart.factory import CartFactory
from promo.domains import PromoStatusContext
from promo.utils import get_applied_promo_context


def promo_status(request: HttpRequest) -> PromoStatusContext:
    """
    Context processor that provides information about the currently applied promo code.

    Args:
        request (HttpRequest): The current HTTP request.

    Returns:
        PromoStatusContext: Dictionary with promo status variables for the template context.
    """
    applied_promo_id: int | None = request.session.get("applied_promo_id")
    cart = CartFactory.create_from_session(request.session)

    return get_applied_promo_context(cart, applied_promo_id)
