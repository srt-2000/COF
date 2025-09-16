"""Tests for the Cart class.

This module contains tests for the Cart class functionality including:
- Unit tests for basic cart operations
- Integration tests for cart interactions
- Mock tests for storage and service dependencies
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from cart.cart import Cart


class TestCartUnit:
    """Unit tests for Cart class."""

    def test_init(self, mock_storage, mock_product_service) -> None:
        """Test cart initialization.

        Args:
            mock_storage: Mocked storage instance
            mock_product_service: Mocked product service instance
        """
        cart = Cart(storage=mock_storage, product_service=mock_product_service)
        assert cart._storage == mock_storage
        assert cart._product_service == mock_product_service
        mock_storage.load.assert_called_once()

    @pytest.mark.parametrize(
        "product_id,quantity,override_quantity,expected_quantity",
        [
            (1, 1, False, 1),  # Add new item
            (1, 2, False, 2),  # Add to existing item
            (1, 5, True, 5),  # Override quantity
        ],
    )
    def test_add(
        self,
        cart: Cart,
        mock_storage,
        product_id: int,
        quantity: int,
        override_quantity: bool,
        expected_quantity: int,
    ) -> None:
        """Test adding items to cart.

        Args:
            cart: Cart instance
            mock_storage: Mocked storage instance
            product_id: ID of the product to add
            quantity: Quantity to add
            override_quantity: Whether to override existing quantity
            expected_quantity: Expected quantity after addition
        """
        cart.add(product_id, quantity, override_quantity)
        assert cart._cart[str(product_id)]["quantity"] == expected_quantity
        mock_storage.save.assert_called()

    def test_remove(self, cart: Cart, mock_storage) -> None:
        """Test removing items from cart.

        Args:
            cart: Cart instance
            mock_storage: Mocked storage instance
        """
        cart.add(1, 1)
        cart.remove(1)
        assert str(1) not in cart._cart
        mock_storage.save.assert_called()

    def test_clear(self, cart: Cart, mock_storage) -> None:
        """Test clearing cart.

        Args:
            cart: Cart instance
            mock_storage: Mocked storage instance
        """
        cart.add(1, 1)
        cart.clear()
        assert cart._cart == {}
        mock_storage.clear.assert_called_once()

    def test_len(self, cart: Cart) -> None:
        """Test cart length calculation.

        Args:
            cart: Cart instance
        """
        cart.add(1, 2)
        cart.add(2, 3)
        assert len(cart) == 5

    def test_get_total_price(self, cart: Cart) -> None:
        """Test total price calculation.

        Args:
            cart: Cart instance
        """
        cart.add(1, 2)
        cart._cart["1"] = {"quantity": 2, "price": Decimal("100.00")}
        assert cart.get_total_price() == Decimal("200.00")


class TestCartIntegration:
    """Integration tests for Cart class."""

    def test_iteration(
        self, cart: Cart, mock_product_service, sample_products: dict[int, dict[str, str | Decimal]]
    ) -> None:
        """Test cart iteration.

        Args:
            cart: Cart instance
            mock_product_service: Mocked product service instance
            sample_products: Sample product data
        """
        mock_product_service.get_products.return_value = sample_products
        cart.add(1, 2)
        cart.add(2, 1)
        cart._cart["1"]["price"] = Decimal("100.00")
        cart._cart["2"]["price"] = Decimal("200.00")

        items = list(cart)
        assert len(items) == 2
        mock_product_service.get_products.assert_called_once_with([1, 2])
        assert mock_product_service.prepare_item.call_count == 2

    def test_get_item(
        self, cart: Cart, mock_product_service, sample_products: dict[int, dict[str, str | Decimal]]
    ) -> None:
        """Test getting item from cart.

        Args:
            cart: Cart instance
            mock_product_service: Mocked product service instance
            sample_products: Sample product data
        """
        mock_product_service.get_products.return_value = sample_products
        mock_product_service.prepare_item.return_value = {
            "product": sample_products[1],
            "quantity": 2,
            "price": sample_products[1]["price"],
            "total_price": sample_products[1]["price"] * 2,
        }

        cart.add(1, 2)
        item = cart.get_item(1)

        assert item is not None
        assert item["product"]["id"] == 1
        assert item["quantity"] == 2
        assert item["price"] == Decimal("100.00")
        assert item["total_price"] == Decimal("200.00")

    def test_get_nonexistent_item(self, cart: Cart, mock_product_service) -> None:
        """Test getting nonexistent item.

        Args:
            cart: Cart instance
            mock_product_service: Mocked product service instance
        """
        mock_product_service.get_products.return_value = {}
        assert cart.get_item(999) is None


class TestCartMock:
    """Tests using mock objects."""

    def test_add_with_mock_storage(self, mock_storage, mocker) -> None:
        """Test add with mocked storage.

        Args:
            mock_storage: Mocked storage instance
            mocker: Pytest mocker fixture
        """
        cart = Cart(storage=mock_storage, product_service=mocker.Mock())
        cart.add(1, 2)
        mock_storage.save.assert_called_once()

    def test_remove_with_mock_storage(self, mock_storage, mocker) -> None:
        """Test remove with mocked storage.

        Args:
            mock_storage: Mocked storage instance
            mocker: Pytest mocker fixture
        """
        cart = Cart(storage=mock_storage, product_service=mocker.Mock())
        cart.add(1, 1)
        cart.remove(1)
        mock_storage.save.assert_called()

    def test_clear_with_mock_storage(self, mock_storage, mocker) -> None:
        """Test clear with mocked storage.

        Args:
            mock_storage: Mocked storage instance
            mocker: Pytest mocker fixture
        """
        cart = Cart(storage=mock_storage, product_service=mocker.Mock())
        cart.clear()
        mock_storage.clear.assert_called_once()

    def test_iteration_with_mock_service(self, mock_product_service, mocker) -> None:
        """Test iteration with mocked service.

        Args:
            mock_product_service: Mocked product service instance
            mocker: Pytest mocker fixture
        """
        test_product = {"id": 1, "name": "Test Product", "price": Decimal("100.00")}
        mock_product_service.get_products.return_value = {1: test_product}
        mock_product_service.prepare_item.return_value = {
            "product": test_product,
            "quantity": 1,
            "price": test_product["price"],
            "total_price": test_product["price"],
        }

        mock_storage = mocker.Mock()
        mock_storage.load.return_value = {}

        cart = Cart(storage=mock_storage, product_service=mock_product_service)
        cart.add(1, 1)
        cart._cart["1"]["price"] = test_product["price"]

        mock_storage.save.assert_called()
        saved_cart = mock_storage.save.call_args[0][0]
        assert "1" in saved_cart
        assert saved_cart["1"]["quantity"] == 1
        assert saved_cart["1"]["price"] == test_product["price"]

        items = list(cart)

        assert len(items) == 1
        mock_product_service.get_products.assert_called_once_with([1])
        assert mock_product_service.prepare_item.called

        item = items[0]
        assert item["product"]["id"] == 1 or item["product"].get("id", None) == 1
        assert item["quantity"] == 1
        assert item["price"] == Decimal("100.00")
        assert item["total_price"] == Decimal("100.00")
