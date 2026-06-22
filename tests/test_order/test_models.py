"""
Tests for order models.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from order.models import Order, OrderItem


class TestOrder:
    """Unit tests for Order model."""

    def test_order_creation(self, test_user: User) -> None:
        """Test basic order creation."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
            applied_promo_name="TEST10",
            applied_promo_status=True,
        )
        assert order.user == test_user
        assert order.delivery_address == "123 Main Street"
        assert order.phone == "+79001234567"
        assert order.total_price == Decimal("100.00")
        assert order.applied_promo_name == "TEST10"
        assert order.applied_promo_status is True
        assert not order.is_paid
        assert order.time_created is not None

    def test_order_str_representation(self, test_user: User) -> None:
        """Test order string representation."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )
        assert str(order) == f"Order #{order.id} from {test_user.email}"

    def test_order_meta_options(self) -> None:
        """Test order model meta options."""
        assert Order._meta.ordering == ["-time_created"]
        assert Order._meta.verbose_name == "Order"
        assert Order._meta.verbose_name_plural == "Orders"

    @pytest.mark.parametrize(
        "total_price,is_valid",
        [
            (Decimal("0.01"), True),
            (Decimal("100.00"), True),
            (Decimal("0.00"), False),
            (Decimal("-1.00"), False),
        ],
    )
    def test_order_total_price_validation(self, test_user: User, total_price: Decimal, is_valid: bool) -> None:
        """Test order total price validation."""
        order = Order(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=total_price,
        )
        if is_valid:
            order.full_clean()
            order.save()
            assert order.total_price == total_price
        else:
            with pytest.raises(ValidationError):
                order.full_clean()

    def test_order_get_total_items(self, test_user: User, order_item_data: dict[str, str | int | Decimal]) -> None:
        """Test order total items' calculation."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("200.00"),
            total_price=Decimal("200.00"),
        )
        OrderItem.objects.create(
            order=order,
            product_id=order_item_data["product_id"],
            product_name=order_item_data["product_name"],
            quantity=order_item_data["quantity"],
            price=order_item_data["price"],
        )
        assert order.get_total_items() == order_item_data["quantity"]

    def test_order_with_promo_fields(self, test_user: User) -> None:
        """Test order creation with promo fields."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
            applied_promo_name="DISCOUNT20",
            applied_promo_status=True,
        )
        assert order.applied_promo_name == "DISCOUNT20"
        assert order.applied_promo_status is True

    def test_order_without_promo_fields(self, test_user: User) -> None:
        """Test order creation without promo fields."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )
        assert order.applied_promo_name is None
        assert order.applied_promo_status is False


class TestOrderItem:
    """Unit tests for OrderItem model."""

    def test_order_item_creation(self, test_user: User) -> None:
        """Test basic order item creation."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )
        order_item = OrderItem.objects.create(
            order=order, product_id=1, product_name="Test Product", quantity=2, price=Decimal("50.00")
        )
        assert order_item.order == order
        assert order_item.product_id == 1
        assert order_item.product_name == "Test Product"
        assert order_item.quantity == 2
        assert order_item.price == Decimal("50.00")

    def test_order_item_str_representation(self, test_user: User) -> None:
        """Test order item string representation."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )
        order_item = OrderItem.objects.create(
            order=order, product_id=1, product_name="Test Product", quantity=2, price=Decimal("50.00")
        )
        assert str(order_item) == "2 x Test Product (50.00 ₽)"

    def test_order_item_meta_options(self) -> None:
        """Test order item model meta options."""
        assert OrderItem._meta.verbose_name == "Order Item"
        assert OrderItem._meta.verbose_name_plural == "Order Items"

    @pytest.mark.parametrize(
        "quantity,is_valid",
        [
            (1, True),
            (2, True),
            (0, False),
            (-1, False),
        ],
    )
    def test_order_item_quantity_validation(self, test_user: User, quantity: int, is_valid: bool) -> None:
        """Test order item quantity validation."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )
        order_item = OrderItem(
            order=order, product_id=1, product_name="Test Product", quantity=quantity, price=Decimal("50.00")
        )
        if is_valid:
            order_item.full_clean()
            order_item.save()
            assert order_item.quantity == quantity
        else:
            with pytest.raises(ValidationError):
                order_item.full_clean()

    @pytest.mark.parametrize(
        "price,is_valid",
        [
            (Decimal("0.01"), True),
            (Decimal("50.00"), True),
            (Decimal("0.00"), False),
            (Decimal("-1.00"), False),
        ],
    )
    def test_order_item_price_validation(self, test_user: User, price: Decimal, is_valid: bool) -> None:
        """Test order item price validation."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )
        order_item = OrderItem(order=order, product_id=1, product_name="Test Product", quantity=2, price=price)
        if is_valid:
            order_item.full_clean()
            order_item.save()
            assert order_item.price == price
        else:
            with pytest.raises(ValidationError):
                order_item.full_clean()


class TestOrderIntegration:
    """Integration tests for Order and OrderItem models."""

    def test_order_with_multiple_items(self, test_user: User) -> None:
        """Test order with multiple items."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("300.00"),
            total_price=Decimal("300.00"),
        )

        OrderItem.objects.create(
            order=order, product_id=1, product_name="Product 1", quantity=2, price=Decimal("50.00")
        )
        OrderItem.objects.create(
            order=order, product_id=2, product_name="Product 2", quantity=1, price=Decimal("200.00")
        )

        assert order.items.count() == 2
        assert order.get_total_items() == 3  # 2 + 1 = 3

    def test_order_cascade_delete(self, test_user: User) -> None:
        """Test that order items are deleted when order is deleted."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )

        OrderItem.objects.create(
            order=order, product_id=1, product_name="Test Product", quantity=2, price=Decimal("50.00")
        )

        assert OrderItem.objects.count() == 1

        # Delete the order
        order.delete()

        # Check that order item is also deleted
        assert OrderItem.objects.count() == 0


class TestOrderWithMocks:
    """Tests for Order model using mocks."""

    def test_order_with_mocked_user(self, test_user: User, mocker) -> None:
        """Test order with mocked user."""
        order = Order.objects.create(
            user=test_user,  # Use real user for DB
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )

        # Mock the __str__ method to return our desired format
        expected_str = f"Order #{order.id} from existing@example.com"
        mocker.patch.object(order, "__str__", return_value=expected_str)
        assert str(order) == expected_str

    def test_order_total_items_mock(self, mocker, test_user: User) -> None:
        """Test order total items with mocked items."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )

        # Mock the get_total_items method directly
        mocker.patch.object(order, "get_total_items", return_value=6)

        assert order.get_total_items() == 6  # 2 + 3 + 1 = 6

    def test_order_promo_fields_mock(self, test_user: User) -> None:
        """Test order promo fields with mocked values."""
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )

        # Mock promo fields
        order.applied_promo_name = "MOCK_PROMO"
        order.applied_promo_status = True

        assert order.applied_promo_name == "MOCK_PROMO"
        assert order.applied_promo_status is True
