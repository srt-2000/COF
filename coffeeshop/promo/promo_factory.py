"""
Factory for creating promo logic objects based on promo type.
"""

from __future__ import annotations

from promo.models import Promo, PromoTypeEnum
from promo.promo import FreeProductPromo, TotalCartPromo


class PromoFactory:
    """
    Factory for promo logic selection.
    """

    @staticmethod
    def get_promo(promo_id: int) -> TotalCartPromo | FreeProductPromo | None:
        """
        Get the promo logic object for the given promo id.
        """
        promo: Promo = Promo.objects.get(id=promo_id)
        if promo.promo_type == PromoTypeEnum.TOTAL_CART.value:
            return TotalCartPromo(promo)
        elif promo.promo_type == PromoTypeEnum.FREE_PRODUCT.value:
            return FreeProductPromo(promo)
        else:
            return None
