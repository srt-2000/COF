from __future__ import annotations

import builtins

from django_filters import FilterSet, filters

from catalog.models import Product, ProductManufacture, ProductRegion, ProductSort, ProductType


class ProductFilter(FilterSet):
    """
    Filter set for Product model that provides filtering capabilities by sort, type, region, and manufacture.

    This filter set allows users to filter products based on various attributes:
    - sort: Filter by coffee/tea sort
    - type: Filter by product type
    - region: Filter by region of origin
    - manufacture: Filter by manufacturer
    """

    sort: builtins.type[filters.ModelChoiceFilter] = filters.ModelChoiceFilter(
        queryset=ProductSort.objects.filter(sorts__sort__isnull=False).distinct(),
        empty_label="Sort not chosen",
        label="Sort",
    )

    product_type: builtins.type[filters.ModelChoiceFilter] = filters.ModelChoiceFilter(
        queryset=ProductType.objects.filter(types__product_type__isnull=False).distinct(),
        empty_label="Type not chosen",
        label="Type",
    )

    region: builtins.type[filters.ModelChoiceFilter] = filters.ModelChoiceFilter(
        queryset=ProductRegion.objects.filter(regions__region__isnull=False).distinct(),
        empty_label="Region not chosen",
        label="Region",
    )

    manufacture: builtins.type[filters.ModelChoiceFilter] = filters.ModelChoiceFilter(
        queryset=ProductManufacture.objects.filter(manufacturers__manufacture__isnull=False).distinct(),
        empty_label="Manufacture not chosen",
        label="Manufacture",
    )

    class Meta:
        model = Product
        fields = ["sort", "product_type", "region", "manufacture"]
