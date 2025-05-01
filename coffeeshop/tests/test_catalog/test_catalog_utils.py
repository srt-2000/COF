from __future__ import annotations

import pytest
from catalog.models import Product, ProductCategory
from catalog.utils import DataMixin
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestDataMixin:
    """Test suite for DataMixin pagination functionality."""

    def test_pagination_default_page(self, client: Client, multiple_products: list[Product]) -> None:
        """Test pagination on the first page with default settings.

        Args:
            client: Django test client
            multiple_products: List of test product objects
        """
        url = reverse("catalog")
        response = client.get(url)

        assert response.status_code == 200
        assert "cof_products" in response.context
        assert len(response.context["cof_products"]) == 2  # paginate_by = 2
        assert "page_obj" in response.context
        assert response.context["page_obj"].number == 1
        assert response.context["page_obj"].has_next()
        assert not response.context["page_obj"].has_previous()

    def test_pagination_second_page(self, client: Client, multiple_products: list[Product]) -> None:
        """Test pagination on the second page.

        Args:
            client: Django test client
            multiple_products: List of test product objects
        """
        url = reverse("catalog")
        response = client.get(url, {"page": 2})

        assert response.status_code == 200
        assert "cof_products" in response.context
        assert len(response.context["cof_products"]) == 2
        assert "page_obj" in response.context
        assert response.context["page_obj"].number == 2
        assert response.context["page_obj"].has_next()
        assert response.context["page_obj"].has_previous()

    def test_pagination_last_page(self, client: Client, multiple_products: list[Product]) -> None:
        """Test pagination on the last page.

        Args:
            client: Django test client
            multiple_products: List of test product objects
        """
        url = reverse("catalog")
        response = client.get(url, {"page": 5})

        assert response.status_code == 200
        assert "cof_products" in response.context
        assert len(response.context["cof_products"]) == 1  # we have 1 product object on the last page
        assert "page_obj" in response.context
        assert response.context["page_obj"].number == 5
        assert not response.context["page_obj"].has_next()
        assert response.context["page_obj"].has_previous()

    def test_pagination_invalid_page(self, client: Client, multiple_products: list[Product]) -> None:
        """Test pagination with invalid page number.

        Args:
            client: Django test client
            multiple_products: List of test product objects
        """
        url = reverse("catalog")
        response = client.get(url, {"page": 999})

        assert response.status_code == 404

    def test_pagination_empty_page(self, client: Client) -> None:
        """Test pagination with empty product list.

        Args:
            client: Django test client
        """
        url = reverse("catalog")
        response = client.get(url)

        assert response.status_code == 200
        assert "cof_products" in response.context
        assert len(response.context["cof_products"]) == 0
        assert "page_obj" in response.context
        assert response.context["page_obj"].number == 1
        assert not response.context["page_obj"].has_next()
        assert not response.context["page_obj"].has_previous()

    def test_pagination_category_view(
        self, client: Client, category_object_tea: ProductCategory, multiple_products: list[Product]
    ) -> None:
        """Test pagination in category view.

        Args:
            client: Django test client
            category_object_tea: Test category object
            multiple_products: List of test product objects
        """
        url = reverse("category", kwargs={"category_slug": "tea"})
        response = client.get(url)

        assert response.status_code == 200
        assert "cof_products" in response.context
        assert len(response.context["cof_products"]) == 2
        assert "page_obj" in response.context
        assert response.context["page_obj"].number == 1
        assert response.context["page_obj"].has_next()
        assert not response.context["page_obj"].has_previous()

    def test_pagination_with_filter(
        self, client: Client, multiple_products: list[Product], sort_object: ProductCategory
    ) -> None:
        """Test pagination with filtered products.

        Args:
            client: Django test client
            multiple_products: List of test product objects
            sort_object: Test sort category object
        """
        # update the same sort field for every object
        for product in multiple_products:
            product.sort = sort_object
            product.save()

        url = reverse("catalog")
        response = client.get(url, {"sort": sort_object.id})

        assert response.status_code == 200
        assert "cof_products" in response.context
        assert len(response.context["cof_products"]) == 2
        assert "page_obj" in response.context
        assert response.context["page_obj"].number == 1
        assert all(p.sort == sort_object for p in response.context["cof_products"])
