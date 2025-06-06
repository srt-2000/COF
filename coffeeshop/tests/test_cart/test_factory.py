"""Tests for cart factory.

This module contains tests for the CartFactory class including:
- Tests for cart creation from request
- Integration tests with real dependencies
- Mock tests for factory functionality
"""
from __future__ import annotations

from typing import TypedDict
from unittest.mock import MagicMock, call, patch

import pytest
from cart.cart import Cart
from cart.factory import CartFactory
from cart.product_service import CartProductService
from cart.storage import SessionCartStorage
from django.http import HttpRequest


class TestCartFactory:
    """Tests for CartFactory class."""

    def test_create_from_request(
        self,
        mock_request: HttpRequest,
    ) -> None:
        """Test creating cart from request.

        Args:
            mock_request: Mocked HTTP request
        """
        with (
            patch("cart.factory.SessionCartStorage") as mock_storage_class,
            patch("cart.factory.CartProductService") as mock_product_service_class,
            patch("cart.factory.Cart") as mock_cart_class,
        ):
            mock_storage = MagicMock(spec=SessionCartStorage)
            mock_storage_class.return_value = mock_storage

            mock_product_service = MagicMock(spec=CartProductService)
            mock_product_service_class.return_value = mock_product_service

            mock_cart = MagicMock(spec=Cart)
            mock_cart_class.return_value = mock_cart

            result = CartFactory.create_from_request(mock_request)

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
    def test_create_from_request_with_different_sessions(
        self,
        session_data: dict[str, dict[str, dict[str, str | int]]],
    ) -> None:
        """Test creating cart with different session data.

        Args:
            session_data: Session data to test with
        """
        with (
            patch("cart.factory.SessionCartStorage") as mock_storage_class,
            patch("cart.factory.CartProductService") as mock_product_service_class,
            patch("cart.factory.Cart") as mock_cart_class,
        ):
            mock_storage = MagicMock(spec=SessionCartStorage)
            mock_storage_class.return_value = mock_storage

            mock_product_service = MagicMock(spec=CartProductService)
            mock_product_service_class.return_value = mock_product_service

            mock_cart = MagicMock(spec=Cart)
            mock_cart_class.return_value = mock_cart

            request = HttpRequest()
            request.session = session_data

            result = CartFactory.create_from_request(request)

            mock_storage_class.assert_called_once_with(session_data)
            mock_product_service_class.assert_called_once()
            mock_cart_class.assert_called_once_with(mock_storage, mock_product_service)
            assert result == mock_cart


class TestCartFactoryIntegration:
    """Integration tests for CartFactory."""

    def test_create_from_request_integration(self, mock_request: HttpRequest) -> None:
        """Test creating cart with real dependencies.

        Args:
            mock_request: Mocked HTTP request
        """
        with (
            patch("cart.factory.SessionCartStorage", autospec=True) as mock_storage_class,
            patch("cart.factory.CartProductService", autospec=True) as mock_product_service_class,
            patch("cart.factory.Cart", autospec=True) as mock_cart_class,
        ):
            mock_storage = MagicMock(spec=SessionCartStorage)
            mock_storage_class.return_value = mock_storage

            mock_product_service = MagicMock(spec=CartProductService)
            mock_product_service_class.return_value = mock_product_service

            mock_cart = MagicMock(spec=Cart)
            mock_cart_class.return_value = mock_cart

            result = CartFactory.create_from_request(mock_request)

            mock_storage_class.assert_called_once_with(mock_request.session)
            mock_product_service_class.assert_called_once()
            mock_cart_class.assert_called_once_with(mock_storage, mock_product_service)
            assert result == mock_cart

    def test_create_from_request_with_real_storage(self, mock_request: HttpRequest) -> None:
        """Test creating cart with real storage.

        Args:
            mock_request: Mocked HTTP request
        """
        with (
            patch("cart.factory.CartProductService", autospec=True) as mock_product_service_class,
            patch("cart.factory.Cart", autospec=True) as mock_cart_class,
        ):
            mock_product_service = MagicMock(spec=CartProductService)
            mock_product_service_class.return_value = mock_product_service

            mock_cart = MagicMock(spec=Cart)
            mock_cart_class.return_value = mock_cart

            result = CartFactory.create_from_request(mock_request)

            mock_product_service_class.assert_called_once()
            mock_cart_class.assert_called_once()

            call_args = mock_cart_class.call_args
            assert isinstance(call_args[0][0], SessionCartStorage)
            assert call_args[0][0].session == mock_request.session
            assert call_args[0][1] == mock_product_service

            assert result == mock_cart


class TestCartFactoryMock:
    """Tests using mock objects."""

    def test_create_from_request_with_mock_dependencies(
        self,
        mock_request: HttpRequest,
    ) -> None:
        """Test creating cart with mocked dependencies.

        Args:
            mock_request: Mocked HTTP request
        """
        with (
            patch("cart.factory.SessionCartStorage") as mock_storage_class,
            patch("cart.factory.CartProductService") as mock_product_service_class,
            patch("cart.factory.Cart") as mock_cart_class,
        ):
            mock_storage = MagicMock(spec=SessionCartStorage)
            mock_storage_class.return_value = mock_storage

            mock_product_service = MagicMock(spec=CartProductService)
            mock_product_service_class.return_value = mock_product_service

            mock_cart = MagicMock(spec=Cart)
            mock_cart_class.return_value = mock_cart

            result = CartFactory.create_from_request(mock_request)

            mock_storage_class.assert_called_once_with(mock_request.session)
            mock_product_service_class.assert_called_once()
            mock_cart_class.assert_called_once_with(mock_storage, mock_product_service)
            assert result == mock_cart

    def test_create_from_request_with_mock_request(self) -> None:
        """Test creating cart with mocked request."""
        with (
            patch("cart.factory.SessionCartStorage") as mock_storage_class,
            patch("cart.factory.CartProductService") as mock_product_service_class,
            patch("cart.factory.Cart") as mock_cart_class,
        ):
            mock_storage = MagicMock(spec=SessionCartStorage)
            mock_storage_class.return_value = mock_storage

            mock_product_service = MagicMock(spec=CartProductService)
            mock_product_service_class.return_value = mock_product_service

            mock_cart = MagicMock(spec=Cart)
            mock_cart_class.return_value = mock_cart

            mock_request = MagicMock(spec=HttpRequest)
            mock_request.session = {}

            result = CartFactory.create_from_request(mock_request)

            mock_storage_class.assert_called_once_with(mock_request.session)
            mock_product_service_class.assert_called_once()
            mock_cart_class.assert_called_once_with(mock_storage, mock_product_service)
            assert result == mock_cart
