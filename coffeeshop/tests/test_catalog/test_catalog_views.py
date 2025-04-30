from __future__ import annotations

import pytest
from catalog.filters import ProductFilter
from catalog.models import Product, ProductCategory
from catalog.templatetags.catalog_tags import show_categories
from catalog.utils import DataMixin
from catalog.views import CoffeShopCategory, CoffeShopHome, ShowItem
from django.db.models import QuerySet
from django.test import Client
from django.urls import reverse

# UNIT tests


def test_coffe_shop_home_view_get_queryset() -> None:
    """Test CoffeShopHome view's get_queryset method.

    Verifies that the queryset is properly configured for Product model
    and is ordered.
    """
    view = CoffeShopHome()
    queryset = view.get_queryset()
    assert queryset.model == Product
    assert queryset.ordered


def test_coffe_shop_category_view_get_queryset(
    category_object_tea: ProductCategory, product_object_tea: Product
) -> None:
    """Test CoffeShopCategory view's get_queryset method.

    Args:
        category_object_tea: Test category object
        product_object_tea: Test product object

    Verifies that the queryset returns correct products for given category.
    """
    view = CoffeShopCategory()
    view.kwargs = {"category_slug": "tea"}
    queryset = view.get_queryset()
    assert queryset.count() == 1
    assert queryset.first().category == category_object_tea


def test_show_item_view_get_context_data(product_object_tea: Product) -> None:
    """Test ShowItem view's get_context_data method.

    Args:
        product_object_tea: Test product object

    Verifies that context contains correct title and product data.
    """
    view = ShowItem()
    view.object = product_object_tea
    context = view.get_context_data()
    assert context["title"] == f"{product_object_tea.category} - {product_object_tea.name}"


# INTEGRATION Tests


def test_home_view(client: Client, multiple_products: list[Product]) -> None:
    """Test home view functionality.

    Args:
        client: Django test client
        multiple_products: List of test product objects

    Verifies that home view returns correct template, context and pagination.
    """
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    assert "catalog.html" in [t.name for t in response.templates]
    assert "cof_products" in response.context
    assert len(response.context["cof_products"]) == 2  # main page pagination
    assert response.context["title"] == "Catalog"
    assert "filter" in response.context  # check filter exists in context


def test_catalog_view(client: Client, multiple_products: list[Product]) -> None:
    """Test catalog view functionality.

    Args:
        client: Django test client
        multiple_products: List of test product objects

    Verifies that catalog view returns correct template and paginated products.
    """
    url = reverse("catalog")
    response = client.get(url)

    assert response.status_code == 200
    assert "catalog.html" in [t.name for t in response.templates]
    assert "cof_products" in response.context
    assert len(response.context["cof_products"]) == 2


def test_category_view(client: Client, category_object_tea: ProductCategory, product_object_tea: Product) -> None:
    """Test category view functionality.

    Args:
        client: Django test client
        category_object_tea: Test category object
        product_object_tea: Test product object

    Verifies that category view returns correct template and filtered products.
    """
    url = reverse("category", kwargs={"category_slug": "tea"})
    response = client.get(url)

    assert response.status_code == 200
    assert "catalog.html" in [t.name for t in response.templates]
    assert "cof_products" in response.context
    assert response.context["title"] == "Product category - TEA"
    assert all(p.category == category_object_tea for p in response.context["cof_products"])


def test_item_view(client: Client, product_object_tea: Product) -> None:
    """Test item detail view functionality.

    Args:
        client: Django test client
        product_object_tea: Test product object

    Verifies that item view returns correct template and product details.
    """
    url = reverse("item", kwargs={"slug": "test-product-1"})
    response = client.get(url)

    assert response.status_code == 200
    assert "item.html" in [t.name for t in response.templates]
    assert "item" in response.context
    assert response.context["item"] == product_object_tea
    assert response.context["title"] == f"{product_object_tea.category} - {product_object_tea.name}"


def test_no_item(client: Client) -> None:
    """Test item view with non-existent product.

    Args:
        client: Django test client

    Verifies that view returns 404 for non-existent product.
    """
    url = reverse("item", kwargs={"slug": "nonexistent"})
    response = client.get(url)
    assert response.status_code == 404


def test_nonexistent_category(client: Client) -> None:
    """Test category view with non-existent category.

    Args:
        client: Django test client

    Verifies that view returns empty product list for non-existent category.
    """
    url = reverse("category", kwargs={"category_slug": "nonexistent"})
    response = client.get(url)
    assert response.status_code == 200  # we must have empty page
    assert "catalog.html" in [t.name for t in response.templates]
    assert "cof_products" in response.context
    assert len(response.context["cof_products"]) == 0  # because we have empty product list
    assert response.context["title"] == "Category not found"


def test_filter_products(client: Client, multiple_products: list[Product], sort_object: ProductCategory) -> None:
    """Test product filtering functionality.

    Args:
        client: Django test client
        multiple_products: List of test product objects
        sort_object: Test sort category object

    Verifies that products are correctly filtered by sort def mock_all(category.
    """
    url = reverse("catalog")
    response = client.get(url, {"sort": sort_object.id})  # sort filtration

    assert response.status_code == 200
    assert "cof_products" in response.context
    assert all(p.sort == sort_object for p in response.context["cof_products"])


def test_pagination(client: Client, multiple_products: list[Product]) -> None:
    """Test pagination functionality.

    Args:
        client: Django test client
        multiple_products: List of test product objects

    Verifies that pagination works correctly for default and second page.
    """
    url = reverse("catalog")
    response = client.get(url)

    # default page
    assert response.status_code == 200
    assert "cof_products" in response.context
    assert len(response.context["cof_products"]) == 2

    # second page
    response = client.get(url, {"page": 2})
    assert response.status_code == 200
    assert len(response.context["cof_products"]) == 2


# MOCK tests


def test_home_view_db_interaction(
    monkeypatch: pytest.MonkeyPatch, client: Client, product_with_all_relations: Product
) -> None:
    """Test home view database interaction using mocks.

    Args:
        monkeypatch: pytest monkeypatch fixture
        client: Django test client
        product_with_all_relations: Test product object with all relations
    """

    def mock_all() -> QuerySet[Product] :
        return Product.objects.filter(pk=product_with_all_relations.pk)

    monkeypatch.setattr(Product.objects, "all", mock_all)

    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert response.context["title"] == "Catalog"


def test_category_view_db_interaction(monkeypatch: pytest.MonkeyPatch, client: Client) -> None:
    """Test category view database interaction using mocks.

        Args:
        monkeypatch: pytest monkeypatch fixture
        client: Django test client
    """
    def mock_filter(*args: str, **kwargs: dict[str, str]) -> QuerySet[Product]:
        return []

    monkeypatch.setattr(Product.objects, "filter", mock_filter)

    response = client.get(reverse("category", kwargs={"category_slug": "coffee"}))
    assert response.status_code == 200
    assert response.context["title"] == "Category not found"


def test_show_item_view_db_interaction(monkeypatch: pytest.MonkeyPatch, client: Client) -> None:
    """Test item view database interaction using mocks.

        Args:
        monkeypatch: pytest monkeypatch fixture
        client: Django test client
    """
    def mock_get(*args: str, **kwargs: dict[str, str]) -> Product:
        raise Product.DoesNotExist()

    monkeypatch.setattr(Product.objects, "get", mock_get)

    response = client.get(reverse("item", kwargs={"slug": "test-coffee"}))
    assert response.status_code == 404
