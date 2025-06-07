from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from order.models import Order, OrderItem
from order.services import OrderService, DatabaseOrderRepository, EmailOrderNotification
from order.interfaces import OrderItemData, OrderData


class TestOrderService:
    """Unit tests for OrderService."""

    def test_order_service_creation(self) -> None:
        """Test OrderService initialization with dependencies."""
        repository = MagicMock()
        notifier = MagicMock()
        service = OrderService(repository, notifier)
        assert service.repository == repository
        assert service.notifier == notifier

    @patch('order.models.Order.objects.get')
    def test_create_order(
        self,
        mock_order_get: MagicMock,
        test_user: User,
        order_item_data: dict[str, str | int | Decimal]
    ) -> None:
        """Test order creation through service.
        
        Args:
            mock_order_get: Mocked Order.objects.get
            test_user: Test user fixture
            order_item_data: Order item data fixture
        """
        # Create mocks
        mock_repository = MagicMock()
        mock_notifier = MagicMock()
        
        # Setup repository mock
        mock_repository.save_order.return_value = {
            'order_id': 1,
            'user_email': test_user.email,
            'delivery_address': '123 Main Street',
            'phone': '+79001234567',
            'total_price': Decimal('200.00'),
            'time_created': '2024-03-20 12:00:00',
            'items': [order_item_data]
        }
        
        # Setup order mock
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.user = test_user
        mock_order.delivery_address = '123 Main Street'
        mock_order.phone = '+79001234567'
        mock_order.total_price = Decimal('200.00')
        mock_order_get.return_value = mock_order
        
        # Create service with mocks
        service = OrderService(mock_repository, mock_notifier)

        result = service.create_order(
            user=test_user,
            items=[order_item_data],
            total_price=Decimal('200.00'),
            delivery_address='123 Main Street',
            phone='+79001234567'
        )

        assert isinstance(result, dict)
        assert result['user_email'] == test_user.email
        assert result['delivery_address'] == '123 Main Street'
        assert result['phone'] == '+79001234567'
        assert result['total_price'] == Decimal('200.00')
        assert result['items'] == [order_item_data]
        
        # Verify mock calls
        mock_repository.save_order.assert_called_once()
        mock_notifier.send_order_notification.assert_called_once_with(mock_order)
        mock_order_get.assert_called_once_with(id=1)

    @pytest.mark.parametrize('invalid_data', [
        {'user': None, 'items': [], 'total_price': Decimal('0'), 'delivery_address': '', 'phone': ''},
        {'user': MagicMock(), 'items': None, 'total_price': Decimal('0'), 'delivery_address': '', 'phone': ''},
        {'user': MagicMock(), 'items': [], 'total_price': None, 'delivery_address': '', 'phone': ''},
    ])
    def test_create_order_invalid_data(self, invalid_data: dict[str, object | None]) -> None:
        """Test order creation with invalid data.
        
        Args:
            invalid_data: Invalid order data
        """
        service = OrderService(MagicMock(), MagicMock())
        with pytest.raises(Exception):
            service.create_order(**invalid_data)


class TestDatabaseOrderRepository:
    """Unit tests for DatabaseOrderRepository."""

    def test_save_order(
        self,
        test_user: User,
        order_item_data: dict[str, str | int | Decimal]
    ) -> None:
        """Test order saving to database.
        
        Args:
            test_user: Test user fixture
            order_item_data: Order item data fixture
        """
        repository = DatabaseOrderRepository()
        order_data: OrderData = {
            'user': test_user,
            'user_email': test_user.email,
            'delivery_address': '123 Main Street',
            'phone': '+79001234567',
            'total_price': Decimal('200.00'),
            'items': [order_item_data]
        }

        result = repository.save_order(order_data)

        assert isinstance(result, dict)
        assert result['user_email'] == test_user.email
        assert result['delivery_address'] == '123 Main Street'
        assert result['phone'] == '+79001234567'
        assert result['total_price'] == Decimal('200.00')
        assert len(result['items']) == 1
        assert result['items'][0]['product_name'] == order_item_data['product_name']
        assert result['items'][0]['quantity'] == order_item_data['quantity']
        assert result['items'][0]['price'] == order_item_data['price']

    @patch('order.models.Order.objects.create')
    @patch('order.models.OrderItem.objects.create')
    def test_save_order_with_multiple_items(
        self,
        mock_order_item_create: MagicMock,
        mock_order_create: MagicMock,
        test_user: User,
        order_item_data: dict[str, str | int | Decimal]
    ) -> None:
        """Test saving order with multiple items.
        
        Args:
            mock_order_item_create: Mocked OrderItem.objects.create
            mock_order_create: Mocked Order.objects.create
            test_user: Test user fixture
            order_item_data: Order item data fixture
        """
        # Setup order mock
        mock_order = MagicMock(spec=Order)
        mock_order.id = 1
        mock_order.user = test_user
        mock_order.delivery_address = '123 Main Street'
        mock_order.phone = '+79001234567'
        mock_order.total_price = Decimal('600.00')
        mock_order_create.return_value = mock_order
        
        # Setup order item mocks
        mock_items = []
        for i in range(3):
            mock_item = MagicMock(spec=OrderItem)
            mock_item.product_id = i + 1
            mock_item.product_name = f'Product {i + 1}'
            mock_item.quantity = order_item_data['quantity']
            mock_item.price = order_item_data['price']
            mock_items.append(mock_item)
        mock_order_item_create.side_effect = mock_items
        
        repository = DatabaseOrderRepository()
        items = [
            order_item_data,
            {**order_item_data, 'product_id': 2, 'product_name': 'Product 2'},
            {**order_item_data, 'product_id': 3, 'product_name': 'Product 3'}
        ]
        order_data: OrderData = {
            'user': test_user,
            'user_email': test_user.email,
            'delivery_address': '123 Main Street',
            'phone': '+79001234567',
            'total_price': Decimal('600.00'),
            'items': items
        }

        result = repository.save_order(order_data)

        # Verify order creation
        mock_order_create.assert_called_once_with(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('600.00')
        )
        
        # Verify order items creation
        assert mock_order_item_create.call_count == 3
        for i, item in enumerate(items):
            mock_order_item_create.assert_any_call(
                order=mock_order,
                product_id=item['product_id'],
                product_name=item['product_name'],
                quantity=item['quantity'],
                price=item['price']
            )

    @pytest.mark.parametrize('invalid_data', [
        {'user': None},
        {'user_email': None},
        {'delivery_address': None},
        {'phone': None},
        {'total_price': None},
        {'items': None},
    ])
    def test_save_order_invalid_data(self, invalid_data: dict[str, None]) -> None:
        """Test saving order with invalid data.
        
        Args:
            invalid_data: Invalid order data
        """
        repository = DatabaseOrderRepository()
        with pytest.raises(Exception):
            repository.save_order(invalid_data)


