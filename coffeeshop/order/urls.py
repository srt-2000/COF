from __future__ import annotations

from django.urls import path
from order.views import OrderCreateView, OrderDetailView


urlpatterns = [
    path("create/", OrderCreateView.as_view(), name="order_create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
]
