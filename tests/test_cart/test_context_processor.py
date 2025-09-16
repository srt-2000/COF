"""
Tests for cart context processor.
"""

from __future__ import annotations

import pytest
from cart.context_processor import cart
from cart.factory import CartFactory
from django.http import HttpRequest


class TestCartContextProcessor:
    """Tests for cart context processor."""

    def test_cart_context_processor(self, mock_request: HttpRequest, mock_cart_factory) -> None:
        """Test cart context processor returns correct data.

        Args:
            mock_request: Mocked HTTP request
            mock_cart_factory: Mocked cart factory
        """
        result = cart(mock_request)

        assert "cart" in result
        assert "total_price" in result
        assert callable(result["cart"])  # Check if it's a mock
        assert isinstance(result["total_price"], int | float) or callable(result["total_price"])  # Check if it's a mock
        mock_cart_factory.assert_called_once_with(mock_request.session)

    def test_cart_context_processor_with_real_request(self, mock_cart_factory) -> None:
        """Test cart context processor with real request.

        Args:
            mock_cart_factory: Mocked cart factory
        """
        request = HttpRequest()
        request.session = {}

        result = cart(request)

        assert "cart" in result
        assert "total_price" in result

    def test_cart_context_processor_integration(self, mock_request: HttpRequest, mocker) -> None:
        """Test cart context processor integration with CartFactory.

        Args:
            mock_request: Mocked HTTP request
            mocker: Pytest mocker fixture
        """
        mock_factory = mocker.patch("cart.context_processor.CartFactory")
        mock_cart = mocker.Mock()
        mock_factory.create_from_session.return_value = mock_cart

        result = cart(mock_request)

        mock_factory.create_from_session.assert_called_once_with(mock_request.session)
        assert result["cart"] == mock_cart

    def test_cart_context_processor_with_session(self, mock_cart_factory) -> None:
        """Test cart context processor with session data.

        Args:
            mock_cart_factory: Mocked cart factory
        """
        request = HttpRequest()
        request.session = {"applied_promo_id": 1}

        result = cart(request)

        assert "cart" in result
        assert "total_price" in result