class TestEmailOrderNotification:
    """Unit tests for EmailOrderNotification."""

    @patch('order.services.send_mail')
    def test_send_order_notification(
        self,
        mock_send_mail: MagicMock,
        test_user: User
    ) -> None:
        """Test sending order notification email.
        
        Args:
            mock_send_mail: Mocked send_mail function
            test_user: Test user fixture
        """
        notification = EmailOrderNotification()
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('200.00')
        )

        notification.send_order_notification(order)

        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args[1]
        assert call_args['subject'] == f"New Order #{order.id}"
        assert 'Order Information' in call_args['message']
        assert 'Order Items' in call_args['message']
        assert call_args['from_email'] is not None
        assert call_args['recipient_list'] is not None

    @patch('order.services.send_mail')
    def test_send_order_notification_error(
        self,
        mock_send_mail: MagicMock,
        test_user: User
    ) -> None:
        """Test error handling in order notification.
        
        Args:
            mock_send_mail: Mocked send_mail function
            test_user: Test user fixture
        """
        mock_send_mail.side_effect = Exception("Email error")
        notification = EmailOrderNotification()
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('200.00')
        )

        with pytest.raises(Exception):
            notification.send_order_notification(order)


# Integration tests
class TestOrderServiceIntegration:
    """Integration tests for OrderService with real dependencies."""

    def test_complete_order_flow(
        self,
        test_user: User,
        order_item_data: dict[str, str | int | Decimal]
    ) -> None:
        """Test complete order creation flow with real dependencies.
        
        Args:
            test_user: Test user fixture
            order_item_data: Order item data fixture
        """
        repository = DatabaseOrderRepository()
        notifier = EmailOrderNotification()
        service = OrderService(repository, notifier)

        result = service.create_order(
            user=test_user,
            items=[order_item_data],
            total_price=Decimal('200.00'),
            delivery_address='123 Main Street',
            phone='+79001234567'
        )

        # Verify order was created
        order = Order.objects.get(id=result['order_id'])
        assert order.user == test_user
        assert order.delivery_address == '123 Main Street'
        assert order.phone == '+79001234567'
        assert order.total_price == Decimal('200.00')

        # Verify order items were created
        assert order.items.count() == 1
        item = order.items.first()
        assert item.product_id == order_item_data['product_id']
        assert item.product_name == order_item_data['product_name']
        assert item.quantity == order_item_data['quantity']
        assert item.price == order_item_data['price']

    def test_order_with_multiple_items(
        self,
        test_user: User,
        order_item_data: dict[str, str | int | Decimal]
    ) -> None:
        """Test order creation with multiple items using real dependencies.
        
        Args:
            test_user: Test user fixture
            order_item_data: Order item data fixture
        """
        repository = DatabaseOrderRepository()
        notifier = EmailOrderNotification()
        service = OrderService(repository, notifier)

        # Create items with correct names
        items = [
            {**order_item_data, 'product_id': i, 'product_name': f'Product {i}'}
            for i in range(1, 4)
        ]

        result = service.create_order(
            user=test_user,
            items=items,
            total_price=Decimal('600.00'),
            delivery_address='123 Main Street',
            phone='+79001234567'
        )

        # Verify order was created
        order = Order.objects.get(id=result['order_id'])
        assert order.user == test_user
        assert order.delivery_address == '123 Main Street'
        assert order.phone == '+79001234567'
        assert order.total_price == Decimal('600.00')

        # Verify items were created
        assert order.items.count() == 3
        saved_items = list(order.items.all())
        assert len(saved_items) == 3
        
        # Verify each item
        for i, item in enumerate(saved_items, 1):
            assert item.product_id == i
            assert item.product_name == f'Product {i}'
            assert item.quantity == order_item_data['quantity']
            assert item.price == order_item_data['price']
