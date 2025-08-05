"""
Views for the catalog application, including product listing, category filtering, and product detail display.
"""

from __future__ import annotations

from typing import cast

from catalog.filters import ProductFilter
from catalog.models import Product
from catalog.utils import DataMixin
from django.db.models import QuerySet
from django.views.generic import DetailView, ListView
from django_filters.views import FilterView


class CoffeShopHome(DataMixin, FilterView):
    """
    View for displaying the main catalog page with filtering capabilities.
    """

    model: type[Product] = Product
    filterset_class: type[ProductFilter] = ProductFilter
    template_name: str = "catalog.html"
    context_object_name: str = "cof_products"
    extra_context: dict[str, str] = {"title": "Catalog"}


class CoffeShopCategory(DataMixin, ListView):
    """
    View for displaying products filtered by category.
    """

    model: type[Product] = Product
    template_name: str = "catalog.html"
    context_object_name: str = "cof_products"

    def get_queryset(self) -> QuerySet[Product]:
        """
        Returns products filtered by category slug.
        Returns:
            QuerySet[Product]: Queryset of products in the given category.
        """
        return Product.objects.filter(category__slug=self.kwargs["category_slug"])

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """
        Adds category title to the context.
        Args:
            **kwargs: Additional context arguments.
        Returns:
            dict[str, object]: The context dictionary with title.
        """
        context: dict[str, object] = super().get_context_data(**kwargs)
        cof_products = cast(list[Product], context.get("cof_products", []))
        if cof_products:
            category_object = cof_products[0].category
            context["title"] = f"Product category - {category_object.name}"
        else:
            context["title"] = "Category not found"
        return context


class ShowItem(DetailView):
    """
    View for displaying individual product details.
    """

    model: type[Product] = Product
    template_name: str = "item.html"
    context_object_name: str = "item"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """
        Adds product title to the context.
        Args:
            **kwargs: Additional context arguments.
        Returns:
            dict[str, object]: The context dictionary with title.
        """
        context: dict[str, object] = super().get_context_data(**kwargs)
        context["title"] = f"{self.object.category} - {self.object.name}"
        return context
