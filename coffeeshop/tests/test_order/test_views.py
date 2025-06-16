from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.test import Client
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, DetailView

from order.forms import OrderCreateForm
from order.models import Order, OrderItem
from order.views import OrderCreateView, OrderDetailView


class TestOrderCreateView:
    """Unit tests for OrderCreateView."""

    def test_view_inheritance(self) -> None:
        """Test view inheritance and configuration."""
        assert issubclass(OrderCreateView, FormView)
        assert OrderCreateView.form_class == OrderCreateForm
        assert OrderCreateView.template_name == 'create_order.html'
        
        # Test get_success_url method
        view = OrderCreateView()
        view.order_data = {
            'order_id': 1,
            'user_email': 'test@example.com',
            'delivery_address': '123 Main Street',
            'phone': '+79001234567',
            'total_price': Decimal('200.00'),
            'time_created': '2024-03-20 12:00:00',
            'items': []
        }
        assert view.get_success_url() == reverse('order_detail', kwargs={'pk': 1})

    def test_get_context_data(self, client: Client, test_user: User) -> None:
        """Test context data includes cart.
        
        Args:
            client: Test client fixture
            test_user: Test user fixture
        """
        client.force_login(test_user)
        response = client.get(reverse('order_create'))
        assert response.status_code == 200
        assert 'cart' in response.context

    def test_get_form_kwargs(self, test_user: User) -> None:
        """Test form kwargs include user.
        
        Args:
            test_user: Test user fixture
        """
        view = OrderCreateView()
        view.request = MagicMock(spec=HttpRequest)
        view.request.user = test_user
        
        # Call parent's get_form_kwargs
        with patch.object(FormView, 'get_form_kwargs') as mock_parent:
            mock_parent.return_value = {}
            kwargs = view.get_form_kwargs()
            assert 'user' in kwargs
            assert kwargs['user'] == test_user

    @patch('order.views.CartFactory.create_from_request')
    @patch('order.views.OrderFactory.create_order_service')
    def test_form_valid(
        self,
        mock_order_service: MagicMock,
        mock_cart: MagicMock,
        test_user: User,
        client: Client
    ) -> None:
        """Test form validation and order creation.
        
        Args:
            mock_order_service: Mocked order service
            mock_cart: Mocked cart
            test_user: Test user fixture
            client: Test client fixture
        """
        # Setup mocks
        mock_cart_instance = MagicMock()
        mock_cart_instance.__iter__.return_value = [
            {
                'product': MagicMock(id=1, name='Test Product'),
                'quantity': 2,
                'price': Decimal('100.00')
            }
        ]
        mock_cart_instance.get_total_price.return_value = Decimal('200.00')
        mock_cart.return_value = mock_cart_instance

        mock_service = MagicMock()
        mock_service.create_order.return_value = {
            'order_id': 1,
            'user_email': test_user.email,
            'delivery_address': '123 Main Street',
            'phone': '+79001234567',
            'total_price': Decimal('200.00'),
            'time_created': '2024-03-20 12:00:00',
            'items': [
                {
                    'product_id': 1,
                    'product_name': 'Test Product',
                    'quantity': 2,
                    'price': Decimal('100.00')
                }
            ]
        }
        mock_order_service.return_value = mock_service

        # Login and submit form
        client.force_login(test_user)
        response = client.post(
            reverse('order_create'),
            {
                'delivery_address': '123 Main Street',
                'phone': '+79001234567'
            }
        )

        # Verify response
        assert response.status_code == 302
        assert response.url == reverse('order_detail', kwargs={'pk': 1})

        # Verify mocks
        mock_cart.assert_called_once()
        mock_order_service.assert_called_once()
        mock_service.create_order.assert_called_once()
        mock_cart_instance.clear.assert_called_once()

    @pytest.mark.parametrize('invalid_data', [
        {'delivery_address': 'Short', 'phone': '123'},  # Too short address, invalid phone
        {'delivery_address': '123 Main Street'},  # Missing phone
        {'phone': '+79001234567'},  # Missing address
    ])
    def test_form_invalid_data(
        self,
        invalid_data: dict[str, str],
        test_user: User,
        client: Client
    ) -> None:
        """Test form validation with invalid data.
        
        Args:
            invalid_data: Invalid form data
            test_user: Test user fixture
            client: Test client fixture
        """
        client.force_login(test_user)
        response = client.post(reverse('order_create'), invalid_data)
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_anonymous_user_redirect(self, client: Client) -> None:
        """Test anonymous user is redirected to login.
        
        Args:
            client: Test client fixture
        """
        response = client.get(reverse('order_create'))
        assert response.status_code == 302
        assert 'login' in response.url


class TestOrderDetailView:
    """Unit tests for OrderDetailView."""

    def test_view_inheritance(self) -> None:
        """Test view inheritance and configuration."""
        assert issubclass(OrderDetailView, DetailView)
        assert OrderDetailView.model == Order
        assert OrderDetailView.template_name == 'order_created.html'
        assert OrderDetailView.context_object_name == 'order'

    def test_get_queryset(self, test_user: User) -> None:
        """Test queryset is filtered by user.
        
        Args:
            test_user: Test user fixture
        """
        view = OrderDetailView()
        view.request = MagicMock(spec=HttpRequest)
        view.request.user = test_user

        queryset = view.get_queryset()
        assert str(queryset.query).count('WHERE') == 1
        assert 'user_id' in str(queryset.query)

    def test_order_detail_page(
        self,
        test_user: User,
        client: Client
    ) -> None:
        """Test order detail page displays correctly.
        
        Args:
            test_user: Test user fixture
            client: Test client fixture
        """
        # Create test order
        order = Order.objects.create(
            user=test_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('200.00')
        )
        OrderItem.objects.create(
            order=order,
            product_id=1,
            product_name='Test Product',
            quantity=2,
            price=Decimal('100.00')
        )

        # Login and view order
        client.force_login(test_user)
        response = client.get(reverse('order_detail', kwargs={'pk': order.id}))

        # Verify response
        assert response.status_code == 200
        assert response.context['order'] == order
        assert 'Test Product' in response.content.decode()
        assert '200.00' in response.content.decode()

    def test_other_user_order_access(
        self,
        test_user: User,
        client: Client
    ) -> None:
        """Test user cannot access other user's order.
        
        Args:
            test_user: Test user fixture
            client: Test client fixture
        """
        # Create another user and their order
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='other123'
        )
        order = Order.objects.create(
            user=other_user,
            delivery_address='123 Main Street',
            phone='+79001234567',
            total_price=Decimal('200.00')
        )

        # Try to access order as test_user
        client.force_login(test_user)
        response = client.get(reverse('order_detail', kwargs={'pk': order.id}))

        # Verify access denied
        assert response.status_code == 404

    def test_anonymous_user_redirect(self, client: Client) -> None:
        """Test anonymous user is redirected to login.
        
        Args:
            client: Test client fixture
        """
        response = client.get(reverse('order_detail', kwargs={'pk': 1}))
        assert response.status_code == 302
        assert 'login' in response.url
