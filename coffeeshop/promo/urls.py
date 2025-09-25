"""
URL configuration for the cart application.

This module defines the URL patterns for the promo application, including
promo apply views.
"""

from __future__ import annotations

from django.urls import path
from promo.views import PromoApplyView, PromoListView

urlpatterns = [
    path("", PromoListView.as_view(), name="promo_list"),
    path("apply/", PromoApplyView.as_view(), name="promo_apply"),
]
