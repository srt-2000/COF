"""Tests for cart product service.

This module contains tests for the CartProductService class including:
- Tests for product retrieval and preparation
- Integration tests with real database
- Mock tests for service functionality
"""
from __future__ import annotations

from decimal import Decimal
from typing import TypedDict
from unittest.mock import MagicMock, patch

import pytest
from cart.product_service import CartProductService
from cart.interfaces import CartItemServiceTypedDict
from catalog.models import Product


class TestCartProductService:
    """Tests for CartProductService class."""

    def test_get_products(
        self,
        mock_product_model: MagicMock,
        mock_product: MagicMock,
    ) -> None:
        """Test retrieving products by IDs.

        Args:
            mock_product_model: Mocked product model
            mock_product: Mocked product instance
        """
        mock_product_model.objects.filter.return_value = [mock_product]
        service = CartProductService()

        result = service.get_products([1])

        mock_product_model.objects.filter.assert_called_once_with(id__in=[1])
        assert result == {1: mock_product}

    @pytest.mark.parametrize(
        "price,quantity,expected",
        [
            (Decimal("100.00"), 1, Decimal("100.00")),
            (Decimal("100.00"), 2, Decimal("200.00")),
            (Decimal("50.00"), 3, Decimal("150.00")),
            (Decimal("0.00"), 5, Decimal("0.00")),
        ],
    )
    def test_calculate_item_total(
        self,
        price: Decimal,
        quantity: int,
        expected: Decimal,
    ) -> None:
        """Test calculating total price for cart item.

        Args:
            price: Product price
            quantity: Product quantity
            expected: Expected total price
        """
        service = CartProductService()
        result = service.calculate_item_total(price, quantity)
        assert result == expected

    def test_prepare_item(
        self,
        mock_product: MagicMock,
    ) -> None:
        """Test preparing cart item from product.

        Args:
            mock_product: Mocked product instance
        """
        quantity = 2
        expected_total = mock_product.price * quantity
        service = CartProductService()

        result = service.prepare_item(mock_product, quantity)

        assert isinstance(result, dict)
        assert result["product"] == mock_product
        assert result["quantity"] == quantity
        assert result["price"] == mock_product.price
        assert result["total_price"] == expected_total


class TestCartProductServiceIntegration:
    """Integration tests for CartProductService."""

    def test_get_products_integration(
        self,
        product_object_tea: Product,
        product_object_coffee: Product,
    ) -> None:
        """Test retrieving products with real database.

        Args:
            product_object_tea: Tea product instance
            product_object_coffee: Coffee product instance
        """
        service = CartProductService()
        result = service.get_products(
            [
                product_object_tea.id,
                product_object_coffee.id,
            ]
        )

        assert len(result) == 2
        assert result[product_object_tea.id] == product_object_tea
        assert result[product_object_coffee.id] == product_object_coffee

    def test_prepare_item_integration(
        self,
        product_object_tea: Product,
    ) -> None:
        """Test preparing cart item with real product.

        Args:
            product_object_tea: Tea product instance
        """
        quantity = 2
        expected_total = product_object_tea.price * quantity
        service = CartProductService()

        result = service.prepare_item(product_object_tea, quantity)

        assert isinstance(result, dict)
        assert result["product"] == product_object_tea
        assert result["quantity"] == quantity
        assert result["price"] == product_object_tea.price
        assert result["total_price"] == expected_total


class TestCartProductServiceMock:
    """Tests using mock objects."""

    def test_get_products_with_mock_queryset(
        self,
        mock_product_model: MagicMock,
        mock_product_queryset: MagicMock,
        mock_product: MagicMock,
    ) -> None:
        """Test retrieving products with mocked queryset.

        Args:
            mock_product_model: Mocked product model
            mock_product_queryset: Mocked product queryset
            mock_product: Mocked product instance
        """
        mock_product_queryset.__iter__.return_value = [mock_product]
        mock_product_model.objects.filter.return_value = mock_product_queryset
        service = CartProductService()

        result = service.get_products([1])

        mock_product_model.objects.filter.assert_called_once_with(id__in=[1])
        mock_product_queryset.__iter__.assert_called_once()
        assert result == {1: mock_product}

    def test_prepare_item_with_mock_product(
        self,
        mock_product: MagicMock,
    ) -> None:
        """Test preparing cart item with mocked product.

        Args:
            mock_product: Mocked product instance
        """
        quantity = 2
        mock_product.price = Decimal("100.00")
        expected_total = mock_product.price * quantity
        service = CartProductService()

        result = service.prepare_item(mock_product, quantity)

        assert isinstance(result, dict)
        assert result["product"] == mock_product
        assert result["quantity"] == quantity
        assert result["price"] == mock_product.price
        assert result["total_price"] == expected_total
