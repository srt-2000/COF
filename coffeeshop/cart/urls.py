"""
URL configuration for the cart application.

This module defines the URL patterns for the cart application, including
cart detail, add, remove, clear, and update views.
"""
from __future__ import annotations

from typing import TypedDict

from django.urls import path

from cart.views import CartAddView, CartClearView, CartDetailView, CartRemoveView, CartUpdateView


class URLPattern(TypedDict):
    pattern: str
    view: object
    name: str


urlpatterns: list[URLPattern] = [
    path("", CartDetailView.as_view(), name="cart_detail"),
    path("add/<int:product_id>/", CartAddView.as_view(), name="cart_add"),
    path("remove/<int:product_id>/", CartRemoveView.as_view(), name="cart_remove"),
    path("clear/", CartClearView.as_view(), name="cart_clear"),
    path("update/<int:product_id>/", CartUpdateView.as_view(), name="cart_update"),
]
