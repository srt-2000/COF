"""
TypedDict definitions for promo-related context data.
"""

from __future__ import annotations

from typing import TypedDict


class PromoStatusContext(TypedDict):
    """
    TypedDict for promo status context passed to templates.
    Fields:
        applied_promo_name (str | None): Name of the applied promo, or None if not applied.
        applied_promo_status (bool): True if promo was successfully applied, False otherwise.
    """

    applied_promo_name: str | None
    applied_promo_status: bool
