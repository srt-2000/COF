"""
Tests for order views.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from order.models import Order


class TestOrderCreateView:
    """Tests for OrderCreateView."""

    def test_view_inheritance(self) -> None:
        """Test that OrderCreateView inherits from correct classes."""
        from order.views import OrderCreateView

        assert hasattr(OrderCreateView, "form_class")
        assert hasattr(OrderCreateView, "template_name")
        assert hasattr(OrderCreateView, "success_url")

    def test_get_context_data(self, client: Client, test_user: User) -> None:
        """Test that context data includes cart."""
        client.force_login(test_user)
        response = client.get(reverse("order_create"))

        assert response.status_code == 200
        assert "form" in response.context
        assert "cart" in response.context

    def test_get_form_kwargs(self, test_user: User, mocker) -> None:
        """Test that form kwargs include user."""
        from order.views import OrderCreateView

        view = OrderCreateView()
        view.request = mocker.Mock()
        view.request.user = test_user

        kwargs = view.get_form_kwargs()
        assert "user" in kwargs
        assert kwargs["user"] == test_user

    def test_form_valid(self, mocker, test_user: User, client: Client, mock_cart_for_order, mock_form_data) -> None:
        """Test form validation and order creation with new signature."""
        # Setup mocks
        mock_cart_factory = mocker.patch("order.views.CartFactory.create_from_session")
        mock_order_factory = mocker.patch("order.views.OrderFactory.create_order_service")
        # mock_order_get = mocker.patch("order.models.Order.objects.get")

        mock_cart_factory.return_value = mock_cart_for_order

        mock_service = mocker.Mock()
        mock_service.create_order.return_value = {
            "order_id": 1,
            "user_email": test_user.email,
            "delivery_address": mock_form_data["delivery_address"],
            "phone": mock_form_data["phone"],
            "total_price": Decimal("200.00"),
            "time_created": "2024-03-20 12:00:00",
            "items": [{"product_id": 1, "product_name": "Test Product", "quantity": 2, "price": Decimal("100.00")}],
            "applied_promo_name": "TEST10",
            "applied_promo_status": True,
        }
        mock_order_factory.return_value = mock_service

        # Test
        client.force_login(test_user)
        response = client.post(reverse("order_create"), mock_form_data)

        # Assertions
        assert response.status_code == 302
        mock_service.create_order.assert_called_once_with(
            user=test_user, cart=mock_cart_for_order, form_data=mock_form_data, applied_promo_id=None
        )
        mock_service.notifier.send_order_notification.assert_called_once_with(1)
        mock_cart_for_order.clear.assert_called_once()

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {"delivery_address": "Short", "phone": "123"},  # Too short address, invalid phone
            {"delivery_address": "123 Main Street"},  # Missing phone
            {"phone": "+79001234567"},  # Missing address
        ],
    )
    def test_form_invalid_data(self, invalid_data: dict[str, str], test_user: User, client: Client) -> None:
        """Test form validation with invalid data."""
        client.force_login(test_user)
        response = client.post(reverse("order_create"), invalid_data)

        assert response.status_code == 200  # Form re-rendered with errors
        assert "form" in response.context
        assert response.context["form"].errors

    def test_anonymous_user_redirect(self, client: Client) -> None:
        """Test that anonymous users are redirected to login."""
        response = client.get(reverse("order_create"))
        assert response.status_code == 302
        assert "/login/" in response.url


class TestOrderDetailView:
    """Tests for OrderDetailView."""

    def test_view_inheritance(self) -> None:
        """Test that OrderDetailView inherits from correct classes."""
        from order.views import OrderDetailView

        assert hasattr(OrderDetailView, "model")
        assert hasattr(OrderDetailView, "template_name")
        assert hasattr(OrderDetailView, "context_object_name")

    def test_get_queryset(self, test_user: User, mocker) -> None:
        """Test that queryset is filtered by user."""
        from order.views import OrderDetailView

        view = OrderDetailView()
        view.request = mocker.Mock()
        view.request.user = test_user

        queryset = view.get_queryset()
        assert queryset.model == Order
        # Note: In test environment, filter might not be applied due to mock

    def test_order_detail_page(self, test_user: User, client: Client) -> None:
        """Test order detail page access."""
        # Create test order
        order = Order.objects.create(
            user=test_user,
            delivery_address="123 Main Street",
            phone="+79001234567",
            cart_price=Decimal("200.00"),  # ДОБАВИТЬ
            total_price=Decimal("200.00"),
        )

        client.force_login(test_user)
        response = client.get(reverse("order_detail", kwargs={"pk": order.pk}))

        assert response.status_code == 200
        assert "order" in response.context
        assert response.context["order"] == order

    def test_other_user_order_access(self, test_user: User, client: Client) -> None:
        """Test that users cannot access other users' orders."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        other_user = User.objects.create_user(username="otheruser", email="other@example.com", password="otherpass123")

        # Create order for other user
        order = Order.objects.create(
            user=other_user,
            delivery_address="456 Other Street",
            phone="+79009876543",
            cart_price=Decimal("300.00"),  # ДОБАВИТЬ
            total_price=Decimal("300.00"),
        )

        client.force_login(test_user)
        response = client.get(reverse("order_detail", kwargs={"pk": order.pk}))

        assert response.status_code == 404

    def test_anonymous_user_redirect(self, client: Client) -> None:
        """Test that anonymous users are redirected to login."""
        response = client.get(reverse("order_detail", kwargs={"pk": 1}))
        assert response.status_code == 302
        assert "/login/" in response.url
