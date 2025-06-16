from __future__ import annotations

from decimal import Decimal
from typing import TypedDict
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User

from order.interfaces import OrderItemData, OrderData, IOrderService, IOrderNotification, IOrderRepository
from order.services import OrderService, EmailOrderNotification, DatabaseOrderRepository
from order.models import Order


class TestOrderItemData:
    """Unit tests for OrderItemData TypedDict structure and validation."""

    def test_order_item_data_structure(self, order_item_data: dict[str, str | int | Decimal]) -> None:
        """Test OrderItemData structure and field types.
        
        Args:
            order_item_data: Sample order item data fixture
        """
        item_data = OrderItemData(order_item_data)
        assert isinstance(item_data['product_id'], int)
        assert isinstance(item_data['product_name'], str)
        assert isinstance(item_data['quantity'], int)
        assert isinstance(item_data['price'], Decimal)


class TestOrderData:
    """Unit tests for OrderData TypedDict structure and validation."""

    def test_order_data_structure(self, order_data: dict[str, str | int | Decimal | list[dict[str, str | int | Decimal]]]) -> None:
        """Test OrderData structure and field types.
        
        Args:
            order_data: Sample order data fixture
        """
        data = OrderData(order_data)
        assert isinstance(data['order_id'], int)
        assert isinstance(data['user_email'], str)
        assert isinstance(data['delivery_address'], str)
        assert isinstance(data['phone'], str)
        assert isinstance(data['total_price'], Decimal)
        assert isinstance(data['time_created'], str)
        assert isinstance(data['items'], list)
        assert all(isinstance(item, dict) for item in data['items'])


class TestIOrderService:
    """Unit tests for IOrderService Protocol implementation."""

    def test_order_service_interface(self, test_user: User, order_item_data: dict[str, str | int | Decimal], mock_order_service: None) -> None:
        """Test OrderService implements IOrderService interface.
        
        Args:
            test_user: Test user fixture
            order_item_data: Order item data fixture
            mock_order_service: Mocked order service fixture
        """
        service = OrderService(MagicMock(), MagicMock())
        result = service.create_order(
            user=test_user,
            items=[order_item_data],
            total_price=Decimal('200.00'),
            delivery_address='123 Main Street',
            phone='+79001234567'
        )
        assert isinstance(result, dict)
        assert 'order_id' in result
        assert 'user_email' in result
        assert 'items' in result

    @pytest.mark.parametrize('invalid_data', [
        {'user': None, 'items': [], 'total_price': Decimal('0'), 'delivery_address': '', 'phone': ''},
        {'user': MagicMock(), 'items': None, 'total_price': Decimal('0'), 'delivery_address': '', 'phone': ''},
        {'user': MagicMock(), 'items': [], 'total_price': None, 'delivery_address': '', 'phone': ''},
    ])
    def test_order_service_invalid_data(self, invalid_data: dict[str, object | None]) -> None:
        """Test OrderService with invalid data.
        
        Args:
            invalid_data: Invalid order data
        """
        service = OrderService(MagicMock(), MagicMock())
        with pytest.raises(Exception):
            service.create_order(**invalid_data)


class TestIOrderNotification:
    """Unit tests for IOrderNotification Protocol implementation."""

    def test_order_notification_interface(self, mock_order_notification: None) -> None:
        """Test EmailOrderNotification implements IOrderNotification interface.
        
        Args:
            mock_order_notification: Mocked order notification fixture
        """
        notification = EmailOrderNotification()
        order = MagicMock()
        notification.send_order_notification(order)  # Should not raise any exceptions

    @patch('order.services.send_mail')
    def test_order_notification_send_mail(self, mock_send_mail: MagicMock) -> None:
        """Test order notification sends email.
        
        Args:
            mock_send_mail: Mocked send_mail function
        """
        notification = EmailOrderNotification()
        order = MagicMock()
        notification.send_order_notification(order)
        mock_send_mail.assert_called_once()


class TestIOrderRepository:
    """Unit tests for IOrderRepository Protocol implementation."""

    def test_order_repository_interface(self, order_data: dict[str, str | int | Decimal | list[dict[str, str | int | Decimal]]], mock_order_repository: None) -> None:
        """Test DatabaseOrderRepository implements IOrderRepository interface.
        
        Args:
            order_data: Sample order data fixture
            mock_order_repository: Mocked order repository fixture
        """
        repository = DatabaseOrderRepository()
        result = repository.save_order(order_data)
        assert isinstance(result, dict)
        assert result == order_data

    @pytest.mark.parametrize('invalid_data', [
        {'order_id': None},
        {'user_email': None},
        {'delivery_address': None},
        {'phone': None},
        {'total_price': None},
        {'items': None},
    ])
    def test_order_repository_invalid_data(self, invalid_data: dict[str, None]) -> None:
        """Test order repository with invalid data.
        
        Args:
            invalid_data: Invalid order data
        """
        repository = DatabaseOrderRepository()
        with pytest.raises(Exception):
            repository.save_order(invalid_data)


class TestOrderServiceIntegration:
    """Integration tests for OrderService with mocked dependencies."""

    @patch('order.models.Order.objects.get')
    def test_order_creation_flow(
        self,
        mock_order_get: MagicMock,
        test_user: User,
        order_item_data: dict[str, str | int | Decimal],
        mock_order_repository: None,
        mock_order_notification: None
    ) -> None:
        """Test complete order creation flow with mocked dependencies.
        
        Args:
            mock_order_get: Mocked Order.objects.get
            test_user: Test user fixture
            order_item_data: Order item data fixture
            mock_order_repository: Mocked order repository fixture
            mock_order_notification: Mocked order notification fixture
        """
        # Setup mock order
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.user = test_user
        mock_order.delivery_address = '123 Main Street'
        mock_order.phone = '+79001234567'
        mock_order.total_price = Decimal('200.00')
        mock_order_get.return_value = mock_order

        # Create service with mocked dependencies
        repository = DatabaseOrderRepository()
        notifier = EmailOrderNotification()
        service = OrderService(repository, notifier)

        # Create order
        result = service.create_order(
            user=test_user,
            items=[order_item_data],
            total_price=Decimal('200.00'),
            delivery_address='123 Main Street',
            phone='+79001234567'
        )
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'order_id' in result
        assert 'user_email' in result
        assert 'delivery_address' in result
        assert 'phone' in result
        assert 'total_price' in result
        assert 'time_created' in result
        assert 'items' in result
        
        # Check result values
        assert result['user_email'] == test_user.email
        assert result['delivery_address'] == '123 Main Street'
        assert result['phone'] == '+79001234567'
        assert result['total_price'] == Decimal('200.00')
        assert result['items'] == [order_item_data]
        
        # Verify mock calls
        mock_order_get.assert_called_once_with(id=1)
