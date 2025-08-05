"""
Tests for order services.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from order.models import Order, OrderItem
from order.services import OrderService, DatabaseOrderRepository, EmailOrderNotification
from order.domains import OrderItemData, OrderData, OrderCreateData


class TestOrderService:
    """Unit tests for OrderService."""

    def test_order_service_creation(self, mocker) -> None:
        """Test OrderService initialization with dependencies."""
        repository = mocker.Mock()
        notifier = mocker.Mock()
        service = OrderService(repository, notifier)
        assert service.repository == repository
        assert service.notifier == notifier

    def test_create_order(
        self,
        mocker,
        test_user: User,
        mock_cart_for_order,
        mock_form_data,
        mock_applied_promo_id
    ) -> None:
        """Test order creation through service with new signature."""
        # Setup mocks
        mock_repository = mocker.Mock()
        mock_notifier = mocker.Mock()
        mock_promo_context = mocker.patch('order.services.get_applied_promo_context')
        
        mock_promo_context.return_value = {
            'applied_promo_name': 'TEST10',
            'applied_promo_status': True
        }
        
        mock_repository.save_order.return_value = {
            'order_id': 1,
            'user_email': test_user.email,
            'delivery_address': mock_form_data['delivery_address'],
            'phone': mock_form_data['phone'],
            'total_price': Decimal('200.00'),
            'time_created': '2024-03-20 12:00:00',
            'items': [
                {
                    'product_id': 1,
                    'product_name': 'Test Product',
                    'quantity': 2,
                    'price': Decimal('100.00')
                }
            ],
            'applied_promo_name': 'TEST10',
            'applied_promo_status': True
        }
        
        # Create service with mocks
        service = OrderService(mock_repository, mock_notifier)

        result = service.create_order(
            user=test_user,
            cart=mock_cart_for_order,
            form_data=mock_form_data,
            applied_promo_id=mock_applied_promo_id
        )

        # Assertions
        assert isinstance(result, dict)
        assert result['user_email'] == test_user.email
        assert result['delivery_address'] == mock_form_data['delivery_address']
        assert result['phone'] == mock_form_data['phone']
        assert result['total_price'] == Decimal('200.00')
        
        # Verify mock calls
        mock_repository.save_order.assert_called_once()
        mock_promo_context.assert_called_once_with(mock_cart_for_order, mock_applied_promo_id)


class TestDatabaseOrderRepository:
    """Unit tests for DatabaseOrderRepository."""

    def test_save_order(
        self,
        test_user: User,
        order_item_data: dict[str, str | int | Decimal]
    ) -> None:
        """Test order saving to database."""
        repository = DatabaseOrderRepository()
        
        order_data: OrderCreateData = {
            'user': test_user,
            'user_email': test_user.email,
            'delivery_address': '123 Main Street',
            'phone': '+79001234567',
            'cart_price': Decimal('200.00'),
            'total_price': Decimal('200.00'),
            'items': [order_item_data],
            'applied_promo_name': 'TEST10',
            'applied_promo_status': True,
            'discount_sum': Decimal('0.00'),
        }
        
        result = repository.save_order(order_data)
        
        assert isinstance(result, dict)
        assert 'order_id' in result
        assert result['user_email'] == test_user.email
        assert result['delivery_address'] == '123 Main Street'
        assert result['phone'] == '+79001234567'
        assert result['total_price'] == Decimal('200.00')
        assert 'time_created' in result
        assert len(result['items']) == 1

    def test_save_order_with_multiple_items(
        self,
        mocker,
        test_user: User,
        order_item_data: dict[str, str | int | Decimal]
    ) -> None:
        """Test order saving with multiple items."""
        mock_order_create = mocker.patch('order.models.Order.objects.create')
        mock_order_item_create = mocker.patch('order.models.OrderItem.objects.create')
        
        repository = DatabaseOrderRepository()
        
        # Create mock order
        mock_order = mocker.Mock()
        mock_order.id = 1
        mock_order.user = test_user
        mock_order.delivery_address = '123 Main Street'
        mock_order.phone = '+79001234567'
        mock_order.total_price = Decimal('300.00')
        mock_order.time_created = '2024-03-20 12:00:00'
        mock_order.applied_promo_name = 'TEST10'
        mock_order.applied_promo_status = True
        mock_order_create.return_value = mock_order
        
        # Create mock order items
        mock_order_item = mocker.Mock()
        mock_order_item.product_name = 'Test Product'
        mock_order_item.quantity = 2
        mock_order_item.price = Decimal('100.00')
        mock_order_item_create.return_value = mock_order_item
        
        order_data: OrderCreateData = {
            'user': test_user,
            'user_email': test_user.email,
            'delivery_address': '123 Main Street',
            'phone': '+79001234567',
            'cart_price': Decimal('300.00'),
            'total_price': Decimal('300.00'),
            'items': [order_item_data, order_item_data],  # Two items
            'applied_promo_name': 'TEST10',
            'applied_promo_status': True,
            'discount_sum': Decimal('0.00'),
        }
        
        result = repository.save_order(order_data)
        
        assert len(result['items']) == 2
        mock_order_create.assert_called_once()
        assert mock_order_item_create.call_count == 2

    @pytest.mark.parametrize('invalid_data', [
        {'user': None},
        {'user_email': None},
        {'delivery_address': None},
        {'phone': None},
        {'total_price': None},
        {'items': None},
    ])
    def test_save_order_invalid_data(self, invalid_data: dict[str, None]) -> None:
        """Test order saving with invalid data."""
        repository = DatabaseOrderRepository()
        
        # This should raise an exception or handle invalid data appropriately
        with pytest.raises(Exception):
            repository.save_order(invalid_data)


class TestEmailOrderNotification:
    """Unit tests for EmailOrderNotification."""

    def test_send_order_notification(
        self,
        mocker,
        test_user: User
    ) -> None:
        """Test order notification sending with new signature."""
        # Setup mocks
        mock_order_get = mocker.patch('order.models.Order.objects.get')
        mock_render_to_string = mocker.patch('order.services.render_to_string')
        mock_send_mail = mocker.patch('order.services.send_mail')
        
        mock_order = mocker.Mock()
        mock_order.id = 1
        mock_order_get.return_value = mock_order
        
        mock_render_to_string.side_effect = ['text_message', 'html_message']
        
        # Create notification service
        notifier = EmailOrderNotification()
        
        # Test
        notifier.send_order_notification(order_id=1)
        
        # Assertions
        mock_order_get.assert_called_once_with(id=1)
        mock_send_mail.assert_called_once()
        assert mock_send_mail.call_args[1]['subject'] == 'New Order #1'

    def test_send_order_notification_error(
        self,
        mocker,
        test_user: User
    ) -> None:
        """Test order notification error handling."""
        mock_order_get = mocker.patch('order.models.Order.objects.get')
        mock_send_mail = mocker.patch('order.services.send_mail')
        
        # Simulate database error
        mock_order_get.side_effect = Order.DoesNotExist()
        
        notifier = EmailOrderNotification()
        
        # Test
        with pytest.raises(Order.DoesNotExist):
            notifier.send_order_notification(order_id=999)


class TestOrderServiceIntegration:
    """Integration tests for OrderService."""

    def test_complete_order_flow(
        self,
        mocker,
        test_user: User,
        mock_cart_for_order,
        mock_form_data,
        mock_applied_promo_id
    ) -> None:
        """Test complete order creation flow."""
        # Setup mocks
        mock_repository = mocker.Mock()
        mock_notifier = mocker.Mock()
        mock_promo_context = mocker.patch('order.services.get_applied_promo_context')
        
        mock_promo_context.return_value = {
            'applied_promo_name': 'TEST10',
            'applied_promo_status': True
        }
        
        mock_repository.save_order.return_value = {
            'order_id': 1,
            'user_email': test_user.email,
            'delivery_address': mock_form_data['delivery_address'],
            'phone': mock_form_data['phone'],
            'total_price': Decimal('200.00'),
            'time_created': '2024-03-20 12:00:00',
            'items': [
                {
                    'product_id': 1,
                    'product_name': 'Test Product',
                    'quantity': 2,
                    'price': Decimal('100.00')
                }
            ],
            'applied_promo_name': 'TEST10',
            'applied_promo_status': True
        }
        
        # Create service
        service = OrderService(mock_repository, mock_notifier)
        
        # Test
        result = service.create_order(
            user=test_user,
            cart=mock_cart_for_order,
            form_data=mock_form_data,
            applied_promo_id=mock_applied_promo_id
        )
        
        # Assertions
        assert result['order_id'] == 1
        assert result['user_email'] == test_user.email
        mock_repository.save_order.assert_called_once()
        mock_promo_context.assert_called_once()

    def test_order_with_multiple_items(
        self,
        mocker,
        test_user: User,
        mock_cart_for_order,
        mock_form_data,
        mock_applied_promo_id
    ) -> None:
        """Test order creation with multiple items."""
        # Setup mocks
        mock_repository = mocker.Mock()
        mock_notifier = mocker.Mock()
        mock_promo_context = mocker.patch('order.services.get_applied_promo_context')
        
        mock_promo_context.return_value = {
            'applied_promo_name': 'TEST10',
            'applied_promo_status': True
        }
        
        # Update cart to have multiple items
        mock_cart_for_order.__iter__.return_value = iter([
            {
                'product': mocker.Mock(id=1, name='Product 1', price=Decimal('100.00')),
                'quantity': 2,
                'price': Decimal('100.00'),
                'total_price': Decimal('200.00')
            },
            {
                'product': mocker.Mock(id=2, name='Product 2', price=Decimal('150.00')),
                'quantity': 1,
                'price': Decimal('150.00'),
                'total_price': Decimal('150.00')
            }
        ])
        mock_cart_for_order.get_total_price.return_value = Decimal('350.00')
        
        mock_repository.save_order.return_value = {
            'order_id': 1,
            'user_email': test_user.email,
            'delivery_address': mock_form_data['delivery_address'],
            'phone': mock_form_data['phone'],
            'total_price': Decimal('350.00'),
            'time_created': '2024-03-20 12:00:00',
            'items': [
                {
                    'product_id': 1,
                    'product_name': 'Product 1',
                    'quantity': 2,
                    'price': Decimal('100.00')
                },
                {
                    'product_id': 2,
                    'product_name': 'Product 2',
                    'quantity': 1,
                    'price': Decimal('150.00')
                }
            ],
            'applied_promo_name': 'TEST10',
            'applied_promo_status': True
        }
        
        # Create service
        service = OrderService(mock_repository, mock_notifier)
        
        # Test
        result = service.create_order(
            user=test_user,
            cart=mock_cart_for_order,
            form_data=mock_form_data,
            applied_promo_id=mock_applied_promo_id
        )
        
        # Assertions
        assert result['order_id'] == 1
        assert result['total_price'] == Decimal('350.00')
        assert len(result['items']) == 2
        mock_repository.save_order.assert_called_once()
