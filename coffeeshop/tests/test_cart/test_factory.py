"""
Tests for CartFactory class.

This module contains tests for the CartFactory class including:
- Creating cart instances from requests
- Integration with storage and product service
- Error handling and edge cases
"""

from __future__ import annotations



import pytest
from django.http import HttpRequest

from cart.factory import CartFactory
from cart.product_service import CartProductService
from cart.storage import SessionCartStorage
from cart.cart import Cart


class TestCartFactory:
    """Tests for CartFactory class."""

    def test_create_from_session(
        self,
        mock_request: HttpRequest,
        mocker,
    ) -> None:
        """Test creating cart from session.

        Args:
            mock_request: Mocked HTTP request
            mocker: Pytest mocker fixture
        """
        mock_storage_class = mocker.patch("cart.factory.SessionCartStorage")
        mock_product_service_class = mocker.patch("cart.factory.CartProductService")
        mock_cart_class = mocker.patch("cart.factory.Cart")
        
        mock_storage = mocker.Mock(spec=SessionCartStorage)
        mock_storage_class.return_value = mock_storage

        mock_product_service = mocker.Mock(spec=CartProductService)
        mock_product_service_class.return_value = mock_product_service

        mock_cart = mocker.Mock(spec=Cart)
        mock_cart_class.return_value = mock_cart

        result = CartFactory.create_from_session(mock_request.session)

        mock_storage_class.assert_called_once_with(mock_request.session)
        mock_product_service_class.assert_called_once()
        mock_cart_class.assert_called_once_with(mock_storage, mock_product_service)
        assert result == mock_cart

    @pytest.mark.parametrize(
        "session_data",
        [
            {},  # Empty session
            {"cart": {}},  # Empty cart
            {"cart": {"1": {"quantity": 2, "price": "100.00"}}},  # Cart with items
        ],
    )
    def test_create_from_session_with_different_sessions(
        self,
        session_data: dict[str, dict[str, dict[str, str | int]]],
        mocker,
    ) -> None:
        """Test creating cart with different session data.

        Args:
            session_data: Session data to test with
            mocker: Pytest mocker fixture
        """
        mock_storage_class = mocker.patch("cart.factory.SessionCartStorage")
        mock_product_service_class = mocker.patch("cart.factory.CartProductService")
        mock_cart_class = mocker.patch("cart.factory.Cart")
        
        mock_storage = mocker.Mock(spec=SessionCartStorage)
        mock_storage_class.return_value = mock_storage

        mock_product_service = mocker.Mock(spec=CartProductService)
        mock_product_service_class.return_value = mock_product_service

        mock_cart = mocker.Mock(spec=Cart)
        mock_cart_class.return_value = mock_cart

        session = session_data

        result = CartFactory.create_from_session(session)

        mock_storage_class.assert_called_once_with(session)
        mock_product_service_class.assert_called_once()
        mock_cart_class.assert_called_once_with(mock_storage, mock_product_service)
        assert result == mock_cart


class TestCartFactoryIntegration:
    """Integration tests for CartFactory."""

    def test_create_from_session_integration(self, mock_request: HttpRequest, mocker) -> None:
        """Test creating cart with real dependencies.

        Args:
            mock_request: Mocked HTTP request
            mocker: Pytest mocker fixture
        """
        mock_storage_class = mocker.patch("cart.factory.SessionCartStorage", autospec=True)
        mock_product_service_class = mocker.patch("cart.factory.CartProductService", autospec=True)
        mock_cart_class = mocker.patch("cart.factory.Cart", autospec=True)
        
        mock_storage = mocker.Mock(spec=SessionCartStorage)
        mock_storage_class.return_value = mock_storage

        mock_product_service = mocker.Mock(spec=CartProductService)
        mock_product_service_class.return_value = mock_product_service

        mock_cart = mocker.Mock(spec=Cart)
        mock_cart_class.return_value = mock_cart

        result = CartFactory.create_from_session(mock_request.session)

        mock_storage_class.assert_called_once_with(mock_request.session)
        mock_product_service_class.assert_called_once()
        mock_cart_class.assert_called_once_with(mock_storage, mock_product_service)
        assert result == mock_cart

    def test_create_from_session_with_real_storage(self, mock_request: HttpRequest, mocker) -> None:
        """Test creating cart with real storage implementation.

        Args:
            mock_request: Mocked HTTP request
            mocker: Pytest mocker fixture
        """
        mock_product_service_class = mocker.patch("cart.factory.CartProductService")
        mock_cart_class = mocker.patch("cart.factory.Cart")
        
        mock_product_service = mocker.Mock(spec=CartProductService)
        mock_product_service_class.return_value = mock_product_service

        mock_cart = mocker.Mock(spec=Cart)
        mock_cart_class.return_value = mock_cart

        result = CartFactory.create_from_session(mock_request.session)

        # Verify SessionCartStorage was created with session
        mock_product_service_class.assert_called_once()
        mock_cart_class.assert_called_once()
        assert result == mock_cart


class TestCartFactoryMock:
    """Tests for CartFactory with mocked dependencies."""

    def test_create_from_session_with_mock_dependencies(
        self,
        mock_request: HttpRequest,
        mocker,
    ) -> None:
        """Test creating cart with mocked dependencies.

        Args:
            mock_request: Mocked HTTP request
            mocker: Pytest mocker fixture
        """
        mock_storage_class = mocker.patch("cart.factory.SessionCartStorage")
        mock_product_service_class = mocker.patch("cart.factory.CartProductService")
        mock_cart_class = mocker.patch("cart.factory.Cart")
        
        mock_storage = mocker.Mock()
        mock_storage_class.return_value = mock_storage

        mock_product_service = mocker.Mock()
        mock_product_service_class.return_value = mock_product_service

        mock_cart = mocker.Mock()
        mock_cart_class.return_value = mock_cart

        result = CartFactory.create_from_session(mock_request.session)

        mock_storage_class.assert_called_once_with(mock_request.session)
        mock_product_service_class.assert_called_once()
        mock_cart_class.assert_called_once_with(mock_storage, mock_product_service)
        assert result == mock_cart

    def test_create_from_session_with_mock_request(self, mocker) -> None:
        """Test creating cart with mock request."""
        mock_request = mocker.Mock()
        mock_session = mocker.Mock()
        mock_request.session = mock_session

        mock_storage_class = mocker.patch("cart.factory.SessionCartStorage")
        mock_product_service_class = mocker.patch("cart.factory.CartProductService")
        mock_cart_class = mocker.patch("cart.factory.Cart")
        
        mock_storage = mocker.Mock()
        mock_storage_class.return_value = mock_storage

        mock_product_service = mocker.Mock()
        mock_product_service_class.return_value = mock_product_service

        mock_cart = mocker.Mock()
        mock_cart_class.return_value = mock_cart

        result = CartFactory.create_from_session(mock_session)

        mock_storage_class.assert_called_once_with(mock_session)
        mock_product_service_class.assert_called_once()
        mock_cart_class.assert_called_once_with(mock_storage, mock_product_service)
        assert result == mock_cart
