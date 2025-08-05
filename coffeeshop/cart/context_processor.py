"""
Context processor for the shopping cart.
"""

from __future__ import annotations

from cart.domains import CartContext
from cart.factory import CartFactory
from django.http import HttpRequest



def cart(request: HttpRequest) -> CartContext:
    """
    Add the cart instance to the template context.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        CartContext: A dictionary containing the cart instance.
    """
    cart_instance = CartFactory.create_from_session(request.session)
    promo_id: int | None = request.session.get("applied_promo_id")
    
    return {
        "cart": cart_instance,
        "total_cart_price": cart_instance.get_cart_total(),
        "discount_sum": cart_instance.get_discount_sum(promo_id),
        "total_price": cart_instance.get_total_price(promo_id),
        }
