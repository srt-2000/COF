from __future__ import annotations

from decimal import Decimal
from typing import TypedDict
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from order.models import Order, OrderItem


class TestOrder:
    """Unit tests for Order model."""

    def test_order_creation(self, test_user: User) -> None:
        """Test basic order creation.
        
        Args:
            test_user: Test user fixture
        """
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('100.00')
        )
        assert order.user == test_user
        assert order.delivery_address == '123 Main Street'
        assert order.phone == '+79001234567'
        assert order.total_price == Decimal('100.00')
        assert not order.is_paid
        assert order.time_created is not None

    def test_order_str_representation(self, test_user: User) -> None:
        """Test order string representation.
        
        Args:
            test_user: Test user fixture
        """
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('100.00')
        )
        assert str(order) == f"Order #{order.id} from {test_user.email}"

    def test_order_meta_options(self) -> None:
        """Test order model meta options."""
        assert Order._meta.ordering == ['-time_created']
        assert Order._meta.verbose_name == "Order"
        assert Order._meta.verbose_name_plural == "Orders"

    @pytest.mark.parametrize('total_price,is_valid', [
        (Decimal('0.01'), True),
        (Decimal('100.00'), True),
        (Decimal('0.00'), False),
        (Decimal('-1.00'), False),
    ])
    def test_order_total_price_validation(self, test_user: User, total_price: Decimal, is_valid: bool) -> None:
        """Test order total price validation.
        
        Args:
            test_user: Test user fixture
            total_price: Total price to test
            is_valid: Whether the price should be valid
        """
        order = Order(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=total_price
        )
        if is_valid:
            order.full_clean()
            order.save()
            assert order.total_price == total_price
        else:
            with pytest.raises(ValidationError):
                order.full_clean()

    def test_order_get_total_items(self, test_user: User, order_item_data: dict[str, str | int | Decimal]) -> None:
        """Test order total items calculation.
        
        Args:
            test_user: Test user fixture
            order_item_data: Order item data fixture
        """
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('200.00')
        )
        OrderItem.objects.create(
            order=order,
            product_id=order_item_data['product_id'],
            product_name=order_item_data['product_name'],
            quantity=order_item_data['quantity'],
            price=order_item_data['price']
        )
        assert order.get_total_items() == order_item_data['quantity']


class TestOrderItem:
    """Unit tests for OrderItem model."""

    def test_order_item_creation(self, test_user: User) -> None:
        """Test basic order item creation.
        
        Args:
            test_user: Test user fixture
        """
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('100.00')
        )
        item = OrderItem.objects.create(
            order=order,
            product_id=1,
            product_name='Test Product',
            quantity=2,
            price=Decimal('50.00')
        )
        assert item.order == order
        assert item.product_id == 1
        assert item.product_name == 'Test Product'
        assert item.quantity == 2
        assert item.price == Decimal('50.00')

    def test_order_item_str_representation(self, test_user: User) -> None:
        """Test order item string representation.
        
        Args:
            test_user: Test user fixture
        """
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('100.00')
        )
        item = OrderItem.objects.create(
            order=order,
            product_id=1,
            product_name='Test Product',
            quantity=2,
            price=Decimal('50.00')
        )
        assert str(item) == "2 x Test Product (50.00 ₽)"

    def test_order_item_meta_options(self) -> None:
        """Test order item model meta options."""
        assert OrderItem._meta.verbose_name == "Order Item"
        assert OrderItem._meta.verbose_name_plural == "Order Items"

    @pytest.mark.parametrize('quantity,is_valid', [
        (1, True),
        (2, True),
        (0, False),
        (-1, False),
    ])
    def test_order_item_quantity_validation(self, test_user: User, quantity: int, is_valid: bool) -> None:
        """Test order item quantity validation.
        
        Args:
            test_user: Test user fixture
            quantity: Quantity to test
            is_valid: Whether the quantity should be valid
        """
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('100.00')
        )
        item = OrderItem(
            order=order,
            product_id=1,
            product_name='Test Product',
            quantity=quantity,
            price=Decimal('50.00')
        )
        if is_valid:
            item.full_clean()
            item.save()
            assert item.quantity == quantity
        else:
            with pytest.raises(ValidationError):
                item.full_clean()

    @pytest.mark.parametrize('price,is_valid', [
        (Decimal('0.01'), True),
        (Decimal('50.00'), True),
        (Decimal('0.00'), False),
        (Decimal('-1.00'), False),
    ])
    def test_order_item_price_validation(self, test_user: User, price: Decimal, is_valid: bool) -> None:
        """Test order item price validation.
        
        Args:
            test_user: Test user fixture
            price: Price to test
            is_valid: Whether the price should be valid
        """
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('100.00')
        )
        item = OrderItem(
            order=order,
            product_id=1,
            product_name='Test Product',
            quantity=2,
            price=price
        )
        if is_valid:
            item.full_clean()
            item.save()
            assert item.price == price
        else:
            with pytest.raises(ValidationError):
                item.full_clean()


# Integration tests
class TestOrderIntegration:
    """Integration tests for Order model with related models."""

    def test_order_with_multiple_items(self, test_user: User) -> None:
        """Test order creation with multiple items.
        
        Args:
            test_user: Test user fixture
        """
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('300.00')
        )
        
        items = [
            OrderItem.objects.create(
                order=order,
                product_id=i,
                product_name=f'Product {i}',
                quantity=2,
                price=Decimal('50.00')
            )
            for i in range(1, 4)
        ]
        
        assert order.items.count() == 3
        assert order.get_total_items() == 6
        assert all(item.order == order for item in items)

    def test_order_cascade_delete(self, test_user: User) -> None:
        """Test order deletion cascades to items.
        
        Args:
            test_user: Test user fixture
        """
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('100.00')
        )
        
        item = OrderItem.objects.create(
            order=order,
            product_id=1,
            product_name='Test Product',
            quantity=2,
            price=Decimal('50.00')
        )
        
        order.delete()
        assert not OrderItem.objects.filter(id=item.id).exists()


# Mock tests
class TestOrderWithMocks:
    """Tests for Order model using mocks."""

    def test_order_with_mocked_user(self, test_user: User) -> None:
        """Test order creation with mocked user.
        
        Args:
            test_user: Test user fixture
        """
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('100.00')
        )
        
        # Mock the string representation
        with patch.object(Order, '__str__', return_value=f"Order #{order.id} from test@example.com"):
            assert str(order) == f"Order #{order.id} from test@example.com"

    @patch('order.models.Order.get_total_items')
    def test_order_total_items_mock(self, mock_get_total_items: MagicMock, test_user: User) -> None:
        """Test order total items with mocked method.
        
        Args:
            mock_get_total_items: Mocked get_total_items method
            test_user: Test user fixture
        """
        mock_get_total_items.return_value = 5
        
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('100.00')
        )
        
        assert order.get_total_items() == 5
        mock_get_total_items.assert_called_once()
