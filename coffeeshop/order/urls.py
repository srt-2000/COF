from __future__ import annotations

from collections.abc import Callable
from typing import TypedDict

from django.urls import path
from django.views.generic import View
from order.views import OrderCreateView, OrderDetailView


class URLPattern(TypedDict):
    """Typed dictionary for URL pattern configuration"""

    pattern: str
    view: Callable[..., View]
    name: str


urlpatterns: list[URLPattern] = [
    path("create/", OrderCreateView.as_view(), name="order_create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
]
