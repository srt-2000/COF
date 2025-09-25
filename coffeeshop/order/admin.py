from __future__ import annotations

from django.contrib import admin
from order.models import Order, OrderItem


@admin.register(Order)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "time_created", "is_paid", "total_price", "user", "delivery_address", "phone")
    list_display_links = ("id", "user")
    search_fields = ["user__username", "phone", "total_price", "delivery_address"]
    list_filter = ["user__username", "is_paid", "time_created", "phone", "delivery_address"]
