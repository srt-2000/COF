from __future__ import annotations

from cart.interfaces import ICart
from promo.domains import PromoStatusContext
from promo.models import Promo


def get_applied_promo_context(cart: ICart, applied_promo_id: int | None) -> PromoStatusContext:
    """
    Separate function to get applied promo context (applied_promo_status and applied_promo_name).
    Args:
        applied_promo_id
        cart
    Returns:
        PromoStatusContext: Dictionary with promo status variables for the template context.
    """

    applied_promo_name: str | None = None
    applied_promo_status: bool = False

    if applied_promo_id:
        try:
            promo = Promo.objects.get(id=applied_promo_id)
            applied_promo_name = promo.name
            if cart.get_total_price(applied_promo_id) < cart.get_cart_total():
                applied_promo_status = True
        except Promo.DoesNotExist:
            applied_promo_name = None
            applied_promo_status = False

    return {
        "applied_promo_name": applied_promo_name,
        "applied_promo_status": applied_promo_status,
    }
