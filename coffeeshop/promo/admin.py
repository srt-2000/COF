from __future__ import annotations

from django.contrib import admin
from promo.models import Promo


@admin.register(Promo)
class CartTotalDiscountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "description",
        "date_start",
        "date_end",
    )
    list_display_links = ("name",)
    list_filter = [
        "name",
        "is_active",
    ]
    filter_horizontal = ("promo_products",)
