"""Tests for cart interfaces.

This module contains tests for cart interfaces including:
- Tests for CartItemTypedDict structure and field types
- Tests for ICart interface abstract methods
- Tests for mock cart implementation
- Integration tests for cart interface
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from cart.interfaces import CartItemTypedDict, ICart
from tests.conftest import MockCart


class TestCartItemTypedDict:
    """Tests for CartItemTypedDict."""

    def test_cart_item_structure(self, sample_cart_item: CartItemTypedDict) -> None:
        """Test cart item structure.

        Args:
            sample_cart_item: Sample cart item to test
        """
        assert isinstance(sample_cart_item["product"], dict)
        assert isinstance(sample_cart_item["quantity"], int)
        assert isinstance(sample_cart_item["price"], Decimal)
        assert isinstance(sample_cart_item["total_price"], Decimal)

    @pytest.mark.parametrize(
        "field,value,expected_type",
        [
            ("product", {"id": 1, "name": "Test", "price": Decimal("100.00")}, dict),
            ("quantity", 2, int),
            ("price", Decimal("100.00"), Decimal),
            ("total_price", Decimal("200.00"), Decimal),
        ],
    )
    def test_cart_item_fields(
        self,
        sample_cart_item: CartItemTypedDict,
        field: str,
        value: dict[str, int | str | Decimal] | int | Decimal,
        expected_type: type,
    ) -> None:
        """Test cart item field types.

        Args:
            sample_cart_item: Sample cart item to test
            field: Field name to test
            value: Value to set for the field
            expected_type: Expected type of the field
        """
        sample_cart_item[field] = value
        assert isinstance(sample_cart_item[field], expected_type)


class TestICart:
    """Tests for ICart interface."""

    def test_abstract_methods(self) -> None:
        """Test that ICart is an abstract class with required methods."""
        with pytest.raises(TypeError):
            ICart()  # type: ignore

        required_methods = {
            "add",
            "remove",
            "clear",
            "__iter__",
            "__len__",
            "get_total_price",
            "get_item",
        }
        assert all(method in dir(ICart) for method in required_methods)

    @pytest.mark.parametrize(
        "method_name,args",
        [
            ("add", (1, 1, False)),
            ("remove", (1,)),
            ("clear", ()),
            ("__iter__", ()),
            ("__len__", ()),
            ("get_total_price", ()),
            ("get_item", (1,)),
        ],
    )
    def test_method_signatures(self, method_name: str, args: tuple[int | bool, ...]) -> None:
        """Test method signatures in ICart.

        Args:
            method_name: Name of the method to test
            args: Arguments to test the method with
        """
        method = getattr(ICart, method_name)
        assert callable(method)
        assert hasattr(method, "__isabstractmethod__")


class TestMockCartImplementation:
    """Tests for mock cart implementation."""

    def test_add_item(self, mock_cart: MockCart) -> None:
        """Test adding items to mock cart.

        Args:
            mock_cart: Mock cart instance
        """
        mock_cart.add(1, 2)
        assert len(mock_cart) == 2
        item = mock_cart.get_item(1)
        assert item is not None
        assert item["quantity"] == 2
        assert item["total_price"] == Decimal("200.00")

    def test_remove_item(self, mock_cart: MockCart) -> None:
        """Test removing items from mock cart.

        Args:
            mock_cart: Mock cart instance
        """
        mock_cart.add(1, 2)
        mock_cart.remove(1)
        assert len(mock_cart) == 0
        assert mock_cart.get_item(1) is None

    def test_clear_cart(self, mock_cart: MockCart) -> None:
        """Test clearing mock cart.

        Args:
            mock_cart: Mock cart instance
        """
        mock_cart.add(1, 2)
        mock_cart.add(2, 3)
        mock_cart.clear()
        assert len(mock_cart) == 0
        assert mock_cart.get_total_price() == Decimal("0.00")

    def test_iteration(self, mock_cart: MockCart) -> None:
        """Test iterating over mock cart.

        Args:
            mock_cart: Mock cart instance
        """
        mock_cart.add(1, 2)
        mock_cart.add(2, 3)
        items = list(mock_cart)
        assert len(items) == 2
        assert all(
            isinstance(item["product"], dict)
            and isinstance(item["quantity"], int)
            and isinstance(item["price"], Decimal)
            and isinstance(item["total_price"], Decimal)
            for item in items
        )

    def test_total_price(self, mock_cart: MockCart) -> None:
        """Test total price calculation in mock cart.

        Args:
            mock_cart: Mock cart instance
        """
        mock_cart.add(1, 2)  # 2 * 100.00 = 200.00
        mock_cart.add(2, 3)  # 3 * 100.00 = 300.00
        assert mock_cart.get_total_price() == Decimal("500.00")

    def test_override_quantity(self, mock_cart: MockCart) -> None:
        """Test overriding quantity in mock cart.

        Args:
            mock_cart: Mock cart instance
        """
        mock_cart.add(1, 2)
        mock_cart.add(1, 3, override_quantity=True)
        assert mock_cart.get_item(1)["quantity"] == 3
        assert mock_cart.get_item(1)["total_price"] == Decimal("300.00")


class TestCartInterfaceIntegration:
    """Integration tests for cart interface."""

    def test_full_cart_workflow(self, mock_cart: MockCart) -> None:
        """Test complete cart workflow.

        Args:
            mock_cart: Mock cart instance
        """
        # Add items
        mock_cart.add(1, 2)
        mock_cart.add(2, 3)
        assert len(mock_cart) == 5
        assert mock_cart.get_total_price() == Decimal("500.00")

        # Update quantity
        mock_cart.add(1, 1, override_quantity=True)
        assert len(mock_cart) == 4
        assert mock_cart.get_total_price() == Decimal("400.00")

        # Remove item
        mock_cart.remove(2)
        assert len(mock_cart) == 1
        assert mock_cart.get_total_price() == Decimal("100.00")

        # Clear cart
        mock_cart.clear()
        assert len(mock_cart) == 0
        assert mock_cart.get_total_price() == Decimal("0.00")

    def test_cart_item_consistency(self, mock_cart: MockCart) -> None:
        """Test cart item data consistency.

        Args:
            mock_cart: Mock cart instance
        """
        mock_cart.add(1, 2)
        item = mock_cart.get_item(1)
        assert item is not None
        assert item["quantity"] * item["price"] == item["total_price"]
        assert item["product"]["price"] == item["price"]
